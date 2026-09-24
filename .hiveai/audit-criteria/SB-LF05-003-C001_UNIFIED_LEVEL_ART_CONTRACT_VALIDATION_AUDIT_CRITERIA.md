# SB-LF05-003-C001 — Unified Level Art Contract Validation — Strict Audit Criteria

Target:
`SB-LF05-003`

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

Validate the complete accepted LEVEL_ART contract without mutating source.

For final gameplay LEVEL_ART require:
- exact production dimensions 20..59 per axis;
- cells count = width*height;
- C01..C16 only;
- actual used-color count 3..12;
- canonical cell/palette indexing;
- no foreign logical colors;
- no semi-alpha;
- final logical gameplay cells opaque;
- exact provenance chain from source/raw -> compiler/artifact -> LevelData;
- duplicate level IDs rejected against the supplied QA/catalog/batch context.

Distinguish source-image alpha from final LEVEL_ART: immutable OWNER_UPLOAD/raw semantic source may contain transparency, but that never makes transparent/semi-alpha logical gameplay cells legal.

Do not apply class-specific dimension or color-count bands.

Do not silently palette-snap, resize, recolor, repair or rename during validation. Validation reports facts/reasons only.

Tests: 20x59/59x20 legal, 19/60 illegal, 2 and 13 used colors illegal, off-palette, semi-alpha, transparent final cell, bad cell count/index, stale provenance, duplicate ID, unchanged bytes.

## Required gates

Focused task tests; affected predecessor M05 tests; all M03/M04 retained tests; relevant owner-upload/semantic-quality/Factory Studio tests; full repository pytest green; compileall PASS; Godot headless editor boot PASS; git diff --check PASS; git diff --exit-code -- TASKS.md PASS.

For cross-repo main-game capability tests, use an independent clean exact-SHA checkout without modifying the owner's primary ScrubBots working tree. Legitimate capability absence may skip only tests whose contract explicitly permits it.

## Acceptance

PASS only when QA truth is versioned, provenance-bound, non-mutating, and does not bypass main-game acceptance authority.
