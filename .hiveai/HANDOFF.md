# ScrubBots Level Factory — H!veAI Handoff

## Current

Active cycle: `PAG-M03-C001`
Cycle title: `Mask / Sprite Generator`
Workflow state: `READY_FOR_IMPLEMENTATION`
Required actor: `CODEX`
Authority repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`
Canonical implementation prompt: `.hiveai/prompts/PAG-M03-C001_MASK_SPRITE_GENERATOR_PROMPT.md`
Previous independent audit: `.hiveai/audits/PAG-M02-C003_RESULT_CONSTRUCTION_BOUNDARY_REMEDIATION_STRICT_AUDIT.md`
Expected Codex log: `.hiveai/codex-logs/PAG-M03-C001_MASK_SPRITE_GENERATOR_CODEX_LOG.md`
Canonical task ledger: `tasks.md`

## Current milestone

`PAG-M02 — Deterministic Generation Core` = `PASS / CLOSED`.

`PAG-M03 — Mask / Sprite Generator` = `ACTIVE`.

## Hard process rule

The matching M03 builder log must exist **before the first source/product/review-artifact edit**.

Do not repeat `F-PAG-M02-C003-PROC-001`.

## Next

Codex must read the M03-C001 authoritative prompt directly from GitHub, implement only the MASK/Sprite milestone, create the matching builder log first, run focused/acceptance/golden/full regression evidence, generate the committed review manifest/contact sheet, publish implementation and log, and stop.

After publication, ChatGPT performs the independent strict audit and manual review of the committed M03 review evidence.

PAG-M04 remains blocked until M03 receives an unconditional independent PASS.

## Historical

- `RECOVERY-R001` = `AUDIT_PASSED / CLOSED`
- `PAG-M00-C001` = `ABORTED_BEFORE_IMPLEMENTATION / SUPERSEDED`
- `PAG-M00-C002` = `AUDIT_FAILED / REMEDIATED`
- `PAG-M00-C003` = `AUDIT_PASSED / TASK_COMPLETE`
- `PAG-M01-C001` = `AUDIT_PASSED / TASK_COMPLETE`
- `PAG-M02-C001` = `AUDIT_FAILED / PARTIALLY_REMEDIATED`
- `PAG-M02-C002` = `AUDIT_FAILED / REMEDIATED_BY_C003`
- `PAG-M02-C003` = `AUDIT_PASSED / TASK_COMPLETE`

## Authority

GitHub repository `Sekiph82/ScrubBots-Level-Factory` is the sole prompt/audit/task authority. `tasks.md` remains canonical task truth.
