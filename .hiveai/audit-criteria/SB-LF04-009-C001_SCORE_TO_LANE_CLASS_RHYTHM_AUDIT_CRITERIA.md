# SB-LF04-009-C001 — Score to Lane / Class Rhythm — Strict Audit Criteria

Target:
`SB-LF04-009`

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

## Mapping policy

Map an AVAILABLE Difficulty V1 score in [0,100] to the current four classification lanes using a versioned score-only policy:

- EASY: 0 <= score < 25
- MEDIUM: 25 <= score < 50
- HARD: 50 <= score < 75
- VERY_HARD: 75 <= score <= 100

Define boundary behavior exactly.

The predicted class is analysis output. It must not rewrite:
- requested difficulty metadata;
- board dimensions;
- palette/color count;
- artwork;
- LevelData.

Never select class from width/height or colors.

Carry:
- source ChallengeScore digest/version;
- lane mapping policy version;
- predicted class;
- optional comparison to requested/descriptive class as a neutral mismatch/match observation only.

No “correcting” the board to fit a lane.

Tests: every threshold edge, score bounds, same score on different board sizes/colors => same predicted lane, no source mutation, deterministic serialization.

## Required repository gates

Focused task tests, affected predecessor M04 tests, retained M03 tests, full pytest green, compileall PASS, Godot headless editor boot PASS, git diff --check PASS and TASKS zero diff.

## Acceptance

PASS only when the task's metric/analysis semantics are versioned, deterministic, provenance-bound and do not overclaim unavailable gameplay truth.
