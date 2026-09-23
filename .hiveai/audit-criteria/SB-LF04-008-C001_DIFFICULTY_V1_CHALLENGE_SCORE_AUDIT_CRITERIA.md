# SB-LF04-008-C001 — Difficulty V1 Challenge Score — Strict Audit Criteria

Target: SB-LF04-008

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

Implement deterministic engineering-policy Challenge Score V1 in [0,100] using ONLY guaranteed core metrics from 002/003: move_count, states_visited, dead_ends, branching, forced_moves. Optional 004-007 diagnostics are NOT in V1 and must not be treated as zero. Fixed normalizers: move=clamp(log1p(move_count)/log1p(64),0,1); states=clamp(log1p(states_visited)/log1p(10000),0,1); dead_end=clamp(dead_ends/max(states_visited,1),0,1); branching=clamp(branching/4.0,0,1); forced_relief=clamp(forced_moves/max(states_visited,1),0,1); forced_component=1-forced_relief. Coefficients: move .25, states .25, dead_end .15, branching .15, forced .20. score=100*weighted sum. All five required metrics must exist; do not renormalize weights. Create versioned policy/result with source LevelMetrics digest and component breakdown. No width/height/color/class in formula. Tests use hand-calculated values, bounds, missing metrics, zero-state edge, metadata independence and determinism.

## Required gates

Run focused task tests, affected earlier-M04 tests, retained M03 tests, relevant production/difficulty tests, full python -m pytest -q with zero failures, python -m compileall -q src tests, Level Factory Godot headless editor boot, git diff --check and git diff --exit-code -- TASKS.md.

## Acceptance

PASS only when semantics are versioned, deterministic, provenance-bound, honest about unavailable canonical data and do not preempt later task semantics.
