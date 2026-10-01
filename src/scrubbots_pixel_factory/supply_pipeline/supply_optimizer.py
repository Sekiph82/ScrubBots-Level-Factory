"""Canonical owner-ZIP supply planning, ranking, solve, and verification route."""

import random

from .batch_planner import BatchPlanner
from .candidate_generator import SupplyCandidateGenerator
from .contracts import DEFAULT_COLUMN_COUNT, validate_column_count
from .difficulty_model import DifficultyModel
from .pixel_analyzer import PixelAnalyzer
from .screening import ScreeningSimulator
from .scrubbots_solver import ScrubBotsSolver
from .solution_verifier import SolutionVerifier
from .supply_scorer import SupplyScorer


class NoValidSupply(RuntimeError):
    pass


class SupplyOptimizer:
    """Deterministic ZIP-derived pipeline for an image or exact logical cells."""

    def __init__(self, rules, solver=None, column_count=None):
        self.rules = rules
        self.column_count = validate_column_count(
            getattr(rules, "column_count", DEFAULT_COLUMN_COUNT)
            if column_count is None else column_count
        )
        self.analyzer = PixelAnalyzer(rules.palette)
        self.model = DifficultyModel(rules)
        self.solver = solver
        self.verifier = SolutionVerifier()

    def prepare_grid(self, grid, used):
        m = self.analyzer.analyze(grid, used)
        band = self.model.band_for(m["image_complexity_score"])
        mean = self.model.mean_batch_size(m["image_complexity_score"], band)
        total, rows = self.model.plan_size(m["playable_pixels"], mean, self.column_count)
        return grid, used, m, band, mean, total, rows

    def prepare(self, image):
        grid, used = self.analyzer.load(image)
        return self.prepare_grid(grid, used)

    def candidate(self, m, mean, total, seed_key, safety):
        rng = random.Random(seed_key)
        plan = BatchPlanner(self.rules.max_robots_per_batch, rng).plan(
            m["_local_counts"], m["_local_components"], total, mean
        )
        generator = SupplyCandidateGenerator(self.column_count, rng)
        return generator.generate(
            plan, m["_local_access"], m["_local_first"], safety * rng.uniform(0.3, 1.3)
        ), generator

    def run(self, image, seed=0, candidates=300, level_id="pixelart_level",
            verify_top=1, screen_budget=3000, metric_top=12, viability_budget=3000,
            real_max_visited=None, level_number=1, progress=print):
        return self._run_prepared(
            *self.prepare(image), seed=seed, candidates=candidates, level_id=level_id,
            verify_top=verify_top, screen_budget=screen_budget, metric_top=metric_top,
            viability_budget=viability_budget, real_max_visited=real_max_visited,
            level_number=level_number, progress=progress,
        )

    def run_grid(self, grid, used, seed=0, candidates=300, level_id="pixelart_level",
                 verify_top=1, screen_budget=3000, metric_top=12, viability_budget=3000,
                 real_max_visited=None, level_number=1, progress=print):
        return self._run_prepared(
            *self.prepare_grid(grid, used), seed=seed, candidates=candidates,
            level_id=level_id, verify_top=verify_top, screen_budget=screen_budget,
            metric_top=metric_top, viability_budget=viability_budget,
            real_max_visited=real_max_visited, level_number=level_number,
            progress=progress,
        )

    def _run_prepared(self, grid, used, m, band, mean, total, rows, *, seed,
                      candidates, level_id, verify_top, screen_budget, metric_top,
                      viability_budget, real_max_visited, level_number, progress):
        log = progress or (lambda *_: None)
        log(
            f"image {m['width']}x{m['height']} playable={m['playable_pixels']} "
            f"colors={m['color_count']} complexity={m['image_complexity_score']} "
            f"band={band} mean_batch={mean:.1f} -> ~{total} batches / ~{rows} rows "
            f"across {self.column_count} columns"
        )
        sim = ScreeningSimulator(grid, self.rules.slot_count)
        counts = m["_local_counts"]
        attempts, pool = 0, []
        for rnd in range(4):
            safety = 1.0 + 0.2 * rnd
            mean_r = mean * (1.0 + 0.1 * rnd)
            total_r, _ = self.model.plan_size(m["playable_pixels"], mean_r, self.column_count)
            n_round = candidates if rnd == 0 else max(20, candidates // 3)
            for i in range(n_round):
                columns, generator = self.candidate(m, mean_r, total_r, f"{seed}:{rnd}:{i}", safety)
                for mutation in range(4):
                    attempts += 1
                    per = {}
                    for column in columns:
                        for color, amount in column:
                            per[color] = per.get(color, 0) + amount
                    assert per == counts, "conservation violated in generation"
                    screened = sim.solve(columns, max_visited=screen_budget)
                    if screened["status"] == "SOLVED":
                        pool.append({"id": f"s{seed}-r{rnd}-c{i}-m{mutation}", "columns": columns, "screen": screened, "round": rnd})
                        break
                    columns = generator.mutate(columns)
            log(f"round {rnd}: {len(pool)} screening-solvable / {attempts} attempts")
            if len(pool) >= max(5, metric_top):
                break
        if not pool:
            raise NoValidSupply(f"no candidate passed screening after {attempts} attempts")

        scorer = SupplyScorer(sim, self.rules.slot_count, viability_budget)
        pool.sort(key=lambda item: (item["round"], abs(sum(len(c) for c in item["columns"]) - total), item["id"]))
        scored = []
        steps = sum(len(column) for column in pool[0]["columns"])
        metric_top = max(4, min(metric_top, 2400 // max(steps, 1)))
        for candidate in pool[:metric_top]:
            candidate["metrics"] = scorer.metrics(candidate["columns"], candidate["screen"]["trace"])
            candidate["score"], candidate["score_parts"] = scorer.score(candidate["metrics"], band)
            scored.append(candidate)
        scored.sort(key=lambda item: (-item["score"], item["id"]))
        log("best screening scores: " + ", ".join(f"{p['id']}={p['score']}" for p in scored[:5]))

        level = {
            "id": level_id, "width": m["width"], "height": m["height"],
            "palette": [self.rules.palette[global_index][1] + "FF" for global_index in used],
            "cells": [int(value) for value in grid.ravel()],
        }
        solver = self.solver or ScrubBotsSolver(self.rules)
        accepted, real_runs = [], []
        for start in range(0, len(scored), 4):
            chunk = scored[start:start + 4]
            response = solver.run(
                level,
                [{"id": p["id"], "columns": [[{"color": c, "count": n} for c, n in column] for column in p["columns"]]} for p in chunk],
                stop_after=verify_top - len(accepted), max_visited=real_max_visited,
                analyze=m["full_canvas"], level_number=level_number,
                progress=lambda line: log("  game solver: " + line),
            )
            by_id = {p["id"]: p for p in chunk}
            for record in response["results"]:
                real_runs.append({"id": record["id"], "status": record["status"], **record.get("solver", {})})
                candidate = by_id[record["id"]]
                if record["status"] != "SOLVED":
                    continue
                verification = self.verifier.verify(
                    counts, m["playable_pixels"], candidate["columns"], record, self.column_count
                )
                official = record.get("difficultyV1")
                if verification["all_ok"] and isinstance(official, dict) and official.get("ok"):
                    accepted.append((candidate, record, verification))
            if len(accepted) >= verify_top:
                break
        if not accepted:
            raise NoValidSupply(
                "no candidate was proven SOLVED by the game's solver with official Difficulty V1 "
                f"({len(real_runs)} real solver runs)"
            )
        candidate, record, verification = max(accepted, key=lambda item: (item[0]["score"], item[0]["id"]))
        gameplay_metrics = scorer.metrics(candidate["columns"], record["trace"])
        difficulty_class, difficulty_score, difficulty_basis = self.model.final(
            record.get("difficultyV1"), m["image_complexity_score"], gameplay_metrics
        )
        color_id = lambda local: self.rules.palette[used[local]][0]
        output_columns = [[{"color": color_id(c), "amount": n} for c, n in column] for column in candidate["columns"]]
        return {
            "image_width": m["width"], "image_height": m["height"], "playable_pixels": m["playable_pixels"],
            "color_count": m["color_count"], "exact_color_histogram": m["histogram"],
            "image_complexity_score": m["image_complexity_score"],
            "difficulty": difficulty_class, "difficulty_score": difficulty_score, "difficulty_basis": difficulty_basis,
            "generation_band": band, "target_mean_batch_size": round(mean, 2),
            "column_count": self.column_count, "visible_preview_depth": 3,
            "supply_rows": max(len(column) for column in candidate["columns"]),
            "total_batches": sum(len(column) for column in candidate["columns"]),
            "supply_columns": output_columns, "column_pixel_totals": verification["column_pixel_totals"],
            "color_conservation_verification": {
                "image": m["histogram"],
                "supply": {color_id(c): sum(n for column in candidate["columns"] for cc, n in column if cc == c) for c in counts},
                "invariants": verification["checks"], "all_ok": verification["all_ok"],
            },
            "solver_status": record["status"],
            "solution_trace": [{"step": i + 1, "column": a["column"] + 1, "batch": {"color": color_id(a["color"]), "amount": a["count"]}, "clears": a["clears"], "pixels_left": a["active_after"]} for i, a in enumerate(record["trace"])],
            "solution_final": "WIN" if record["replay"]["solved"] and record["replay"]["finalActive"] == 0 else "FAIL",
            "solution_length": len(record["trace"]), "solution_replay": record["replay"],
            "solver_metrics": {"game_solver": record["solver"], "trace_hash": record.get("traceHash"), "gameplay": gameplay_metrics, "gameplay_quality_score": candidate["score"], "gameplay_quality_parts": candidate["score_parts"], "official_difficulty_v1": record.get("difficultyV1")},
            "image": {key: value for key, value in m.items() if not key.startswith("_")},
            "generation_attempts": attempts, "screening_solvable_candidates": len(pool), "real_solver_runs": real_runs, "random_seed": seed,
            "settings": {"candidates": candidates, "column_count": self.column_count, "visible_preview_depth": 3, "verify_top": verify_top, "screen_budget": screen_budget, "metric_top": metric_top, "viability_budget": viability_budget, "batch_cap": None, "slot_count": getattr(self.rules, "baseline_slot_count", 5), "batch_count_policy": "positive per-plan metadata bound; no global cap"},
            "export_notes": [], "_level": level,
        }
