# SB-LF04-006-C001 — Canonical Bait / Deadlock Metrics — Strict Audit Criteria

Target:
`SB-LF04-006`

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

Bait/deadlock metrics require canonical counterfactual gameplay proof.

Do not treat every search dead end as a “bait move” and do not infer traps from artwork.

Define a versioned provider/result for counterfactual one-move analysis.

Recommended canonical V1 when executable:
- at a canonical state, enumerate legal player moves through accepted legal provider;
- apply each move through accepted canonical transition;
- solve/classify child through accepted canonical solver;
- proven_deadlock_move_count = number of legal moves whose child is PROVEN_UNSOLVABLE;
- bait_deadlock ratio = proven_deadlock_move_count / legal_move_count, in [0,1].

UNKNOWN_BOUND / INCONCLUSIVE children do not count as proven deadlock and must prevent an EXACT ratio claim if exactness is required.

If canonical counterfactual proof is unavailable, leave bait_deadlock absent.

All operations must use M03 providers/bridge. No second solver.

Tests: exact 0, partial, all deadlock, inconclusive child, unavailable provider, repeat determinism, authority binding.

## Required repository gates

Focused task tests, affected predecessor M04 tests, retained M03 tests, full pytest green, compileall PASS, Godot headless editor boot PASS, git diff --check PASS and TASKS zero diff.

## Acceptance

PASS only when the task's metric/analysis semantics are versioned, deterministic, provenance-bound and do not overclaim unavailable gameplay truth.
