# SB-LF04-007-C001 — Color / Remaining-State Volatility — Strict Audit Criteria

Target:
`SB-LF04-007`

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

## Scope

Add one versioned volatility diagnostic only where canonical state observations make it meaningful.

Do not use image pixel fragmentation as gameplay volatility.

Recommended V1 semantic when an ordered canonical state trace is available:
- build a closed normalized gameplay-state signature from canonical quantities that are already exposed without rule reimplementation, such as remaining active-cell count, supply remaining count and occupied-slot count;
- per transition delta = normalized absolute change across those declared quantities;
- volatility = arithmetic mean of transition deltas, bounded [0,1].

The exact signature fields, normalization denominators and formula must be versioned and documented.

If required canonical trace quantities are unavailable, production volatility remains absent/UNAVAILABLE.

“Color volatility” may only be included if canonical state authority exposes a stable color-distribution quantity; do not inspect rendered art as a substitute.

Tests: stable trace = 0, changing trace, bounds, one-state trace absent, repeat determinism, unavailable/malformed trace.

## Required repository gates

Focused task tests, affected predecessor M04 tests, retained M03 tests, full pytest green, compileall PASS, Godot headless editor boot PASS, git diff --check PASS and TASKS zero diff.

## Acceptance

PASS only when the task's metric/analysis semantics are versioned, deterministic, provenance-bound and do not overclaim unavailable gameplay truth.
