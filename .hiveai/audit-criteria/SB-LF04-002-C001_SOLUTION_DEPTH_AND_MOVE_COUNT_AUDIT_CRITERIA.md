# SB-LF04-002-C001 — Solution Depth / Move Count — Strict Audit Criteria

Target: SB-LF04-002

Prerequisites:
- M03 COMPLETE / VERIFIED.
- SB-LF04-001 LevelMetrics V1 PASS/CLOSED.
- Every earlier M04 task in this batch is a builder dependency claim only until independently audited after the whole batch.

Global invariants:
- Canonical gameplay truth remains in Sekiph82/Scrubbots.
- No Python copy of gameplay rules.
- Width and height 20..59 independently legal.
- Used colors 3..12 independent of difficulty.
- Difficulty is never inferred from board size or used-color count.
- Operational timing is non-canonical.
- Missing canonical evidence remains absent/UNAVAILABLE, never fabricated zero.
- Analysis is read-only and never mutates gameplay/art source.
- Builder never edits root TASKS.md.

## Task-specific contract

Populate only LevelMetrics.solution_depth and move_count from the exact accepted SolverEvidenceReport bound by schema/version/digest. For AVAILABLE+SOLVED, move_count is the number of canonical LegalMove selections in the recorded witness path and solution_depth is the edge depth of that same witness. Do not call the path shortest/optimal/minimal. Solved-at-start may be 0/0. PROVEN_UNSOLVABLE, INCONCLUSIVE, UNAVAILABLE, ERROR, or missing witness evidence must leave both fields absent, never fabricated zero. Preserve all unrelated metrics and provenance. Pure deterministic transformation only; no new gameplay call, no wall-clock data, no source mutation. Tests: solved witness, solved-at-start, non-solved dispositions, evidence mismatch, deterministic repeat, prior metric preservation.

## Required gates

Run focused task tests, affected earlier-M04 tests, retained M03 tests, relevant production/difficulty tests, full python -m pytest -q with zero failures, python -m compileall -q src tests, Level Factory Godot headless editor boot, git diff --check and git diff --exit-code -- TASKS.md.

## Acceptance

PASS only when semantics are versioned, deterministic, provenance-bound, honest about unavailable canonical data and do not preempt later task semantics.
