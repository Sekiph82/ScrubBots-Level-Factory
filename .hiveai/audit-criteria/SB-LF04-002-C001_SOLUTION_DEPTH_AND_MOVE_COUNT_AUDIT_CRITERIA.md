# SB-LF04-002-C001 — Solution Depth / Move Count — Strict Audit Criteria

Target:
`SB-LF04-002`

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

## Required semantics

Populate only the already-defined LevelMetrics slots:
- solution_depth
- move_count

Input must be an accepted AVAILABLE LevelMetrics envelope bound to the exact SolverEvidenceReport being consumed.

For an AVAILABLE + SOLVED deterministic search witness:
- move_count = number of canonical player LegalMove selections in the accepted solution path.
- solution_depth = edge depth of that same recorded witness.
- Under the current one-player-move-per-edge search these values are expected to be equal, but keep the fields semantically separate.

Do not call the witnessed path “shortest”, “optimal”, or “minimal” unless a future solver explicitly proves that property.

For PROVEN_UNSOLVABLE, INCONCLUSIVE, UNAVAILABLE, ERROR, or missing path evidence:
- do not fabricate zero;
- leave solution_depth/move_count absent;
- preserve truthful disposition/reason.

Requirements:
- exact solver evidence schema/version/digest match;
- exact LevelData and authority lineage retained;
- pure deterministic transformation;
- preserve all unrelated metric slots;
- no gameplay invocation, no source mutation, no wall-clock data.

Tests must cover solved witness, zero-move solved start, unsolvable/inconclusive/unavailable, evidence digest mismatch, repeat determinism, unrelated metric preservation, and no “shortest” claim.

## Required repository gates

Focused task tests, affected predecessor M04 tests, retained M03 tests, full pytest green, compileall PASS, Godot headless editor boot PASS, git diff --check PASS and TASKS zero diff.

## Acceptance

PASS only when the task's metric/analysis semantics are versioned, deterministic, provenance-bound and do not overclaim unavailable gameplay truth.
