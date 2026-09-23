# SB-LF04-003-C001 — States / Dead Ends / Branching / Forced Moves — Strict Audit Criteria

Target: SB-LF04-003

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

Populate states_visited=SolverMetrics.visited_count, dead_ends=dead_end_count, branching=deterministic arithmetic mean of observed branch_counts, and forced_moves=count(branch_count==1). If no branch observation exists, branching stays absent rather than zero. Use only accepted SolverMetrics; never reconstruct legal actions from CompactSolverState. Preserve 002 metrics and provenance. Tests must cover known branch tuples, forced branches, no branches, evidence mismatch, determinism and preservation.

## Required gates

Run focused task tests, affected earlier-M04 tests, retained M03 tests, relevant production/difficulty tests, full python -m pytest -q with zero failures, python -m compileall -q src tests, Level Factory Godot headless editor boot, git diff --check and git diff --exit-code -- TASKS.md.

## Acceptance

PASS only when semantics are versioned, deterministic, provenance-bound, honest about unavailable canonical data and do not preempt later task semantics.
