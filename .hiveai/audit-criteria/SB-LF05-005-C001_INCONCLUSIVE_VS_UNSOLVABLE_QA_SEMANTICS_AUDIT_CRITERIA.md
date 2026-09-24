# SB-LF05-005-C001 — INCONCLUSIVE vs UNSOLVABLE QA Semantics — Strict Audit Criteria

Target:
`SB-LF05-005`

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

Define the closed QA outcome semantics that keep solver uncertainty distinct from proof.

At minimum distinguish:
- ACCEPTABLE_SOLVER_PROOF / SOLVED;
- REJECT_PROVEN_UNSOLVABLE;
- INCONCLUSIVE_REVIEW_OR_RETRY_REQUIRED;
- UNAVAILABLE;
- ERROR.

An INCONCLUSIVE candidate may be queued for retry/review according to later policy, but it must not be counted as a proven-unsolvable rejection.

QA rejection statistics/reasons must preserve this distinction.

Wall-clock timeout remains operational-only and must not become canonical unsolvability.

Tests must prove no code path maps UNKNOWN_BOUND/INCONCLUSIVE/timeout-before-result to PROVEN_UNSOLVABLE.

## Required gates

Focused task tests; affected predecessor M05 tests; all M03/M04 retained tests; relevant owner-upload/semantic-quality/Factory Studio tests; full repository pytest green; compileall PASS; Godot headless editor boot PASS; git diff --check PASS; git diff --exit-code -- TASKS.md PASS.

For cross-repo main-game capability tests, use an independent clean exact-SHA checkout without modifying the owner's primary ScrubBots working tree. Legitimate capability absence may skip only tests whose contract explicitly permits it.

## Acceptance

PASS only when QA truth is versioned, provenance-bound, non-mutating, and does not bypass main-game acceptance authority.
