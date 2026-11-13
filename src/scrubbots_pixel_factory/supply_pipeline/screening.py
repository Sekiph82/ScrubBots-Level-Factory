"""ScreeningSimulator: fast Python mirror of the ScrubBots ProofKernel, for RANKING only.

Never an acceptance authority: every supply this pipeline outputs is accepted only after
the game's own SolvabilitySolver (Godot bridge) proves SOLVED and its replay reaches WIN.
Mirrored rules (from the game source, see godot/solver_bridge.gd for the real thing):
  - placement: a column FRONT batch goes to the rightmost EMPTY slot; none empty -> illegal;
  - wave kernel: every occupied slot (ascending placement sequence) claims at most one
    reachable, unreserved ACTIVE cell of its color per wave, all against the pre-wave board;
    the wave's clears then apply; repeat until a wave claims nothing (quiescence);
  - TargetSelector WHAT-order: bottom-most, then left-most (key (h-1-y)*w + x);
  - reachability: a target is reachable when it touches outside-board space or an OPEN cell
    (cleared / transparent) 4-connected to the outside (railroad is lane-robust);
  - a batch frees its slot when its last robot's clear lands;
  - SOLVED = board clear, slots empty, supply exhausted.
"""
from bisect import bisect_left, insort

import numpy as np


class ScreeningSimulator:
    """State arrays are bytearrays; per colour the reachable ACTIVE cells are kept as a
    sorted list of TargetSelector ranks, updated as cells clear and open (2026-11-13:
    the old per-lane numpy scan of every cell of a colour was 93% of screening time)."""

    def __init__(self, grid, slot_count=5):
        """grid: (h, w) int array of local color index, -1 = transparent (starts open)."""
        g = np.asarray(grid, dtype=np.int16)
        self.h, self.w = g.shape
        self.n = g.size
        self.color = g.ravel().copy()
        self.slot_count = slot_count
        w, h = self.w, self.h
        ys, xs = np.divmod(np.arange(self.n), w)
        key = (h - 1 - ys) * w + xs
        self.ncolors = int(self.color.max()) + 1 if (self.color >= 0).any() else 0
        # per color: cell indices in TargetSelector priority order
        self.by_color = [np.flatnonzero(self.color == c)[np.argsort(key[self.color == c], kind="stable")]
                         for c in range(self.ncolors)]
        self.cells_of = [[int(cell) for cell in cells] for cells in self.by_color]
        self.colors = [int(c) for c in self.color]
        self.rank = [0] * self.n
        for cells in self.cells_of:
            for r, cell in enumerate(cells):
                self.rank[cell] = r
        self.nbrs = []
        for i in range(self.n):
            y, x = divmod(i, w)
            self.nbrs.append([j for j, ok in ((i - w, y > 0), (i + w, y < h - 1), (i - 1, x > 0), (i + 1, x < w - 1)) if ok])
        self.border = np.zeros(self.n, bool)
        self.border.reshape(h, w)[[0, -1], :] = True
        self.border.reshape(h, w)[:, [0, -1]] = True

    # ------------------------------------------------------------------ state --
    def initial(self, columns):
        """columns: 3 lists of (color, count). Returns a quiescent state dict."""
        active = bytearray(1 if c >= 0 else 0 for c in self.colors)
        opened = bytearray(self.n)
        reach = bytearray(self.n)
        elig = [[] for _ in range(self.ncolors)]
        for i in np.flatnonzero((self.color >= 0) & self.border):
            i = int(i)
            reach[i] = 1
            insort(elig[self.colors[i]], self.rank[i])
        for i in np.flatnonzero((self.color < 0) & self.border):  # transparent edge -> open region
            if not opened[i]:
                self._open(active, opened, reach, int(i), elig)
        st = {"active": active, "open": opened, "reach": reach, "elig": elig, "ptr": [0] * len(columns),
              "slots": [None] * self.slot_count, "seq": 1, "cols": columns, "left": sum(active)}
        self.quiesce(st)
        return st

    def copy(self, st):
        return {"active": st["active"][:], "open": st["open"][:], "reach": st["reach"][:],
                "elig": [lst[:] for lst in st["elig"]],
                "ptr": list(st["ptr"]), "slots": list(st["slots"]), "seq": st["seq"], "cols": st["cols"],
                "left": st["left"]}

    def key(self, st):
        occ = sorted((s[2], i) for i, s in enumerate(st["slots"]) if s)
        rank = {seq: r for r, (seq, _) in enumerate(occ)}
        slots = tuple(None if s is None else (s[0], s[1], rank[s[2]]) for s in st["slots"])
        return bytes(st["active"]), tuple(st["ptr"]), slots

    def _open(self, active, opened, reach, start, elig=None):
        nbrs, colors, rank = self.nbrs, self.colors, self.rank
        opened[start] = 1
        stack = [start]
        while stack:
            c = stack.pop()
            for nb in nbrs[c]:
                if active[nb]:
                    if not reach[nb]:
                        reach[nb] = 1
                        if elig is not None:
                            insort(elig[colors[nb]], rank[nb])
                elif not opened[nb]:
                    opened[nb] = 1
                    stack.append(nb)

    # ---------------------------------------------------------------- kernel ---
    def legal(self, st):
        if None not in st["slots"]:
            return []
        return [c for c in range(len(st["cols"])) if st["ptr"][c] < len(st["cols"][c])]

    def place(self, st, col):
        """Mutates st: front of `col` -> rightmost empty slot, then quiesce. Returns clears."""
        color, count = st["cols"][col][st["ptr"][col]]
        st["ptr"][col] += 1
        slot = max(i for i, s in enumerate(st["slots"]) if s is None)
        st["slots"][slot] = (color, count, st["seq"])
        st["seq"] += 1
        return self.quiesce(st)

    def quiesce(self, st):
        active, reach, opened, elig, slots = st["active"], st["reach"], st["open"], st["elig"], st["slots"]
        cells_of, colors, rank = self.cells_of, self.colors, self.rank
        clears = 0
        while True:
            lanes = sorted((s[2], i) for i, s in enumerate(slots) if s and s[1] > 0)
            claims = []
            taken = {}
            for _, i in lanes:
                c = slots[i][0]
                k = taken.get(c, 0)
                if k < len(elig[c]):
                    claims.append((i, cells_of[c][elig[c][k]]))
                    taken[c] = k + 1
            if not claims:
                return clears
            for i, cell in claims:
                active[cell] = 0
                reach[cell] = 0
                lst = elig[colors[cell]]
                del lst[bisect_left(lst, rank[cell])]
                self._open(active, opened, reach, cell, elig)
                color, rem, seq = slots[i]
                slots[i] = (color, rem - 1, seq) if rem > 1 else None
            clears += len(claims)
            st["left"] -= len(claims)

    def solved(self, st):
        return st["left"] == 0 and all(s is None for s in st["slots"]) and \
            all(p == len(c) for p, c in zip(st["ptr"], st["cols"]))

    # ---------------------------------------------------------------- search ---
    def solve(self, columns=None, state=None, max_visited=3000):
        """Deterministic DFS, ascending column order, memoized (like SolvabilitySolver).
        Returns {status: SOLVED|DEADLOCK|BOUND, visited, trace:[{column, clears, active_after}]}."""
        root = state if state is not None else self.initial(columns)
        seen = set()
        stack = [(root, [])]
        while stack:
            st, trace = stack.pop()
            k = self.key(st)
            if k in seen:
                continue
            seen.add(k)
            if self.solved(st):
                return {"status": "SOLVED", "visited": len(seen), "trace": trace}
            if len(seen) >= max_visited:
                return {"status": "BOUND", "visited": len(seen), "trace": []}
            children = []
            for c in self.legal(st):
                ch = self.copy(st)
                clears = self.place(ch, c)
                children.append((ch, trace + [{"column": c, "clears": clears, "active_after": ch["left"]}]))
            stack.extend(reversed(children))
        return {"status": "DEADLOCK", "visited": len(seen), "trace": []}

    def replay(self, columns, trace):
        """Replay a column trace; returns (ok, per-step records with decision-state info)."""
        st = self.initial(columns)
        steps = []
        for i, a in enumerate(trace):
            legal = self.legal(st)
            if a["column"] not in legal:
                return False, steps
            occ = sum(s is not None for s in st["slots"])
            clears = self.place(st, a["column"])
            rec = {"legal": legal, "occupied_before": occ, "clears": clears, "active_after": st["left"]}
            if ("clears" in a and a["clears"] != clears) or ("active_after" in a and a["active_after"] != st["left"]):
                rec["diverged"] = True
                steps.append(rec)
                return False, steps
            steps.append(rec)
        return self.solved(st), steps

    # ------------------------------------------------------------------ peel ---
    def peel_waves(self):
        """Colour-agnostic accessibility layers: wave index at which each cell first becomes
        reachable if every reachable cell were cleared each wave (-1 for transparent)."""
        active = (self.color >= 0).astype(np.uint8)
        opened = np.zeros(self.n, np.uint8)
        reach = (active.astype(bool) & self.border).astype(np.uint8)
        for i in np.flatnonzero((active == 0) & self.border):
            if not opened[i]:
                self._open(active, opened, reach, int(i))
        wave = np.full(self.n, -1, np.int32)
        t = 0
        while active.any():
            now = np.flatnonzero(active & reach)
            if len(now) == 0:
                break
            wave[now] = t
            for c in now:
                active[c] = 0
            for c in now:
                reach[c] = 0
                self._open(active, opened, reach, int(c))
            t += 1
        return wave


