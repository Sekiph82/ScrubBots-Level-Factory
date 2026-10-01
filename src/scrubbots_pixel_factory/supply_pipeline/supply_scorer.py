"""SupplyScorer: gameplay metrics along a solution path + gameplay-quality score.

Metrics are measured with the ScreeningSimulator (verified step-exact against the real
kernel on the same trace; divergence is reported, never hidden). Alternative choices at each
decision are probed with a bounded search: SOLVED -> viable, DEADLOCK -> dead end,
BOUND -> unknown (never counted as dead).
Target ranges per class are tuning seeds.
"""
TARGETS = {  # (low, high) seeds
    "EASY":      {"dead": (0.00, 0.12), "forced": (0.10, 0.35), "slot": (0.20, 0.50)},
    "MEDIUM":    {"dead": (0.08, 0.25), "forced": (0.20, 0.45), "slot": (0.30, 0.60)},
    "HARD":      {"dead": (0.18, 0.38), "forced": (0.30, 0.55), "slot": (0.40, 0.70)},
    "VERY_HARD": {"dead": (0.28, 0.50), "forced": (0.35, 0.65), "slot": (0.50, 0.80)},
}


def _band(v, lo, hi, width=0.25):
    if lo <= v <= hi:
        return 1.0
    d = lo - v if v < lo else v - hi
    return max(0.0, 1.0 - d / width)


class SupplyScorer:
    def __init__(self, sim, slot_count, viability_budget=3000, max_probes=60):
        self.sim = sim
        self.slots = slot_count
        self.budget = viability_budget
        self.max_probes = max_probes  # alternatives are probed at <= this many evenly spaced decisions

    def metrics(self, columns, trace):
        sim = self.sim
        st = sim.initial(columns)
        rows = []
        prev = None
        n_steps = len(trace)
        step = max(1, -(-n_steps // self.max_probes))
        for t, a in enumerate(trace):
            legal = sim.legal(st)
            occ = sum(s is not None for s in st["slots"])
            probed = t % step == 0
            viable = dead = unknown = 0
            for c in (legal if probed else []):
                if c == a["column"]:
                    viable += 1
                    continue
                ch = sim.copy(st)
                sim.place(ch, c)
                # proving SOLVED needs >= remaining decisions states: budget scales with them
                r = sim.solve(state=ch, max_visited=min(self.budget, 2 * (n_steps - t) + 50))
                viable += r["status"] == "SOLVED"
                dead += r["status"] == "DEADLOCK"
                unknown += r["status"] == "BOUND"
            color = columns[a["column"]][st["ptr"][a["column"]]][0]
            clears = sim.place(st, a["column"])
            rows.append({"probed": probed, "legal": len(legal), "viable": viable, "dead": dead, "unknown": unknown,
                         "occupied_after": sum(s is not None for s in st["slots"]), "occupied_before": occ,
                         "clears": clears, "switch": prev is not None and color != prev,
                         "diverged": "clears" in a and a["clears"] != clears})
            prev = color
        n = max(len(rows), 1)
        q1, q3 = n // 4, (3 * n) // 4
        avg = lambda xs, f: sum(f(r) for r in xs) / max(len(xs), 1)
        P = [r for r in rows if r["probed"]]  # viability metrics come from probed decisions only
        Pq = lambda a, b: [r for r in rows[a:b] if r["probed"]]
        streak = best = 0
        for r in P:
            streak = streak + 1 if r["viable"] <= 1 and not r["unknown"] else 0
            best = max(best, streak)
        best *= step  # in decisions (estimate when sampled)
        adj = sum(1 for col in columns for x, y in zip(col, col[1:]) if x[0] == y[0])
        m = {
            "solution_length": len(rows),
            "decision_states": len(rows),
            "avg_legal_choices": avg(rows, lambda r: r["legal"]),
            "probed_decisions": len(P), "probe_budget_cap": self.budget,
            "avg_viable_choices": avg(P, lambda r: r["viable"]),
            "meaningful_decisions": round(avg(P, lambda r: r["viable"] >= 2) * len(rows)),
            "forced_move_ratio": avg(P, lambda r: r["viable"] <= 1 and not r["unknown"]),
            "dead_end_branch_ratio": sum(r["dead"] for r in P) / max(sum(r["legal"] for r in P), 1),
            "unknown_branches": sum(r["unknown"] for r in P),
            "slot_pressure_mean": avg(rows, lambda r: r["occupied_after"] / self.slots),
            "slot_pressure_max": max((r["occupied_after"] for r in rows), default=0),
            "slot_pressure_frequency": avg(rows, lambda r: r["occupied_after"] >= self.slots - 1),
            "color_switch_frequency": avg(rows[1:], lambda r: r["switch"]),
            "same_color_adjacent_in_columns": adj,
            "early_game_freedom": avg(Pq(0, q1), lambda r: r["viable"]),
            "mid_game_pressure": avg(rows[q1:q3], lambda r: r["occupied_after"] / self.slots),
            "late_game_forced_ratio": avg(Pq(q3, n), lambda r: r["viable"] <= 1 and not r["unknown"]),
            "longest_forced_streak": best,
            "bottlenecks": step * sum(r["viable"] == 1 and not r["unknown"] and r["occupied_after"] >= self.slots - 1 for r in P),
            "productive_placement_ratio": avg(rows, lambda r: r["clears"] > 0),
            "screening_diverged_steps": sum(r["diverged"] for r in rows),
        }
        m["pressure_index"] = round(100 * min(1.0, 0.35 * m["dead_end_branch_ratio"] / 0.5
                                              + 0.30 * m["forced_move_ratio"] + 0.35 * m["slot_pressure_mean"]), 2)
        return m

    def score(self, m, band):
        t = TARGETS[band]
        early_pressure = m["slot_pressure_mean"]  # overall
        parts = {
            "dead_end_fit": 2.0 * _band(m["dead_end_branch_ratio"], *t["dead"]),
            "forced_fit": 1.5 * _band(m["forced_move_ratio"], *t["forced"]),
            "slot_fit": 1.5 * _band(m["slot_pressure_mean"], *t["slot"]),
            "open_start": 1.0 * min(1.0, m["early_game_freedom"] / 2.0),
            "mid_pressure_rise": 1.0 * (m["mid_game_pressure"] >= 0.9 * early_pressure),
            "controlled_cleanup": 1.0 * (1.0 - min(1.0, max(0.0, m["late_game_forced_ratio"] - 0.6) / 0.4)),
            "no_long_forced_runs": 1.0 * (1.0 - min(1.0, max(0, m["longest_forced_streak"] - 5) / 10)),
            "few_bottlenecks": 1.0 * (1.0 - min(1.0, m["bottlenecks"] / max(3, m["solution_length"] / 8))),
            "color_switching": 0.75 * _band(m["color_switch_frequency"], 0.5, 0.9),
            "column_spacing": 0.75 * (1.0 - min(1.0, m["same_color_adjacent_in_columns"] / max(1, m["solution_length"] / 6))),
            "meaningful": 1.0 * min(1.0, m["meaningful_decisions"] / max(1, 0.4 * m["solution_length"])),
        }
        return round(sum(parts.values()), 4), parts


