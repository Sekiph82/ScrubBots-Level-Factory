from pathlib import Path

ROOT = Path(r"C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator")
p = ROOT / "src/scrubbots_pixel_factory/supply_pipeline/supply_optimizer.py"
s = p.read_text(encoding="utf-8")

anchor = "class _AlreadyProven(Exception):"
helpers = '''# Owner idea 2026-11-23: a plan the game loses by a slot jam is repaired, not dropped.
# Experiment on the 21 REAL_PLAY_NO_WINNING_PLAN levels: 16 won after this repair.
MAX_SLOT_JAM_REPAIR_ROUNDS = 6


def _repair_slot_jam(columns, clicks, slots):
    """At a real-play jam every WAITING slot batch keeps the robots it used; the rest
    become a new batch at the end of the same column, clicked last. Robot totals per
    colour are unchanged. Returns (columns, clicks) or None when nothing can shrink.

    Batch ids are ``<level>-K<column>-<row>`` exactly as SupplyExporter numbers them.
    """
    import re

    new = [list(column) for column in columns]
    new_clicks = list(clicks)
    changed = False
    for slot in slots or ():
        if not (isinstance(slot, dict) and slot.get("occupied") and slot.get("state") == "WAITING"):
            continue
        remaining = int(slot.get("remaining") or 0)
        match = re.search(r"-K(\\d+)-(\\d+)$", str(slot.get("batchId", "")))
        if remaining <= 0 or match is None:
            continue
        ci, ri = int(match.group(1)) - 1, int(match.group(2)) - 1
        if not (0 <= ci < len(new) and 0 <= ri < len(new[ci])):
            continue
        color, count = new[ci][ri]
        used = count - remaining
        keep = used if used > 0 else max(1, count // 2)
        moved = count - keep
        if moved <= 0:
            continue
        new[ci][ri] = (color, keep)
        new[ci].append((color, moved))
        new_clicks.append(ci + 1)
        changed = True
    return (new, new_clicks) if changed else None


def _trace_for_clicks(sim, columns, clicks):
    """Kernel-equivalent screening trace of one exact click order (1-based columns),
    or None when a click is illegal or the board is not cleared."""
    state = sim.initial(columns)
    trace = []
    for click in clicks:
        column = int(click) - 1
        if column not in sim.legal(state):
            return None
        clears = sim.place(state, column)
        trace.append({"column": column, "clears": clears, "active_after": state["left"]})
    return trace if sim.solved(state) else None


'''
assert s.count(anchor) == 1
s = s.replace(anchor, helpers + anchor, 1)

old = '''                    verdict = real_play_precheck(level, shape["supply_columns"], shape["solution_trace"])
                    real_play_prechecks.append({"id": candidate["id"], **verdict})
                    if not verdict.get("won"):
                        log(f"real-play pre-check {candidate['id']}: {verdict.get('verdict')} at click {verdict.get('stuck_click')}")
                        continue
'''
new = '''                    verdict = real_play_precheck(level, shape["supply_columns"], shape["solution_trace"])
                    real_play_prechecks.append({"id": candidate["id"], **verdict})
                    if not verdict.get("won"):
                        log(f"real-play pre-check {candidate['id']}: {verdict.get('verdict')} at click {verdict.get('stuck_click')}")
                        repaired = self._repair_jammed_plan(
                            level, candidate, record, verdict, sim, solver, bounded(call_options), counts, m,
                            color_id, real_play_precheck, real_play_prechecks, log)
                        if repaired is None:
                            continue
                        candidate, record, verification = repaired
'''
assert s.count(old) == 1
s = s.replace(old, new, 1)

anchor2 = "    def prepare_grid(self, grid, used):"
method = '''    def _repair_jammed_plan(self, level, candidate, record, verdict, sim, solver, options, counts, m,
                            color_id, real_play_precheck, prechecks, log):
        """Repair a real-play slot jam (owner 2026-11-23) and prove the repaired plan the same
        way as any plan: kernel replay of its exact order, verifier, real-play pre-check.
        Returns (candidate, record, verification) of a won plan, else None."""
        columns = [list(column) for column in candidate["columns"]]
        clicks = [int(action["column"]) + 1 for action in record["trace"]]
        for round_index in range(1, MAX_SLOT_JAM_REPAIR_ROUNDS + 1):
            if options is None or verdict.get("won") or verdict.get("verdict") != "LOST":
                return None
            repaired = _repair_slot_jam(columns, clicks, verdict.get("slots"))
            if repaired is None:
                return None
            columns, clicks = repaired
            trace = _trace_for_clicks(sim, columns, clicks)
            repair_id = f"{candidate['id']}-jam{round_index}"
            if trace is None:
                log(f"slot-jam repair {repair_id}: repaired order does not clear the board")
                return None
            try:
                response = solver.run(
                    level,
                    [{"id": repair_id, "columns": [[{"color": c, "count": n} for c, n in column] for column in columns],
                      "verify_trace": trace}],
                    **{**options, "analyze": False},
                )
            except SolverBridgeError as exc:
                if (getattr(exc, "telemetry", {}) or {}).get("cancelled"):
                    raise
                log(f"slot-jam repair {repair_id}: solver error {str(exc).splitlines()[0][:120]}")
                return None
            new_record = (response.get("results") or [{}])[0]
            if new_record.get("status") != "SOLVED":
                log(f"slot-jam repair {repair_id}: kernel replay {new_record.get('status', 'UNAVAILABLE')}")
                return None
            repaired_candidate = {**candidate, "id": repair_id, "columns": columns, "screen": {"trace": trace}}
            verification = self.verifier.verify(counts, m["playable_pixels"], columns, new_record, self.column_count)
            if not verification["all_ok"]:
                log(f"slot-jam repair {repair_id}: verification failed")
                return None
            shape = _export_shape(repaired_candidate, new_record, color_id)
            verdict = real_play_precheck(level, shape["supply_columns"], shape["solution_trace"])
            prechecks.append({"id": repair_id, **verdict})
            if verdict.get("won"):
                log(f"slot-jam repair {repair_id}: WON_CANONICAL after {round_index} round(s)")
                return repaired_candidate, new_record, verification
            log(f"slot-jam repair {repair_id}: {verdict.get('verdict')} at click {verdict.get('stuck_click')}")
        return None

'''
assert s.count(anchor2) == 1
s = s.replace(anchor2, method + anchor2, 1)
p.write_text(s, encoding="utf-8")

e = ROOT / "src/scrubbots_pixel_factory/studio_extensions.py"
t = e.read_text(encoding="utf-8")
old3 = '''                    "clicks": per_dt.get("clicksPlaced"), "result_path": _relative(Path(gate["result_path"]))}'''
new3 = '''                    "clicks": per_dt.get("clicksPlaced"), "slots": per_dt.get("slots"),
                    "result_path": _relative(Path(gate["result_path"]))}'''
assert t.count(old3) == 1
e.write_text(t.replace(old3, new3, 1), encoding="utf-8")
print("applied")
