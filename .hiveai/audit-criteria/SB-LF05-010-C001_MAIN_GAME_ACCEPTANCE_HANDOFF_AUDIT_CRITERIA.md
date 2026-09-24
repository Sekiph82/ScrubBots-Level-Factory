# SB-LF05-010-C001 — Main-Game Acceptance Handoff — Strict Audit Criteria

Target:
`SB-LF05-010`

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

Create an immutable validation-only handoff for Factory-accepted artifacts into the main ScrubBots acceptance chain. Do not bypass it and do not directly publish to the production catalog.

At execution time re-resolve current `Sekiph82/Scrubbots@main` authority.

Handoff package must bind:
- final LevelData bytes/hash;
- final logical-art PNG bytes/hash;
- source provenance hash;
- M05 QA report digest;
- M03 solver evidence digest;
- M04 difficulty analysis digest;
- semantic recognizability evidence digest;
- Factory schema/version;
- target main-game repository authority SHA.

Validate the package against current main-game LevelValidator + ProductionLevelValidator / accepted M09 art-first contract where applicable, using a clean exact-SHA checkout and validation-only execution.

Downstream truth:
- M30 is already closed gameplay win/lose/retry authority; Factory must not redefine it.
- M47 Android device testing is OPEN and cannot be claimed by Factory.
- M48 iOS readiness is OPEN and cannot be claimed by Factory.

Therefore Factory QA ACCEPT means “eligible for main-game acceptance handoff”, NOT “device/release accepted”.

Report downstream gates explicitly, e.g. M30_COMPATIBLE, M47_PENDING, M48_PENDING.

No cross-repo source mutation, no direct catalog overwrite, no production release claim.

Tests: valid handoff, QA not accepted, stale QA/art/LevelData hash, wrong main-game SHA, validator reject, clean checkout unchanged before/after, M47/M48 never fabricated as passed.

## Required gates

Focused task tests; affected predecessor M05 tests; all M03/M04 retained tests; relevant owner-upload/semantic-quality/Factory Studio tests; full repository pytest green; compileall PASS; Godot headless editor boot PASS; git diff --check PASS; git diff --exit-code -- TASKS.md PASS.

For cross-repo main-game capability tests, use an independent clean exact-SHA checkout without modifying the owner's primary ScrubBots working tree. Legitimate capability absence may skip only tests whose contract explicitly permits it.

## Acceptance

PASS only when QA truth is versioned, provenance-bound, non-mutating, and does not bypass main-game acceptance authority.
