# SB-LF05-002-C001 — Audited M09 Art-First Round-Trip Reuse — Strict Audit Criteria

Target:
`SB-LF05-002`

Prerequisites:
- M03 Puzzle Intelligence COMPLETE / VERIFIED.
- M04 Difficulty Intelligence COMPLETE / VERIFIED.
- SB-LF05-006 actionable rejection reasons PASS/CLOSED.
- SB-LF05-009 semantic recognizability/readability gate PASS/CLOSED.

Global rules:
- root TASKS.md is ChatGPT-owned;
- canonical gameplay/data acceptance truth remains in Sekiph82/Scrubbots;
- no Python clone of main-game validation/gameplay rules;
- no board-size/color-count difficulty inference;
- no source/art/LevelData mutation during QA;
- no structural metric may fabricate recognizability;
- operational timeout is non-canonical;
- missing evidence remains UNAVAILABLE/INCONCLUSIVE, never fabricated PASS;
- no network/provider credits merely for tests.

## Task contract

Reuse the audited main-game M09 exact-pixel round-trip contract for FINAL LOGICAL LEVEL_ART exports.

Do not rewrite the importer algorithm in Factory.

Required proof:
- one final logical PNG pixel = one logical cell;
- no resize/resample/interpolation;
- exact row-major pixel/palette/cell identity survives PNG -> LevelData -> reconstructed image;
- source logical PNG bytes/pixels are never mutated;
- round-trip evidence binds exact main-game importer/source authority and artifact SHA.

Important: M09 historical difficulty-band behavior is NOT current Difficulty V1 truth. Round-trip reuse must not reintroduce class=dimension or per-class color-count rules. Production legality is owned by SB-LF05-001/003.

A capability-gated main-game M09 round-trip provider is preferred. If capability is absent, report UNAVAILABLE rather than duplicating the algorithm.

Tests: exact round-trip, rectangular logical art, repeated colors/palette ordering, off-path source mutation check, authority drift, capability unavailable, no legacy difficulty inference.

## Required gates

Focused task tests; affected predecessor M05 tests; all M03/M04 retained tests; relevant owner-upload/semantic-quality/Factory Studio tests; full repository pytest green; compileall PASS; Godot headless editor boot PASS; git diff --check PASS; git diff --exit-code -- TASKS.md PASS.

For cross-repo main-game capability tests, use an independent clean exact-SHA checkout without modifying the owner's primary ScrubBots working tree. Legitimate capability absence may skip only tests whose contract explicitly permits it.

## Acceptance

PASS only when QA truth is versioned, provenance-bound, non-mutating, and does not bypass main-game acceptance authority.
