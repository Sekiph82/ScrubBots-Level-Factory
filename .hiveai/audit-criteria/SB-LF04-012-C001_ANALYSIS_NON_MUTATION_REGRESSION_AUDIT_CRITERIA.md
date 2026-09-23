# SB-LF04-012-C001 — Analysis Non-Mutation / M04 Regression Closure — Strict Audit Criteria

Target: SB-LF04-012

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

Final M04 closure. Create a versioned declarative checksummed M04 regression corpus covering 001 contract, 002 witness depth/moves, 003 complexity/forced metrics, 004 dependency provider available/unavailable contract, 005 slot pressure contract, 006 bait/deadlock exact/inconclusive contract, 007 volatility contract, 008 known Challenge Score values, 009 threshold mapping, 010 provenance cross-binding rejection, 011 calibration disabled state. Prove representative analysis runs preserve exact pre/post bytes/SHA of Level Data source, art/logical source fixture, and canonical ScrubBots checkout files/status where bridge is used. No recolor/resize/palette/source mutation or network write. Full M04, retained M03, production/difficulty, full pytest, compileall, Godot, real bridge where configured, diff-check and TASKS no-diff must be green.

## Required gates

Run focused task tests, affected earlier-M04 tests, retained M03 tests, relevant production/difficulty tests, full python -m pytest -q with zero failures, python -m compileall -q src tests, Level Factory Godot headless editor boot, git diff --check and git diff --exit-code -- TASKS.md.

## Acceptance

PASS only when semantics are versioned, deterministic, provenance-bound, honest about unavailable canonical data and do not preempt later task semantics.
