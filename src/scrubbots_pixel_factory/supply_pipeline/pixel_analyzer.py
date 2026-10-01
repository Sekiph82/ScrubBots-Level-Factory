"""PixelAnalyzer: indexed-colour image -> exact histogram + structural complexity metrics."""
import math
from collections import Counter

import numpy as np
from PIL import Image

from .screening import ScreeningSimulator


class PixelAnalyzer:
    def __init__(self, palette):
        """palette: [(cid, '#RRGGBB'), ...] global game palette (GameRules.palette)."""
        self.palette = palette
        self.rgb_to_global = {tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)): gi for gi, (_, h) in enumerate(palette)}

    def load(self, image):
        """PIL image / path -> (local grid with -1 transparent, used global indices ascending).
        Fails on any opaque off-palette pixel (no silent quantization)."""
        img = Image.open(image) if not isinstance(image, Image.Image) else image
        a = np.asarray(img.convert("RGBA"))
        h, w = a.shape[:2]
        glob = np.full((h, w), -1, np.int16)
        bad = []
        for y in range(h):
            for x in range(w):
                r, g, b, al = (int(v) for v in a[y, x])
                if al < 128:
                    continue
                gi = self.rgb_to_global.get((r, g, b))
                if gi is None:
                    bad.append((x, y, (r, g, b)))
                else:
                    glob[y, x] = gi
        if bad:
            raise ValueError(f"{len(bad)} opaque pixels are not palette colours, e.g. {bad[:3]}")
        used = sorted(int(v) for v in np.unique(glob) if v >= 0)  # ascending global C-ID
        local = np.full((h, w), -1, np.int16)
        for li, gi in enumerate(used):
            local[glob == gi] = li
        return local, used

    def analyze(self, grid, used):
        g = np.asarray(grid)
        h, w = g.shape
        flat = g.ravel()
        play = flat >= 0
        n = int(play.sum())
        if n == 0:
            raise ValueError("image has no playable pixels")
        counts = Counter(int(v) for v in flat[play])
        k = len(counts)
        # connected components per colour (4-neighbour)
        comp = np.full(flat.size, -1, np.int32)
        comps = {c: [] for c in counts}
        nid = 0
        for i in np.flatnonzero(play):
            if comp[i] >= 0:
                continue
            c = flat[i]
            stack, size = [i], 0
            comp[i] = nid
            while stack:
                j = stack.pop()
                size += 1
                y, x = divmod(int(j), w)
                for nb, ok in ((j - w, y > 0), (j + w, y < h - 1), (j - 1, x > 0), (j + 1, x < w - 1)):
                    if ok and comp[nb] < 0 and flat[nb] == c:
                        comp[nb] = nid
                        stack.append(nb)
            comps[int(c)].append(size)
            nid += 1
        # edges / thin detail
        gg = g.astype(np.int32)
        hp = (gg[:, 1:] >= 0) & (gg[:, :-1] >= 0)
        vp = (gg[1:, :] >= 0) & (gg[:-1, :] >= 0)
        pairs = int(hp.sum() + vp.sum())
        diff = int((hp & (gg[:, 1:] != gg[:, :-1])).sum() + (vp & (gg[1:, :] != gg[:-1, :])).sum())
        same_nb = np.zeros((h, w), np.int32)
        same_nb[:, 1:] += (gg[:, 1:] == gg[:, :-1]) & hp
        same_nb[:, :-1] += (gg[:, 1:] == gg[:, :-1]) & hp
        same_nb[1:, :] += (gg[1:, :] == gg[:-1, :]) & vp
        same_nb[:-1, :] += (gg[1:, :] == gg[:-1, :]) & vp
        thin = int(((same_nb <= 1) & (gg >= 0)).sum())
        p = np.array([counts[c] / n for c in sorted(counts)])
        entropy = float(-(p * np.log(p)).sum())
        ncomp = sum(len(v) for v in comps.values())
        small = sum(s for v in comps.values() for s in v if s <= 2)
        wave = ScreeningSimulator(g).peel_waves()
        maxwave = int(wave.max())
        color_wave = {c: {"first": int(wave[flat == c].min()), "median": float(np.median(wave[flat == c])),
                          "last": int(wave[flat == c].max())} for c in counts}
        m = {
            "width": w, "height": h, "total_cells": w * h, "playable_pixels": n, "color_count": k,
            "full_canvas": n == w * h,
            "histogram": {self.palette[used[c]][0]: counts[c] for c in sorted(counts)},
            "percent": {self.palette[used[c]][0]: round(100 * counts[c] / n, 2) for c in sorted(counts)},
            "components": {self.palette[used[c]][0]: len(comps[c]) for c in sorted(counts)},
            "component_sizes": {self.palette[used[c]][0]: sorted(comps[c], reverse=True) for c in sorted(counts)},
            "small_islands": sum(1 for v in comps.values() for s in v if s <= 2),
            "small_island_pixels": small,
            "edge_transition_density": diff / max(pairs, 1),
            "dominant_color_ratio": max(counts.values()) / n,
            "color_entropy": entropy,
            "color_entropy_norm": entropy / math.log(k) if k > 1 else 0.0,
            "fragmentation_per_100px": 100.0 * (ncomp - k) / n,
            "thin_detail_density": thin / n,
            "playable_density": n / (w * h),
            "access_layers": maxwave + 1,
            "color_access": {self.palette[used[c]][0]: color_wave[c] for c in sorted(counts)},
        }
        m["image_complexity_score"] = self.complexity_score(m)
        # internal (local index keyed) data for planning
        m["_local_counts"] = {c: counts[c] for c in sorted(counts)}
        m["_local_components"] = {c: len(comps[c]) for c in sorted(counts)}
        m["_local_access"] = {c: (color_wave[c]["median"] / max(maxwave, 1)) for c in sorted(counts)}
        m["_local_first"] = {c: (color_wave[c]["first"] / max(maxwave, 1)) for c in sorted(counts)}
        return m

    @staticmethod
    def complexity_score(m):
        """0..100 structural complexity. Weights/normalizers are tuning seeds (documented)."""
        cl = lambda v: max(0.0, min(1.0, v))
        parts = {
            "colors": (0.15, cl((m["color_count"] - 3) / 9)),
            "entropy": (0.10, m["color_entropy_norm"]),
            "fragmentation": (0.20, cl(m["fragmentation_per_100px"] / 6.0)),
            "islands": (0.10, cl(m["small_island_pixels"] / m["playable_pixels"] / 0.04)),
            "edges": (0.15, cl(m["edge_transition_density"] / 0.45)),
            "thin": (0.10, cl(m["thin_detail_density"] / 0.35)),
            "access_depth": (0.10, cl((m["access_layers"] - 3) / 17)),
            "size": (0.10, cl(math.log(max(m["playable_pixels"], 400) / 400) / math.log(3481 / 400))),
        }
        return round(100 * sum(wt * v for wt, v in parts.values()), 2)


