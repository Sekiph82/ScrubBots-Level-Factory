"""BatchPlanner: exact colour counts -> variable-size batches (conservation-exact)."""
import math


class BatchPlanner:
    def __init__(self, max_per_batch, rng):
        self.cap = max_per_batch or 10 ** 9  # None = no cap (owner decision); else the chosen limit
        self.rng = rng

    def batch_counts(self, counts, components, total_batches, mean):
        """counts/components: {color: int}. Fragmented colours get more appearances."""
        want = {}
        for c, p in counts.items():
            frag = min(1.0, (components[c] - 1) / max(1.0, p / 8.0))
            want[c] = p / mean * (1.0 + 0.5 * frag)
        scale = total_batches / max(sum(want.values()), 1e-9)
        # keep each colour's average batch within [0.5, 1.6] x mean and <= 75% of the cap, so
        # sizes always have room to vary (no all-3s / all-at-cap runs)
        size_hi = min(1.6 * mean, 0.75 * self.cap)
        size_lo = 0.5 * mean
        out = {}
        for c, p in counts.items():
            lo = math.ceil(p / size_hi)
            hi = max(lo, math.floor(p / size_lo))
            out[c] = max(lo, min(hi, round(want[c] * scale * self.rng.uniform(0.85, 1.15))))
        return out

    def split(self, total, k, mean):
        """total into k positive parts, varied (no uniform runs), each <= cap."""
        if k <= 1:
            return [total]
        cap = min(self.cap, total)
        floor = min(total // k, max(3, round(mean * 0.35)))
        if floor * k > total or cap * k < total:  # infeasible bounds (never with planner k)
            base, rem = divmod(total, k)
            return self._rhythm([base + (i < rem) for i in range(k)])
        wts = [self.rng.uniform(0.45, 1.65) for _ in range(k)]
        raw = [total * x / sum(wts) for x in wts]
        parts = [min(cap, max(floor, int(r))) for r in raw]
        diff = total - sum(parts)
        order = sorted(range(k), key=lambda i: raw[i] - int(raw[i]), reverse=diff > 0)
        while diff:  # each sweep moves >= 1 unit: bounds are feasible
            for j in order:
                if diff > 0 and parts[j] < cap:
                    parts[j] += 1
                    diff -= 1
                elif diff < 0 and parts[j] > floor:
                    parts[j] -= 1
                    diff += 1
                if not diff:
                    break
        return self._rhythm(parts)

    def _rhythm(self, parts):
        """Alternate larger/smaller sizes so a colour's appearances never form a flat run."""
        s = sorted(parts)
        out = []
        while s:
            out.append(s.pop() if (len(out) % 2 == 0) == (self.rng.random() < 0.8) else s.pop(0))
        return out

    def plan(self, counts, components, total_batches, mean):
        k = self.batch_counts(counts, components, total_batches, mean)
        plan = {c: self.split(counts[c], k[c], mean) for c in counts}
        for c in counts:  # hard invariant
            assert sum(plan[c]) == counts[c] and min(plan[c]) >= 1 and max(plan[c]) <= self.cap, (c, plan[c])
        return plan


