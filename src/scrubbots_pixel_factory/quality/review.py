"""Deterministic, self-contained M07 review manifest and contact sheet."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
import html
import json
from pathlib import Path

from ..contracts import Difficulty, parse_difficulty
from .core import GridInput, QualityPolicy, QualityReport, diversity_report, evaluate_grid, logical_grid_hash


@dataclass(frozen=True, slots=True)
class ReviewEntry:
    candidate_id: str
    width: int
    height: int
    cells: tuple[str, ...]
    mode: str | None = None
    seed: int | str | None = None
    difficulty: Difficulty | str | None = None
    policy: QualityPolicy = QualityPolicy()

    def __init__(
        self,
        candidate_id: str,
        width: int,
        height: int,
        cells: Iterable[str],
        *,
        mode: str | None = None,
        seed: int | str | None = None,
        difficulty: Difficulty | str | None = None,
        policy: QualityPolicy | None = None,
    ) -> None:
        if type(candidate_id) is not str or not candidate_id:
            raise ValueError("candidate_id must be a non-empty string")
        object.__setattr__(self, "candidate_id", candidate_id)
        object.__setattr__(self, "width", width)
        object.__setattr__(self, "height", height)
        object.__setattr__(self, "cells", tuple(cells))
        object.__setattr__(self, "mode", mode)
        object.__setattr__(self, "seed", seed)
        object.__setattr__(self, "difficulty", parse_difficulty(difficulty) if difficulty is not None else None)
        object.__setattr__(self, "policy", policy or QualityPolicy())


def _assessed(entry: ReviewEntry) -> QualityReport:
    return evaluate_grid(entry.width, entry.height, entry.cells, policy=entry.policy)


def _entry_dict(entry: ReviewEntry, report: QualityReport) -> dict[str, object]:
    analysis = report.analysis
    used_count = len(analysis.used_colors) if analysis else None
    grid_hash = logical_grid_hash(entry.width, entry.height, entry.cells) if analysis else None
    return {
        "candidate_id": entry.candidate_id,
        "generator_mode": entry.mode,
        "seed": entry.seed,
        "difficulty": entry.difficulty.value if isinstance(entry.difficulty, Difficulty) else entry.difficulty,
        "width": entry.width,
        "height": entry.height,
        "used_color_count": used_count,
        "used_colors": list(analysis.used_colors) if analysis else [],
        "negative_space_color": analysis.negative_space.inferred_color if analysis else None,
        "metrics": analysis.metrics.as_dict() if analysis else None,
        "quality_decision": "ACCEPT" if report.accepted else "REJECT",
        "rejection_codes": list(report.rejection_codes),
        "grid_hash": grid_hash,
        "policy": entry.policy.as_dict(),
        "human_review": "",
    }


def build_review_manifest(entries: Iterable[ReviewEntry]) -> dict[str, object]:
    ordered = tuple(sorted(entries, key=lambda entry: entry.candidate_id))
    reports = tuple(_assessed(entry) for entry in ordered)
    manifest_entries = [_entry_dict(entry, report) for entry, report in zip(ordered, reports, strict=True)]
    valid = tuple((entry, report) for entry, report in zip(ordered, reports, strict=True) if report.analysis is not None)
    valid_grids = tuple(GridInput(entry.width, entry.height, entry.cells) for entry, _ in valid)
    diversity = diversity_report(valid_grids, near_duplicate_threshold=0.95)
    candidate_ids = tuple(entry.candidate_id for entry, _ in valid)
    diversity_dict = diversity.as_dict()
    diversity_dict["candidate_ids"] = list(candidate_ids)
    exact_by_index: dict[int, list[str]] = {}
    for group in diversity.exact_duplicate_groups:
        names = [candidate_ids[index] for index in group]
        for index in group:
            exact_by_index[index] = names
    near_by_index: dict[int, list[dict[str, object]]] = {}
    for pair in diversity.near_duplicate_pairs:
        left = {"candidate_id": candidate_ids[pair.second_index], **pair.similarity.as_dict()}
        right = {"candidate_id": candidate_ids[pair.first_index], **pair.similarity.as_dict()}
        near_by_index.setdefault(pair.first_index, []).append(left)
        near_by_index.setdefault(pair.second_index, []).append(right)
    valid_index_by_entry = {entry.candidate_id: index for index, (entry, _) in enumerate(valid)}
    for manifest_entry in manifest_entries:
        index = valid_index_by_entry.get(str(manifest_entry["candidate_id"]))
        manifest_entry["diversity"] = {
            "exact_duplicate_group": exact_by_index.get(index) if index is not None else None,
            "near_duplicate_pairs": near_by_index.get(index, []) if index is not None else [],
        }
    return {
        "schema": "scrubbots-m07-review-manifest",
        "version": 1,
        "description": "Deterministic structural quality evidence; human_review is intentionally blank until owner review.",
        "quality_layer": {"schema": "scrubbots-quality", "version": 1},
        "entries": manifest_entries,
        "diversity_evidence": diversity_dict,
    }


def _cell_color(color_id: str) -> str:
    from ..contracts import CANONICAL_PALETTE

    return CANONICAL_PALETTE.hex_for(color_id)


def build_contact_sheet(entries: Iterable[ReviewEntry]) -> str:
    ordered = tuple(sorted(entries, key=lambda entry: entry.candidate_id))
    cards: list[str] = []
    for entry in ordered:
        report = _assessed(entry)
        analysis = report.analysis
        cells = entry.cells
        spans: list[str] = []
        if analysis:
            for cell in cells:
                spans.append(f'<span class="cell" style="background:{_cell_color(cell)}"></span>')
        grid_html = "".join(spans)
        grid_style = f"grid-template-columns:repeat({entry.width},6px);grid-template-rows:repeat({entry.height},6px);"
        metric_summary = "unavailable"
        if analysis:
            metric_summary = (
                f"occupied {analysis.metrics.occupied_ratio:.4f}; "
                f"components {analysis.metrics.occupied_component_count}; "
                f"negative-space {analysis.negative_space.inferred_color}; "
                f"colors {len(analysis.used_colors)}"
            )
        cards.append(
            "<article class=\"card\">"
            f"<h2>{html.escape(entry.candidate_id)}</h2>"
            f"<p>mode={html.escape(str(entry.mode))} seed={html.escape(str(entry.seed))} "
            f"difficulty={html.escape(str(entry.difficulty))} dimensions={entry.width}×{entry.height}</p>"
            f"<div class=\"grid\" style=\"{grid_style}\">{grid_html}</div>"
            f"<p>{html.escape(metric_summary)}</p>"
            f"<p class=\"{'accept' if report.accepted else 'reject'}\">"
            f"{'ACCEPT' if report.accepted else 'REJECT'} "
            f"{html.escape(', '.join(report.rejection_codes) or 'none')}</p>"
            "</article>"
        )
    return (
        "<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<title>SCRUBBOTS M07 Review</title><style>"
        "body{background:#202533;color:#fff;font-family:monospace;margin:20px}"
        ".sheet{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px}"
        ".card{background:#30384b;padding:12px;border:1px solid #59657d}"
        ".grid{display:grid;gap:0;width:max-content;image-rendering:pixelated;border:1px solid #fff}"
        ".cell{width:6px;height:6px;display:block}.accept{color:#63d6a3}.reject{color:#ff8d8d}"
        "h1{color:#f2c94c}</style></head><body>"
        "<h1>PAG-M07 — Artwork Quality &amp; Diversity Filters</h1>"
        "<p>Structural evidence only. Human review fields remain blank in the manifest.</p>"
        f"<section class=\"sheet\">{''.join(cards)}</section></body></html>\n"
    )


def write_review_pack(entries: Iterable[ReviewEntry], output_dir: str | Path) -> tuple[Path, Path]:
    ordered = tuple(sorted(entries, key=lambda entry: entry.candidate_id))
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    manifest_path = destination / "m07_review_manifest.json"
    contact_path = destination / "M07_QUALITY_CONTACT_SHEET.html"
    manifest_path.write_text(
        json.dumps(build_review_manifest(ordered), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    contact_path.write_text(build_contact_sheet(ordered), encoding="utf-8")
    return manifest_path, contact_path


__all__ = ["ReviewEntry", "build_contact_sheet", "build_review_manifest", "write_review_pack"]
