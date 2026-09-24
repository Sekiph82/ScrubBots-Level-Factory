# SB-LF05-008-C001 — Owner Source Byte Preservation QA — Strict Audit Criteria

Target:
`SB-LF05-008`

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

Integrate immutable OWNER_UPLOAD/source-library truth into Unified QA.

Requirements:
- owner source bytes remain byte-for-byte unchanged before/after every validation/analysis path;
- source SHA/length/dimensions must match the immutable source record;
- derived logical art/LevelData/preview/report are separate artifacts and paths;
- no normalized/quantized/resized output may overwrite or masquerade as OWNER_UPLOAD source;
- stale/corrupt/missing source record or bytes fail closed;
- repeated QA is idempotent and produces no meaningless source diff.

Reuse accepted owner_upload/source-library contracts. Do not invent a second source store.

Tests: pre/post exact bytes/SHA, re-run idempotence, corrupt source bytes, corrupt record, derived output separation, source filename/path metadata cannot override content identity.

## Required gates

Focused task tests; affected predecessor M05 tests; all M03/M04 retained tests; relevant owner-upload/semantic-quality/Factory Studio tests; full repository pytest green; compileall PASS; Godot headless editor boot PASS; git diff --check PASS; git diff --exit-code -- TASKS.md PASS.

For cross-repo main-game capability tests, use an independent clean exact-SHA checkout without modifying the owner's primary ScrubBots working tree. Legitimate capability absence may skip only tests whose contract explicitly permits it.

## Acceptance

PASS only when QA truth is versioned, provenance-bound, non-mutating, and does not bypass main-game acceptance authority.
