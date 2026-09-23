# SB-LF04-010-C001 — Metric Provenance / Versioning — Strict Audit Criteria

Target: SB-LF04-010

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

Create a closed immutable DifficultyAnalysis provenance envelope binding exact LevelData/source SHA, canonical gameplay authority, SolverEvidence identity/digest, LevelMetrics schema/version/digest, each populated metric provider/policy version, ChallengeScore digest/version if present, lane mapping digest/version if present, disposition/reason and exact component availability. Reject mixed lineage such as score from metrics A plus lane result from score B. No elapsed time, timeout seconds, local paths, machine IDs or UI state in canonical provenance. Optional unavailable diagnostics remain explicitly unavailable. Tests: valid round trip, every cross-binding mismatch, unknown fields/version, deterministic bytes and no operational telemetry.

## Required gates

Run focused task tests, affected earlier-M04 tests, retained M03 tests, relevant production/difficulty tests, full python -m pytest -q with zero failures, python -m compileall -q src tests, Level Factory Godot headless editor boot, git diff --check and git diff --exit-code -- TASKS.md.

## Acceptance

PASS only when semantics are versioned, deterministic, provenance-bound, honest about unavailable canonical data and do not preempt later task semantics.
