"""SupplyOptimizer: the pipeline.

image -> PixelAnalyzer -> DifficultyModel (band, mean batch size, dynamic batch/row count)
      -> many candidates (BatchPlanner + SupplyCandidateGenerator [+ mutations])
      -> ScreeningSimulator search (ranking only) -> SupplyScorer metrics/score
      -> ScrubBotsSolver (game's SolvabilitySolver + replay + Difficulty V1)  <- ACCEPTANCE
      -> SolutionVerifier invariants -> result (+ SupplyExporter)
Deterministic for (image, palette, rules, seed, settings).
"""
import random

from .batch_planner import BatchPlanner
from .candidate_generator import SupplyCandidateGenerator
from .difficulty_model import DifficultyModel
from .pixel_analyzer import PixelAnalyzer
from .screening import ScreeningSimulator
from .scrubbots_solver import ScrubBotsSolver
from .solution_verifier import SolutionVerifier
from .supply_scorer import SupplyScorer


class NoValidSupply(RuntimeError):
    pass


class SupplyOptimizer:
    def __init__(self, rules, solver=None):
        self.rules = rules
        self.analyzer = PixelAnalyzer(rules.palette)
        self.model = DifficultyModel(rules)
        self.solver = solver  # ScrubBotsSolver, created lazily (needs Godot)
        self.verifier = SolutionVerifier()

    # -------------------------------------------------------------- stages ---
    def prepare(self, image, target=None):
        grid, used = self.analyzer.load(image)
        m = self.analyzer.analyze(grid, used)
        band = self.model.band_for(m["image_complexity_score"], target)
        mean = self.model.mean_batch_size(m["image_complexity_score"], band)
        total, rows = self.model.plan_size(m["playable_pixels"], mean)
        return grid, used, m, band, mean, total, rows

    def candidate(self, m, mean, total, seed_key, safety):
        rng = random.Random(seed_key)
        plan = BatchPlanner(self.rules.max_robots_per_batch, rng).plan(
            m["_local_counts"], m["_local_components"], total, mean)
        gen = SupplyCandidateGenerator(self.rules.column_count, rng)
        # vary how early enclosed colours appear: low -> waiting batches / slot pressure,
        # high -> relaxed; screening rejects the unsolvable ones, the scorer picks the band fit
        return gen.generate(plan, m["_local_access"], m["_local_first"], safety * rng.uniform(0.3, 1.3)), gen

    def run(self, image, seed=0, candidates=300, target=None, level_id="pixelart_level",
            verify_top=1, screen_budget=3000, metric_top=12, viability_budget=3000,
            real_max_visited=None, level_number=1, progress=print):
        log = progress or (lambda *_: None)
        grid, used, m, band, mean, total, rows = self.prepare(image, target)
        log(f"image {m['width']}x{m['height']} playable={m['playable_pixels']} colors={m['color_count']} "
            f"complexity={m['image_complexity_score']} band={band} mean_batch={mean:.1f} "
            f"-> ~{total} batches / ~{rows} rows")
        sim = ScreeningSimulator(grid, self.rules.slot_count)
        counts = m["_local_counts"]
        attempts, pool = 0, []
        for rnd in range(4):  # bounded search; later rounds relax pressure (more safety, larger batches)
            safety = 1.0 + 0.2 * rnd
            mean_r = mean * (1.0 + 0.1 * rnd)
            total_r, _ = self.model.plan_size(m["playable_pixels"], mean_r)
            n_round = candidates if rnd == 0 else max(20, candidates // 3)
            for i in range(n_round):
                cols, gen = self.candidate(m, mean_r, total_r, f"{seed}:{rnd}:{i}", safety)
                for mut in range(4):  # original + up to 3 mutations
                    attempts += 1
                    per = {}
                    for col in cols:
                        for c, n in col:
                            per[c] = per.get(c, 0) + n
                    assert per == counts, "conservation violated in generation"  # never expected
                    r = sim.solve(cols, max_visited=screen_budget)
                    if r["status"] == "SOLVED":
                        pool.append({"id": f"s{seed}-r{rnd}-c{i}-m{mut}", "columns": cols, "screen": r, "round": rnd})
                        break
                    cols = gen.mutate(cols)
            log(f"round {rnd}: {len(pool)} screening-solvable / {attempts} attempts")
            if len(pool) >= max(5, metric_top):
                break
        if not pool:
            raise NoValidSupply(f"no candidate passed screening after {attempts} attempts")
        # gameplay metrics + score for the most promising (deterministic order)
        scorer = SupplyScorer(sim, self.rules.slot_count, viability_budget)
        pool.sort(key=lambda p: (p["round"], abs(sum(len(c) for c in p["columns"]) - total), p["id"]))
        scored = []
        steps = sum(len(c) for c in pool[0]["columns"])
        metric_top = max(4, min(metric_top, 2400 // max(steps, 1)))  # big levels: fewer full metric runs
        for p in pool[:metric_top]:
            p["metrics"] = scorer.metrics(p["columns"], p["screen"]["trace"])
            p["score"], p["score_parts"] = scorer.score(p["metrics"], band)
            scored.append(p)
        scored.sort(key=lambda p: (-p["score"], p["id"]))
        log("best screening scores: " + ", ".join(f"{p['id']}={p['score']}" for p in scored[:5]))
        # ACCEPTANCE: real game solver, best-first
        level = {"id": level_id, "width": m["width"], "height": m["height"],
                 "palette": [self.rules.palette[g][1] + "FF" for g in used],
                 "cells": [int(v) for v in grid.ravel()]}
        solver = self.solver or ScrubBotsSolver(self.rules)
        accepted, real_runs = [], []
        for start in range(0, len(scored), 4):
            chunk = scored[start:start + 4]
            resp = solver.run(level, [{"id": p["id"], "columns": [[{"color": c, "count": n} for c, n in col]
                                                                   for col in p["columns"]]} for p in chunk],
                              stop_after=verify_top - len(accepted), max_visited=real_max_visited,
                              analyze=m["full_canvas"], level_number=level_number,
                              progress=lambda l: log("  game solver: " + l))
            byid = {p["id"]: p for p in chunk}
            for rec in resp["results"]:
                real_runs.append({"id": rec["id"], "status": rec["status"], **rec.get("solver", {})})
                p = byid[rec["id"]]
                if rec["status"] != "SOLVED":
                    continue  # rejected: the game cannot prove a win
                ver = self.verifier.verify(counts, m["playable_pixels"], p["columns"], rec)
                if ver["all_ok"]:
                    accepted.append((p, rec, ver))
            if len(accepted) >= verify_top:
                break
        if not accepted:
            raise NoValidSupply("no candidate was proven SOLVED by the game's solver "
                                f"({len(real_runs)} real solver runs)")
        p, rec, ver = max(accepted, key=lambda a: (a[0]["score"], a[0]["id"]))
        # gameplay metrics on the REAL winning trace
        gm = scorer.metrics(p["columns"], rec["trace"])
        diff_cls, diff_score, basis = self.model.final(rec.get("difficultyV1"), m["image_complexity_score"], gm)
        cid = lambda c: self.rules.palette[used[c]][0]
        cols_out = [[{"color": cid(c), "amount": n} for c, n in col] for col in p["columns"]]
        result = {
            "image_width": m["width"], "image_height": m["height"], "playable_pixels": m["playable_pixels"],
            "color_count": m["color_count"], "exact_color_histogram": m["histogram"],
            "image_complexity_score": m["image_complexity_score"],
            "difficulty": diff_cls, "difficulty_score": diff_score, "difficulty_basis": basis,
            "generation_band": band, "target_mean_batch_size": round(mean, 2),
            "supply_rows": max(len(c) for c in p["columns"]), "total_batches": sum(len(c) for c in p["columns"]),
            "supply_columns": cols_out,
            "column_pixel_totals": ver["column_pixel_totals"],
            "color_conservation_verification": {
                "image": m["histogram"],
                "supply": {cid(c): sum(n for col in p["columns"] for cc, n in col if cc == c) for c in counts},
                "invariants": ver["checks"], "all_ok": ver["all_ok"]},
            "solver_status": rec["status"],
            "solution_trace": [{"step": i + 1, "column": a["column"] + 1, "batch": {"color": cid(a["color"]), "amount": a["count"]},
                                "clears": a["clears"], "pixels_left": a["active_after"]} for i, a in enumerate(rec["trace"])],
            "solution_final": "WIN" if rec["replay"]["solved"] and rec["replay"]["finalActive"] == 0 else "FAIL",
            "solution_length": len(rec["trace"]),
            "solution_replay": rec["replay"],
            "solver_metrics": {"game_solver": rec["solver"], "trace_hash": rec.get("traceHash"),
                               "gameplay": gm, "gameplay_quality_score": p["score"],
                               "gameplay_quality_parts": p["score_parts"],
                               "official_difficulty_v1": rec.get("difficultyV1")},
            "image": {k: v for k, v in m.items() if not k.startswith("_")},
            "generation_attempts": attempts, "screening_solvable_candidates": len(pool),
            "real_solver_runs": real_runs, "random_seed": seed,
            "settings": {"candidates": candidates, "target": target, "verify_top": verify_top,
                         "screen_budget": screen_budget, "metric_top": metric_top,
                         "batch_cap": None,
                         "batch_count_policy": "positive per-plan metadata bound; no global cap"},
            "export_notes": [],
            "_level": level,
        }
        return result

