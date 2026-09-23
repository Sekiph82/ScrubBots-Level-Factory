# SB-LF04-005-C001 — Canonical Slot Pressure — Strict Audit Criteria

Target: SB-LF04-005

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

Slot pressure must use canonical gameplay slot-state observations only. Recommended V1 if canonical trace snapshots are safely available: per-state occupancy ratio = occupied canonical slots / canonical capacity, slot_pressure = maximum observed ratio, finite [0,1]. If trace snapshots cannot be retrieved without gameplay emulation, production remains UNAVAILABLE and slot_pressure absent. Never infer from art/colors. Tests cover empty/partial/full occupancy, deterministic max, malformed capacity/state, authority mismatch and unavailable behavior.

## Required gates

Run focused task tests, affected earlier-M04 tests, retained M03 tests, relevant production/difficulty tests, full python -m pytest -q with zero failures, python -m compileall -q src tests, Level Factory Godot headless editor boot, git diff --check and git diff --exit-code -- TASKS.md.

## Acceptance

PASS only when semantics are versioned, deterministic, provenance-bound, honest about unavailable canonical data and do not preempt later task semantics.
