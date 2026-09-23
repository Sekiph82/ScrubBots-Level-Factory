# SB-LF04-006-C001 — Canonical Bait / Deadlock Metrics — Strict Audit Criteria

Target: SB-LF04-006

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

Bait/deadlock requires canonical counterfactual proof. Never equate search dead_end_count with bait. Recommended exact V1 when executable: canonical legal moves -> canonical transition for each -> canonical solver child classification; proven_deadlock_move_count counts only children proven PROVEN_UNSOLVABLE; bait_deadlock ratio = proven_deadlock_move_count/legal_move_count. UNKNOWN_BOUND or INCONCLUSIVE children cannot be counted as proven deadlocks and prevent an EXACT claim when exactness is required. Use M03 providers/bridge only. If unavailable, leave absent. Tests: 0, partial, all deadlock, inconclusive child, unavailable, repeat determinism and authority binding.

## Required gates

Run focused task tests, affected earlier-M04 tests, retained M03 tests, relevant production/difficulty tests, full python -m pytest -q with zero failures, python -m compileall -q src tests, Level Factory Godot headless editor boot, git diff --check and git diff --exit-code -- TASKS.md.

## Acceptance

PASS only when semantics are versioned, deterministic, provenance-bound, honest about unavailable canonical data and do not preempt later task semantics.
