# SB-LF04-003-C001 — States / Dead Ends / Branching / Forced Moves — Strict Audit Criteria

Target:
`SB-LF04-003`

M03 is COMPLETE / VERIFIED. SB-LF04-001 LevelMetrics V1 is the accepted M04 envelope prerequisite.

Global invariants:
- canonical gameplay truth remains in `Sekiph82/Scrubbots`;
- Factory must not copy gameplay rules;
- width/height 20..59 independently legal;
- used colors 3..12 independent of difficulty;
- descriptive difficulty is not derived from board size or color count;
- operational timing is non-canonical;
- missing canonical evidence remains absent/unavailable, never fabricated zero;
- analysis must not mutate gameplay/art source;
- builder never edits root `TASKS.md`.

## Required semantics

Populate:
- states_visited = SolverMetrics.visited_count
- dead_ends = SolverMetrics.dead_end_count
- branching = deterministic arithmetic mean of the observed SolverMetrics.branch_counts. If no branch observation exists, leave branching absent rather than inventing zero.
- forced_moves = number of observed branch_counts exactly equal to 1.

The branch_counts source is canonical provider-driven search evidence. Do not reconstruct legal actions from CompactSolverState.

Metrics are descriptive search-witness diagnostics, not proof that an alternative search policy has identical counts.

Requirements:
- exact LevelMetrics/evidence binding;
- finite non-negative branching;
- no division/order nondeterminism;
- preserve 002 values;
- unavailable/error evidence cannot gain measurements;
- no difficulty classification.

Tests: known branch tuple, single forced branch, multiple forced branches, no branch observations, repeat determinism, evidence mismatch, preservation of prior metrics.

## Required repository gates

Focused task tests, affected predecessor M04 tests, retained M03 tests, full pytest green, compileall PASS, Godot headless editor boot PASS, git diff --check PASS and TASKS zero diff.

## Acceptance

PASS only when the task's metric/analysis semantics are versioned, deterministic, provenance-bound and do not overclaim unavailable gameplay truth.
