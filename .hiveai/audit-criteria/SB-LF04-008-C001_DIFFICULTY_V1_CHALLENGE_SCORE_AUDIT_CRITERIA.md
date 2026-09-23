# SB-LF04-008-C001 — Difficulty V1 Challenge Score — Strict Audit Criteria

Target:
`SB-LF04-008`

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

## Difficulty V1 policy

Implement an explicit engineering-policy score in [0,100]. It is deterministic and versioned, not empirically calibrated.

V1 uses only guaranteed core M04 metrics from 002/003:
- move_count
- states_visited
- dead_ends
- branching
- forced_moves

Dependency depth, slot pressure, bait/deadlock and volatility are diagnostic-only in V1 and MUST NOT be silently treated as zero when unavailable.

### Required normalization

Use fixed V1 saturating normalizers:
- move_component = clamp(log1p(move_count) / log1p(64), 0, 1)
- states_component = clamp(log1p(states_visited) / log1p(10000), 0, 1)
- dead_end_component = clamp(dead_ends / max(states_visited, 1), 0, 1)
- branching_component = clamp(branching / 4.0, 0, 1)
- forced_relief = clamp(forced_moves / max(states_visited, 1), 0, 1)
- forced_component = 1 - forced_relief

### Required coefficients

- move: 0.25
- states: 0.25
- dead_end: 0.15
- branching: 0.15
- forced: 0.20

challenge_score = 100 * weighted sum, rounded only for presentation; canonical numeric representation must be deterministic and documented.

All five required source metrics must be present. Otherwise score disposition is UNAVAILABLE/INCONCLUSIVE as appropriate; do not renormalize weights around missing metrics.

Define versioned ChallengeScorePolicy/Result with component values, coefficients, source LevelMetrics digest and policy version.

No board size, used color count or descriptive difficulty class enters the formula.

NaN/Infinity forbidden.

Tests must use hand-calculated known answers, bounds, missing component, zero-state edge, metadata/dimension/color independence and repeat determinism.

## Required repository gates

Focused task tests, affected predecessor M04 tests, retained M03 tests, full pytest green, compileall PASS, Godot headless editor boot PASS, git diff --check PASS and TASKS zero diff.

## Acceptance

PASS only when the task's metric/analysis semantics are versioned, deterministic, provenance-bound and do not overclaim unavailable gameplay truth.
