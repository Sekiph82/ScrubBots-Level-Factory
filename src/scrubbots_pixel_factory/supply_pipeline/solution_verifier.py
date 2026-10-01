"""SolutionVerifier: hard invariants on an accepted supply. Any violation = hard failure."""


class SolutionVerifier:
    def verify(self, counts, playable, columns, real):
        """counts: {local color: exact image count}; columns: 3 lists of (color, count);
        real: bridge result for this candidate (SolvabilitySolver + replay)."""
        flat = [b for col in columns for b in col]
        per = {}
        for c, n in flat:
            per[c] = per.get(c, 0) + n
        col_tot = [sum(n for _, n in col) for col in columns]
        trace = real.get("trace", [])
        rp = real.get("replay", {})
        # the trace must consume every batch exactly in each column's FIFO order
        ptr = [0] * len(columns)
        fifo_ok = True
        for a in trace:
            c = a["column"]
            if ptr[c] >= len(columns[c]) or tuple(columns[c][ptr[c]]) != (a["color"], a["count"]):
                fifo_ok = False
                break
            ptr[c] += 1
        checks = {
            "histogram_sums_to_playable": sum(counts.values()) == playable,
            "per_color_supply_equals_image": per == counts,
            "no_missing_or_extra_color": set(per) == set(counts),
            "all_batches_sum_to_playable": sum(n for _, n in flat) == playable,
            "columns_sum_to_playable": sum(col_tot) == playable,
            "every_batch_positive": all(n >= 1 for _, n in flat),
            "three_nonempty_columns": len(columns) == 3 and all(columns),
            "solver_status_SOLVED": real.get("status") == "SOLVED",
            "replay_ok": bool(rp.get("ok")),
            "replay_reaches_WIN": bool(rp.get("solved")),
            "replay_remaining_pixels_zero": rp.get("finalActive") == 0,
            "trace_consumes_all_supply_in_FIFO_order": fifo_ok and ptr == [len(c) for c in columns],
        }
        return {"all_ok": all(checks.values()), "checks": checks, "column_pixel_totals": col_tot}


