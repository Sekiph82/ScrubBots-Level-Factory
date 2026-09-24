# SB-LF05-001-C001 — Unified Structural / Production / Difficulty Validation — Strict Audit Criteria

Target:
`SB-LF05-001`

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

Compose one versioned M05 QA entry point over already accepted authorities. It must not invent a parallel validator.

Required stages:
1. exact Level Data V1 source identity;
2. structural validity against current main-game LevelValidator semantics;
3. production legality against current main-game ProductionLevelValidator semantics;
4. Factory production-envelope/palette lineage consistency where already accepted;
5. Difficulty V1 analysis from accepted M04 LevelMetrics/ChallengeScore/Lane artifacts.

Use a capability-gated external main-game validation provider or equivalent exact-source execution against a clean exact-SHA Scrubbots checkout. Do not port LevelValidator/ProductionLevelValidator logic into Python.

The current production truth is width/height 20..59 independently, rectangular legal, difficulty not derived from dimensions or used-color count. Do not resurrect retired class-size or class-color bands.

Return a closed stage-by-stage disposition model, not a single bool. Structural/production/difficulty evidence must each carry exact authority/version/digest.

Tests: structurally invalid; TEST/unknown production difficulty; legal rectangular board; same legal dimensions under different descriptive classes; M04 analysis mismatch; authority/source drift; capability unavailable; deterministic serialization.

## Required gates

Focused task tests; affected predecessor M05 tests; all M03/M04 retained tests; relevant owner-upload/semantic-quality/Factory Studio tests; full repository pytest green; compileall PASS; Godot headless editor boot PASS; git diff --check PASS; git diff --exit-code -- TASKS.md PASS.

For cross-repo main-game capability tests, use an independent clean exact-SHA checkout without modifying the owner's primary ScrubBots working tree. Legitimate capability absence may skip only tests whose contract explicitly permits it.

## Acceptance

PASS only when QA truth is versioned, provenance-bound, non-mutating, and does not bypass main-game acceptance authority.
