# SB-LF05-010-C001 — Main-Game Acceptance Handoff

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch: main

Task:
`SB-LF05-010`

Audit criteria:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/SB-LF05-010-C001_MAIN_GAME_ACCEPTANCE_HANDOFF_AUDIT_CRITERIA.md

Builder log:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF05-010-C001_MAIN_GAME_ACCEPTANCE_HANDOFF_CODEX_LOG.md

Do not edit root TASKS.md.

Read first:
- root TASKS.md, AGENTS.md, GOVERNANCE.md;
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF03-M03_FINAL_CLOSURE_SUMMARY.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF04-M04_FINAL_CLOSURE_SUMMARY.md
- retained SB-LF05-006 and SB-LF05-009 evidence/contracts;
- exact task criteria;
- all earlier M05 task implementations in this batch.

## Mission

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

Implement only this task plus minimal compatibility plumbing. Do not preempt later M05 tasks.

Create the task builder log before product edits. Run every required gate. Publish implementation/tests/docs + builder log, then a terminal log-only commit. Continue only under the M05 master batch.
