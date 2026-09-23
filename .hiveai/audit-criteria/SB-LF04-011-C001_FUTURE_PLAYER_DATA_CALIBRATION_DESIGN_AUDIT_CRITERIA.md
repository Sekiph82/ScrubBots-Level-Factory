# SB-LF04-011-C001 — Future Player-Data Calibration Design — Strict Audit Criteria

Target:
`SB-LF04-011`

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

## Design-only task

No player analytics policy is currently approved by this task. Therefore this task must NOT add runtime data collection, telemetry upload, identifiers, network endpoints, SDKs or user profiling.

Produce a versioned future calibration design and disabled contract.

Required design:
- explicit state: DISABLED_UNTIL_POLICY_APPROVED;
- offline/import-only aggregate calibration dataset schema for future use;
- no names, emails, device IDs, account IDs, IPs, raw event streams or free-form PII fields;
- intended aggregate fields may include score-policy version, anonymous cohort label supplied by approved future process, completion/failure aggregates, move-count aggregates and sample count;
- minimum sample-count guard;
- versioned calibration algorithm interface/design;
- calibration must be able to create a future policy version, never silently alter Difficulty V1 in place;
- raw Difficulty V1 engineering score remains reproducible.

Document approval gates: privacy/analytics policy, product owner, security review, retention, consent/legitimate-basis as applicable.

Tests must prove current production path cannot enable calibration/network behavior and schema rejects forbidden identity fields.

## Required repository gates

Focused task tests, affected predecessor M04 tests, retained M03 tests, full pytest green, compileall PASS, Godot headless editor boot PASS, git diff --check PASS and TASKS zero diff.

## Acceptance

PASS only when the task's metric/analysis semantics are versioned, deterministic, provenance-bound and do not overclaim unavailable gameplay truth.
