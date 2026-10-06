"""Tests for the ScrubBots supply pipeline.

  python -m unittest scrubbots_supply.tests.test_supply_pipeline            # fast + game-solver tests
  set SCRUBBOTS_SLOW=1  -> also the full 37x37 and 59x59 real-solver pipelines
Game-solver tests are skipped when Godot or the ScrubBots project is missing.
"""
import json
import math
import os
import random
import subprocess
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from scrubbots_pixel_factory.supply_pipeline import GameRules, SupplyExporter, SupplyOptimizer, find_godot
from scrubbots_pixel_factory.supply_pipeline.batch_planner import BatchPlanner
from scrubbots_pixel_factory.supply_pipeline.screening import ScreeningSimulator
from scrubbots_pixel_factory.supply_pipeline.scrubbots_solver import ScrubBotsSolver
from scrubbots_pixel_factory.supply_pipeline.solution_verifier import SolutionVerifier

def _explicit_game_rules():
    """Use only a caller-provided game checkout; never discover a Desktop checkout."""
    configured = os.environ.get("SCRUBBOTS_PROJECT", "").strip()
    if not configured:
        return None

    project = Path(configured).expanduser().resolve()
    if not (project / "project.godot").is_file():
        raise RuntimeError(f"SCRUBBOTS_PROJECT is not a Godot project: {project}")
    remote = subprocess.run(
        ["git", "-C", str(project), "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
        check=False,
    )
    allowed_origins = {
        "https://github.com/sekiph82/scrubbots.git",
        "https://github.com/sekiph82/scrubbots",
        "git@github.com:sekiph82/scrubbots.git",
        "ssh://git@github.com/sekiph82/scrubbots.git",
    }
    if remote.returncode != 0 or remote.stdout.strip().lower() not in allowed_origins:
        raise RuntimeError(f"SCRUBBOTS_PROJECT origin is not the canonical ScrubBots repository: {project}")
    try:
        return GameRules(project=project)
    except FileNotFoundError:
        return None


RULES = _explicit_game_rules()
HAVE_GAME = RULES is not None and find_godot() is not None
SLOW = os.environ.get("SCRUBBOTS_SLOW") == "1"
TMP = Path(tempfile.mkdtemp(prefix="sb_tests_"))


def palette_rgb(cids):
    hexes = dict(RULES.palette)
    return [tuple(int(hexes[c][i:i + 2], 16) for i in (1, 3, 5)) for c in cids]


def make_image(idx, cids, name):
    """idx: (h, w) int array of indices into cids (-1 transparent)."""
    rgb = palette_rgb(cids)
    h, w = idx.shape
    a = np.zeros((h, w, 4), np.uint8)
    for i, c in enumerate(rgb):
        a[idx == i, :3] = c
        a[idx == i, 3] = 255
    p = TMP / f"{name}.png"
    Image.fromarray(a, "RGBA").save(p)
    return p


def scene(w, h, seed):
    """Full-canvas scene: sky speckle, hills, ground, a round object (like the reference)."""
    r = np.random.default_rng(seed)
    idx = np.where(r.random((h, w)) < 0.3, 1, 0)  # sky / cloud
    ys, xs = np.mgrid[0:h, 0:w]
    hill = (h * 0.45 + h * 0.08 * np.sin(xs / (w / 6))).astype(int)
    ground = (h * 0.62 + h * 0.04 * np.sin(xs / (w / 4) + 2)).astype(int)
    idx[(ys >= hill) & (ys < ground)] = 2
    idx[ys == ground] = 3
    idx[ys > ground] = 4
    obj = (xs - w * 0.3) ** 2 + (ys - h * 0.75) ** 2 <= (min(w, h) * 0.15) ** 2
    idx[obj] = 5
    idx[obj & ((xs - w * 0.3) ** 2 + (ys - h * 0.75) ** 2 <= (min(w, h) * 0.07) ** 2)] = 6
    return idx, ["C06", "C15", "C04", "C11", "C12", "C07", "C16"]


def contiguous(w, h):
    ys, xs = np.mgrid[0:h, 0:w]
    idx = np.zeros((h, w), int)
    idx[ys > h // 3] = 1
    idx[ys > 2 * h // 3] = 2
    return idx, ["C07", "C04", "C02"]


def fragmented(w, h, seed=3):
    r = np.random.default_rng(seed)
    blocks = r.integers(0, 10, (h // 2 + 1, w // 2 + 1))
    return np.kron(blocks, np.ones((2, 2), int))[:h, :w], ["C01", "C02", "C03", "C04", "C05",
                                                           "C06", "C07", "C08", "C09", "C10"]


@unittest.skipIf(RULES is None, "ScrubBots project not found")
class FastTests(unittest.TestCase):
    def test_planner_exact_conservation_and_variation(self):
        for seed in range(200):
            rng = random.Random(seed)
            counts = {0: rng.randint(1, 900), 1: rng.randint(1, 300), 2: rng.randint(1, 40)}
            comps = {c: rng.randint(1, 30) for c in counts}
            mean = rng.uniform(11, 25)
            plan = BatchPlanner(None, rng).plan(counts, comps, round(sum(counts.values()) / mean), mean)
            for c, sizes in plan.items():
                self.assertEqual(sum(sizes), counts[c])
                self.assertTrue(all(s >= 1 for s in sizes))
            big = plan[0]
            if len(big) >= 6:
                self.assertGreater(len(set(big)), 2, "sizes should vary")

    def test_uncapped_plan_allows_more_than_thirty_robots_per_batch(self):
        plan = BatchPlanner(None, random.Random(991)).plan({0: 120}, {0: 1}, 3, 40.0)
        self.assertGreater(max(plan[0]), 30)

    def test_candidates_never_miss_or_add_pixels(self):
        opt = SupplyOptimizer(RULES)
        for name, (idx, cids) in {"contig": contiguous(32, 32), "frag": fragmented(32, 32),
                                  "scene": scene(37, 37, 1)}.items():
            grid, used, m, band, mean, total, rows = opt.prepare(make_image(idx, cids, name))
            for i in range(30):
                cols, _ = opt.candidate(m, mean, total, f"t:{i}", 1.0)
                per = {}
                for col in cols:
                    for c, n in col:
                        per[c] = per.get(c, 0) + n
                self.assertEqual(per, m["_local_counts"], name)
                self.assertEqual(sum(per.values()), m["playable_pixels"])
                self.assertEqual(len(cols), 3)
                self.assertTrue(all(cols))

    def test_dynamic_row_scaling(self):
        """Regression: supply rows come from active pixels + complexity, never a fixed 18."""
        opt = SupplyOptimizer(RULES)
        out = {}
        for size in (20, 37, 59):
            idx, cids = scene(size, size, 1)
            _, _, m, band, mean, total, rows = opt.prepare(make_image(idx, cids, f"scale{size}"))
            out[size] = (m["playable_pixels"], total, rows)
        self.assertLess(out[20][2], out[37][2])
        self.assertGreater(out[59][2], 1.8 * out[37][2], out)  # 59x59 gets substantially more rows
        self.assertGreater(len({r for _, _, r in out.values()}), 2)
        for n, total, rows in out.values():
            self.assertEqual(rows, math.ceil(total / 3))

    def test_fragmented_is_more_complex_and_gets_more_batches_per_pixel(self):
        opt = SupplyOptimizer(RULES)
        _, _, mc, _, meanc, totc, _ = opt.prepare(make_image(*contiguous(32, 32), "c2"))
        _, _, mf, _, meanf, totf, _ = opt.prepare(make_image(*fragmented(32, 32), "f2"))
        self.assertGreater(mf["image_complexity_score"], mc["image_complexity_score"] + 20)
        self.assertGreater(totf / mf["playable_pixels"], totc / mc["playable_pixels"])

    def test_verifier_rejects_extra_and_missing_pixels(self):
        counts = {0: 10, 1: 5}
        real = {"status": "SOLVED", "trace": [], "replay": {"ok": True, "solved": True, "finalActive": 0}}
        good = [[(0, 6)], [(0, 4)], [(1, 5)]]
        self.assertTrue(SolutionVerifier().verify(counts, 15, good, real)["checks"]["per_color_supply_equals_image"])
        extra = [[(0, 7)], [(0, 4)], [(1, 5)]]
        missing = [[(0, 6)], [(0, 3)], [(1, 5)]]
        for cols in (extra, missing):
            self.assertFalse(SolutionVerifier().verify(counts, 15, cols, real)["all_ok"])

    def test_screening_detects_unsolvable(self):
        idx, cols = enclosed_unsolvable()
        self.assertEqual(ScreeningSimulator(idx).solve(cols)["status"], "DEADLOCK")


def enclosed_unsolvable():
    """Colour 1 (centre) is enclosed by colour 0. Every column starts with 5 colour-1 batches,
    so 5 slots fill with waiting batches before any colour-0 batch can be placed: no win."""
    idx = np.zeros((6, 6), int)
    idx[2:4, 2:4] = 1  # 4 enclosed cells... need 15 single-robot colour-1 batches -> 15 cells
    idx = np.zeros((9, 9), int)
    idx[2:7, 2:5] = 1  # 15 cells, fully enclosed by colour 0 ring
    ring = int((idx == 0).sum())
    col = [(1, 1)] * 5
    return idx, [col + [(0, ring)], list(col), list(col)]


@unittest.skipUnless(HAVE_GAME, "Godot / ScrubBots project not available")
class GameSolverTests(unittest.TestCase):
    def level_of(self, idx, cids):
        hexes = dict(RULES.palette)
        return {"id": "t", "width": idx.shape[1], "height": idx.shape[0],
                "palette": [hexes[c] + "FF" for c in cids], "cells": [int(v) for v in idx.ravel()]}

    def test_intentionally_unsolvable_supply_is_rejected(self):
        idx, cols = enclosed_unsolvable()
        lvl = self.level_of(idx, ["C07", "C01"])
        resp = ScrubBotsSolver(RULES).run(lvl, [{"id": "bad", "columns": [[{"color": c, "count": n} for c, n in col]
                                                                         for col in cols]}], analyze=False)
        rec = resp["results"][0]
        self.assertEqual(rec["status"], "DEADLOCK")
        counts = {0: int((idx == 0).sum()), 1: int((idx == 1).sum())}
        self.assertFalse(SolutionVerifier().verify(counts, idx.size, cols, rec)["all_ok"])

    def test_screening_traces_replay_exactly_in_the_real_game(self):
        """Differential: screening solutions replay step-exact through SolvabilitySolver.replay."""
        root = RULES.project / "data/levels"
        pal = dict(RULES.palette)
        cands, level = [], None
        for lvl_name in ("level_004_orange_cat", "level_008_butterfly"):
            lvl = json.loads((root / f"{lvl_name}.json").read_text())
            plan = json.loads((root / "supply" / f"{lvl_name}_supply_v1.json").read_text())
            local = {h[:7].upper(): i for i, h in enumerate(lvl["palette"])}
            cols = [[(local[pal[b["cid"]]], b["robots"]) for b in col] for col in plan["columns"]]
            grid = np.array(lvl["cells"]).reshape(lvl["height"], lvl["width"])
            r = ScreeningSimulator(grid).solve(cols)
            self.assertEqual(r["status"], "SOLVED", lvl_name)
            level = {"id": lvl_name, "width": lvl["width"], "height": lvl["height"], "palette": lvl["palette"],
                     "cells": lvl["cells"]}
            resp = ScrubBotsSolver(RULES).run(level, [{"id": lvl_name, "columns": [[{"color": c, "count": n} for c, n in col]
                                                                                     for col in cols],
                                                       "replay_trace": r["trace"]}], analyze=False)
            rp = resp["results"][0]["replay"]
            self.assertTrue(rp["ok"] and rp["solved"] and rp["finalActive"] == 0, (lvl_name, rp))

    def run_pipeline(self, idx, cids, name, seed=11, candidates=60):
        res = SupplyOptimizer(RULES).run(make_image(idx, cids, name), seed=seed, candidates=candidates,
                                         level_id=name, progress=None)
        self.assertEqual(res["solver_status"], "SOLVED")
        self.assertEqual(res["solution_final"], "WIN")
        self.assertEqual(res["solution_replay"]["finalActive"], 0)
        self.assertTrue(res["color_conservation_verification"]["all_ok"])
        self.assertEqual(sum(res["column_pixel_totals"]), res["playable_pixels"])
        self.assertEqual(res["solution_length"], res["total_batches"])
        return res

    def test_small_image_accepted_and_replays_to_win(self):
        idx, cids = scene(20, 20, 2)
        res = self.run_pipeline(idx, cids, "small20")
        files = SupplyExporter(RULES).export(res, TMP / "out", "small20")
        self.assertIn("supply_plan", files)

    def test_deterministic_seed_reproduction(self):
        idx, cids = contiguous(20, 20)
        a = self.run_pipeline(idx, cids, "det", seed=5, candidates=30)
        b = self.run_pipeline(idx, cids, "det", seed=5, candidates=30)
        for k in ("supply_columns", "solution_trace", "difficulty_score", "generation_attempts"):
            self.assertEqual(a[k], b[k], k)

    def test_low_color_contiguous_and_fragmented(self):
        self.run_pipeline(*contiguous(24, 24), "contig24")
        self.run_pipeline(*fragmented(24, 24), "frag24")

    @unittest.skipUnless(SLOW, "set SCRUBBOTS_SLOW=1")
    def test_37_and_59_full_pipeline_rows_scale(self):
        r37 = self.run_pipeline(*scene(37, 37, 1), "scene37", candidates=80)
        r59 = self.run_pipeline(*scene(59, 59, 1), "scene59", candidates=60)
        self.assertGreater(r59["supply_rows"], 1.8 * r37["supply_rows"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

