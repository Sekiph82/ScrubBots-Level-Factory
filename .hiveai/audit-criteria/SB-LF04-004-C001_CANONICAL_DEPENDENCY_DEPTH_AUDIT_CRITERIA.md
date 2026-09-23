# SB-LF04-004-C001 — Canonical Dependency Depth — Strict Audit Criteria

Target:
`SB-LF04-004`

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

Dependency depth may exist only when supplied by an explicit canonical dependency-semantics provider tied to the accepted ScrubBots gameplay authority.

M03 solver path depth is NOT automatically dependency depth.

Do not infer dependency edges from:
- color adjacency;
- image regions;
- WFC constraints;
- move order alone;
- board dimensions;
- heuristic causal guesses.

Implement a versioned DependencyMetricProvider interface/result with AVAILABLE / UNAVAILABLE / ERROR and exact authority/state/evidence binding.

If no canonical dependency semantics are executable in current main-game authority, production behavior must remain UNAVAILABLE and LevelMetrics.dependency_depth stays absent.

Fixture-only providers may prove contract validation.

If a real canonical provider is established, dependency_depth must be an exact non-negative integer with deterministic repeat evidence.

PASS is allowed with truthful production UNAVAILABLE plus complete interface/tests; fabricated dependency depth is a blocker.

## Required repository gates

Focused task tests, affected predecessor M04 tests, retained M03 tests, full pytest green, compileall PASS, Godot headless editor boot PASS, git diff --check PASS and TASKS zero diff.

## Acceptance

PASS only when the task's metric/analysis semantics are versioned, deterministic, provenance-bound and do not overclaim unavailable gameplay truth.
