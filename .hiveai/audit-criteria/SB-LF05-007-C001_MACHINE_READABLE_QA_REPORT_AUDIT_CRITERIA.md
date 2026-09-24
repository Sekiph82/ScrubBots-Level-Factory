# SB-LF05-007-C001 — Machine-Readable QA Report — Strict Audit Criteria

Target:
`SB-LF05-007`

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

Create a closed immutable versioned QA report that composes accepted M05 stages and retained SB-LF05-006 actionable reasons / SB-LF05-009 recognizability evidence.

Report must bind:
- exact source/LevelData/logical-art identities;
- main-game validation authority/result identities;
- production contract facts;
- M03 solver disposition/evidence digest;
- M04 DifficultyAnalysis/score/lane digest where available;
- semantic recognizability assessment/review evidence;
- actionable rejection/retry reasons with stable codes;
- overall QA disposition.

Overall disposition must be derived from stage truth, not caller-supplied independently.

Structural diagnostics must never fabricate recognizability. UNREVIEWED recognizability must not become semantic ACCEPT.

Closed JSON parser, canonical bytes/digest, no timestamps/paths/secrets/operational timeout in canonical identity.

Tests: accepted case, structural reject, proven-unsolvable reject, solver inconclusive, semantic reject, semantic unreviewed, missing evidence, tamper/cross-lineage, unknown fields, deterministic round-trip.

## Required gates

Focused task tests; affected predecessor M05 tests; all M03/M04 retained tests; relevant owner-upload/semantic-quality/Factory Studio tests; full repository pytest green; compileall PASS; Godot headless editor boot PASS; git diff --check PASS; git diff --exit-code -- TASKS.md PASS.

For cross-repo main-game capability tests, use an independent clean exact-SHA checkout without modifying the owner's primary ScrubBots working tree. Legitimate capability absence may skip only tests whose contract explicitly permits it.

## Acceptance

PASS only when QA truth is versioned, provenance-bound, non-mutating, and does not bypass main-game acceptance authority.
