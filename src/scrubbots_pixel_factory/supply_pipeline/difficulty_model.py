"""DifficultyModel: image complexity -> generation band; final class from the game's own
Difficulty V1 Challenge Score (LevelDifficultyAnalyzerV1, measured on the solver-proven path).

The mean-batch-size bands below are TUNING SEEDS, not rules.
"""
import math

CLASSES = ("EASY", "MEDIUM", "HARD", "VERY_HARD")
# target mean robots per batch (seeds); smaller mean -> more batches -> more decisions/pressure
MEAN_BATCH_SEED = {"EASY": (21.0, 25.0), "MEDIUM": (18.0, 22.0), "HARD": (14.0, 18.0), "VERY_HARD": (11.0, 15.0)}
# image complexity score edges used only to pick the starting band (seeds)
COMPLEXITY_EDGES = (30.0, 50.0, 70.0)


class DifficultyModel:
    def __init__(self, rules):
        self.rules = rules

    def band_for(self, image_score, override=None):
        if override in CLASSES:
            return override
        for cls, edge in zip(CLASSES, COMPLEXITY_EDGES):
            if image_score < edge:
                return cls
        return "VERY_HARD"

    def mean_batch_size(self, image_score, band):
        """Within the band, a more complex image gets the smaller end of the seed range."""
        lo, hi = MEAN_BATCH_SEED[band]
        i = CLASSES.index(band)
        left = (0.0,) + COMPLEXITY_EDGES
        right = COMPLEXITY_EDGES + (100.0,)
        t = max(0.0, min(1.0, (image_score - left[i]) / (right[i] - left[i])))
        return min(hi - t * (hi - lo), float(self.rules.max_robots_per_batch or 10 ** 9))

    def plan_size(self, playable, mean):
        total = max(self.rules.column_count, round(playable / mean))
        return total, math.ceil(total / self.rules.column_count)

    def final(self, official, image_score, gameplay):
        """official: bridge difficultyV1 (ok + challengeScore) or None (non-production image).
        Returns (class, score, basis)."""
        if official and official.get("ok"):
            d = float(official["challengeScore"])
            return self.rules.classify(d), round(d, 2), "ScrubBots Difficulty V1 challengeScore (official analyzer)"
        # provisional: transparent/non-production images cannot be analysed by the game
        d = 0.5 * image_score + 0.5 * gameplay.get("pressure_index", 0.0)
        return self.rules.classify(d), round(d, 2), "PROVISIONAL image+solver blend (official analyzer needs a full-canvas level)"


