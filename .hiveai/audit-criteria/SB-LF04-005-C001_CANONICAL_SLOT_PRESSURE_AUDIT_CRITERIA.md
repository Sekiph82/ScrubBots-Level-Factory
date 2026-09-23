# SB-LF04-005-C001 — Canonical Slot Pressure — Strict Audit Criteria

Target:
`SB-LF04-005`

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

## Truth rule

Slot pressure must be derived only from canonical gameplay slot-state observations, never from artwork, colors or guessed capacity.

Canonical slot count is five under current accepted ProofState authority.

Define a versioned SlotPressure provider/metric.

If canonical trace state snapshots are available, the recommended V1 diagnostic is:
- occupancy ratio for each observed canonical state = occupied slot count / canonical slot capacity;
- slot_pressure = maximum observed occupancy ratio across the accepted trace.

It must be finite in [0,1].

If the accepted evidence does not contain or cannot canonically retrieve the required slot snapshots without reimplementing gameplay, leave slot_pressure absent and production provider UNAVAILABLE.

Do not derive occupied slots from rendered pixels or Factory heuristics.

Tests must cover 0%, partial, 100%, deterministic max, malformed capacity/state, authority mismatch, and truthful unavailable.

## Required repository gates

Focused task tests, affected predecessor M04 tests, retained M03 tests, full pytest green, compileall PASS, Godot headless editor boot PASS, git diff --check PASS and TASKS zero diff.

## Acceptance

PASS only when the task's metric/analysis semantics are versioned, deterministic, provenance-bound and do not overclaim unavailable gameplay truth.
