# SB-LF04-004-C001 — Canonical Dependency Depth — Strict Audit Criteria

Target: SB-LF04-004

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

Dependency depth is legal only from an explicit canonical dependency-semantics provider bound to accepted ScrubBots gameplay authority. M03 path depth is not dependency depth. Do not infer dependency from colors, adjacency, WFC, move order, dimensions or heuristics. Define a versioned provider/result with AVAILABLE/UNAVAILABLE/ERROR and exact authority/state/evidence binding. If no canonical dependency semantics are executable in current main-game authority, production must truthfully remain UNAVAILABLE and LevelMetrics.dependency_depth absent. Fixture-only providers may validate the contract but cannot become production authority.

## Required gates

Run focused task tests, affected earlier-M04 tests, retained M03 tests, relevant production/difficulty tests, full python -m pytest -q with zero failures, python -m compileall -q src tests, Level Factory Godot headless editor boot, git diff --check and git diff --exit-code -- TASKS.md.

## Acceptance

PASS only when semantics are versioned, deterministic, provenance-bound, honest about unavailable canonical data and do not preempt later task semantics.
