"""Deterministic post-Difficulty-V1 production placement."""

from __future__ import annotations

from collections.abc import Iterable, Mapping


def build_progression(entries: Iterable[Mapping[str, object]]) -> dict[str, object]:
    """Sort published levels by official score, then immutable level ID."""

    normalized = [dict(entry) for entry in entries]
    normalized.sort(key=lambda item: (float(item.get("difficulty_score", 0.0)), str(item["level_id"])))
    return {
        "schema": "scrubbots-level-progression-v1",
        "version": 1,
        "ordering": "difficulty_score_ascending_then_level_id_ascending",
        "levels": normalized,
    }


__all__ = ["build_progression"]
