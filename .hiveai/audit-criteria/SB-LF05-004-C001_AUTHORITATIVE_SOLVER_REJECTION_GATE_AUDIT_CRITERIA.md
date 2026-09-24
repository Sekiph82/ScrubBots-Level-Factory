# SB-LF05-004-C001 — Authoritative Solver Rejection Gate — Strict Audit Criteria

Target:
`SB-LF05-004`

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

Add a QA solver gate that consumes accepted M03 solver evidence only.

Rules:
- PROVEN_UNSOLVABLE from exact authoritative solver evidence => REJECT.
- SOLVED => solver gate PASS.
- INCONCLUSIVE/UNKNOWN_BOUND => never label UNSOLVABLE and never reject under the proven-unsolvable reason.
- UNAVAILABLE/ERROR => separate truthful dispositions.
- evidence authority/source/request/budget identity mismatch => ERROR/fail closed.

Do not run a second solver or infer unsolvability from dead ends, Challenge Score, WFC, visual structure or timeout.

The gate must preserve exact solver evidence digest and deterministic budget identity.

Tests: solved, proven-unsolvable, unknown-bound/inconclusive, operational timeout wrapper, unavailable, wrong authority/evidence, deterministic report.

## Required gates

Focused task tests; affected predecessor M05 tests; all M03/M04 retained tests; relevant owner-upload/semantic-quality/Factory Studio tests; full repository pytest green; compileall PASS; Godot headless editor boot PASS; git diff --check PASS; git diff --exit-code -- TASKS.md PASS.

For cross-repo main-game capability tests, use an independent clean exact-SHA checkout without modifying the owner's primary ScrubBots working tree. Legitimate capability absence may skip only tests whose contract explicitly permits it.

## Acceptance

PASS only when QA truth is versioned, provenance-bound, non-mutating, and does not bypass main-game acceptance authority.
