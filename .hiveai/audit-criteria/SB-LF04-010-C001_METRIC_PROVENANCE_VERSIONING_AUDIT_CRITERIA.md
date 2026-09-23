# SB-LF04-010-C001 — Metric Provenance / Versioning — Strict Audit Criteria

Target:
`SB-LF04-010`

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

## Required provenance bundle

Create a closed immutable DifficultyAnalysis provenance/report envelope that binds:
- exact LevelData/source SHA;
- canonical gameplay authority;
- exact SolverEvidence identity/digest;
- LevelMetrics schema/version/digest;
- each populated metric family policy/provider version;
- ChallengeScore policy/version/digest if present;
- lane mapping policy/version/digest if present;
- analysis disposition/reason;
- exact component availability.

Do not copy operational elapsed time, timeout seconds, local paths, machine IDs or UI state into canonical provenance.

Do not allow a metric value without its producing version/source identity.

The bundle must detect mixed lineage, e.g. score from LevelMetrics A combined with lane result from score B.

Parsing is closed-schema and fails on unknown fields/version/digest mismatch.

Tests: valid round-trip, mismatched source/evidence/metrics/score/lane rejected, optional unavailable diagnostics represented truthfully, deterministic bytes, no operational telemetry.

## Required repository gates

Focused task tests, affected predecessor M04 tests, retained M03 tests, full pytest green, compileall PASS, Godot headless editor boot PASS, git diff --check PASS and TASKS zero diff.

## Acceptance

PASS only when the task's metric/analysis semantics are versioned, deterministic, provenance-bound and do not overclaim unavailable gameplay truth.
