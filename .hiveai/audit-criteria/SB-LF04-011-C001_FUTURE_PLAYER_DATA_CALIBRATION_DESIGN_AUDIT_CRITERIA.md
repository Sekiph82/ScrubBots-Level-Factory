# SB-LF04-011-C001 — Future Player-Data Calibration Design — Strict Audit Criteria

Target: SB-LF04-011

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

DESIGN/DISABLED ONLY. No analytics policy is approved here. Do not add telemetry upload, HTTP, SDKs, identifiers, profiling or runtime collection. Define state DISABLED_UNTIL_POLICY_APPROVED and a strict offline/import-only aggregate future CalibrationDataset/CalibrationPlan schema. Forbid names, emails, device/account IDs, IPs, raw event streams and free-form PII. Aggregate fields may include score-policy version, approved future anonymous cohort label, completion/failure aggregates, move-count aggregates and sample count. Require minimum sample count. Future calibration must create a new explicit policy version, never silently mutate Difficulty V1. Document privacy/product/security/retention/consent approval gates. Tests prove current production path cannot enable calibration/network behavior and forbidden identity fields are rejected.

## Required gates

Run focused task tests, affected earlier-M04 tests, retained M03 tests, relevant production/difficulty tests, full python -m pytest -q with zero failures, python -m compileall -q src tests, Level Factory Godot headless editor boot, git diff --check and git diff --exit-code -- TASKS.md.

## Acceptance

PASS only when semantics are versioned, deterministic, provenance-bound, honest about unavailable canonical data and do not preempt later task semantics.
