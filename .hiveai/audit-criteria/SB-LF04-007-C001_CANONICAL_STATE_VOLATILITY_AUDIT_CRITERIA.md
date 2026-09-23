# SB-LF04-007-C001 — Canonical State Volatility — Strict Audit Criteria

Target: SB-LF04-007

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

Add one versioned gameplay-state volatility diagnostic only if ordered canonical trace quantities are available. Do not use pixel/art fragmentation. Recommended V1: a closed normalized signature from canonical remaining-active-cell count, supply remaining count, occupied-slot count or similarly already-exposed canonical quantities; transition delta is normalized absolute change; volatility is mean transition delta in [0,1]. Exact fields/normalizers/formula must be versioned. If trace data is unavailable without gameplay emulation, production remains UNAVAILABLE. Tests: stable trace=0, changing trace, bounds, one-state absent, malformed/unavailable and determinism.

## Required gates

Run focused task tests, affected earlier-M04 tests, retained M03 tests, relevant production/difficulty tests, full python -m pytest -q with zero failures, python -m compileall -q src tests, Level Factory Godot headless editor boot, git diff --check and git diff --exit-code -- TASKS.md.

## Acceptance

PASS only when semantics are versioned, deterministic, provenance-bound, honest about unavailable canonical data and do not preempt later task semantics.
