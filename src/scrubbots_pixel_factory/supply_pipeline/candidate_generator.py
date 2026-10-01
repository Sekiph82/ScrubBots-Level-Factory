"""SupplyCandidateGenerator: planned batches -> 3 ordered FIFO columns (+ mutations)."""


class SupplyCandidateGenerator:
    def __init__(self, column_count, rng):
        self.k = column_count
        self.rng = rng

    def generate(self, plan, access, first, safety=1.0):
        """plan: {color: [sizes]}; access/first: {color: 0..1} median/first accessibility layer.
        safety > 1 releases deep (enclosed) colours later -> fewer waiting slots."""
        rng = self.rng
        items = []
        for c, sizes in plan.items():
            k = len(sizes)
            start = min(0.85, (0.5 * first[c] + 0.4 * access[c]) * safety)
            for j, s in enumerate(sizes):
                t = start + (1 - start) * (j + rng.uniform(0.15, 0.85)) / k + rng.gauss(0, 0.05)
                items.append((t, c, s))
        items.sort()
        total = sum(s for _, _, s in items)
        cols = [[] for _ in range(self.k)]
        pix = [0] * self.k
        for n, (_, c, s) in enumerate(items):
            if n < self.k:  # every column non-empty, different openers
                cols[n].append((c, s))
                pix[n] += s
                continue
            def cost(i):
                row = len(cols[i])
                same_row = sum(1 for j in range(self.k) if j != i and len(cols[j]) > row and cols[j][row][0] == c)
                return (1.0 * (pix[i] + s) / (total / self.k) + 0.6 * len(cols[i]) / (len(items) / self.k)
                        + 1.5 * (cols[i][-1][0] == c) + 0.8 * same_row + rng.uniform(0, 0.6))
            i = min(range(self.k), key=cost)
            cols[i].append((c, s))
            pix[i] += s
        return cols

    def mutate(self, cols):
        """Conservation-preserving local change: swap/move batches (columns stay non-empty)."""
        rng = self.rng
        cols = [list(c) for c in cols]
        op = rng.random()
        a = rng.randrange(self.k)
        if op < 0.4 and len(cols[a]) > 1:  # swap neighbours inside a column
            i = rng.randrange(len(cols[a]) - 1)
            cols[a][i], cols[a][i + 1] = cols[a][i + 1], cols[a][i]
        elif op < 0.75:  # swap across columns at a similar depth
            b = (a + rng.randrange(1, self.k)) % self.k
            i = rng.randrange(len(cols[a]))
            j = min(len(cols[b]) - 1, max(0, i + rng.randint(-1, 1)))
            cols[a][i], cols[b][j] = cols[b][j], cols[a][i]
        elif len(cols[a]) > 1:  # move a batch later in its column
            i = rng.randrange(len(cols[a]) - 1)
            x = cols[a].pop(i)
            cols[a].insert(min(len(cols[a]), i + rng.randint(1, 3)), x)
        return cols


