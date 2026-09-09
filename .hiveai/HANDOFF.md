# ScrubBots Level Factory — H!veAI Handoff

## Current

Active cycle: `PAG-M04-C001`
Cycle title: `Procedural Shape / Rule Generator`
Workflow state: `READY_FOR_IMPLEMENTATION`
Required actor: `CODEX`
Authority repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`
Canonical implementation prompt: `.hiveai/prompts/PAG-M04-C001_PROCEDURAL_SHAPE_RULE_GENERATOR_PROMPT.md`
Previous independent audit: `.hiveai/audits/PAG-M03-C003_SEMANTIC_ROLE_BINDING_AND_WEAK_FAMILY_RECOGNIZABILITY_REMEDIATION_STRICT_AUDIT.md`
Expected Codex log: `.hiveai/codex-logs/PAG-M04-C001_PROCEDURAL_SHAPE_RULE_GENERATOR_CODEX_LOG.md`
Canonical task ledger: `tasks.md`

## Current milestone

`PAG-M03 — Mask / Sprite Generator` = `PASS / CLOSED`.

`PAG-M04 — Procedural Shape / Rule Generator` = `ACTIVE`.

## Forward performance dependency

`PAG-0441` references the V1 performance budget that will only be established in M10.

For M04:
- benchmark representative 59×59 RULES generation;
- record boundedness and timing evidence;
- do not invent a budget;
- do not mark PAG-0441 complete.

## Next

Codex must read the M04-C001 prompt directly from GitHub, create the matching builder log before any source/test/review edit, implement only the RULES generator milestone, publish primitive/recipe golden and review evidence, run the deterministic acceptance batch and full regression, benchmark 59×59 without inventing the M10 budget, publish implementation and log, and stop.

After publication, ChatGPT performs the independent strict audit and manual review.

PAG-M05+ remains blocked until the M04 implementation is independently accepted for its currently testable scope.

## Historical

- `RECOVERY-R001` = `AUDIT_PASSED / CLOSED`
- `PAG-M00-C001` = `ABORTED_BEFORE_IMPLEMENTATION / SUPERSEDED`
- `PAG-M00-C002` = `AUDIT_FAILED / REMEDIATED`
- `PAG-M00-C003` = `AUDIT_PASSED / TASK_COMPLETE`
- `PAG-M01-C001` = `AUDIT_PASSED / TASK_COMPLETE`
- `PAG-M02-C001` = `AUDIT_FAILED / PARTIALLY_REMEDIATED`
- `PAG-M02-C002` = `AUDIT_FAILED / REMEDIATED_BY_C003`
- `PAG-M02-C003` = `AUDIT_PASSED / TASK_COMPLETE`
- `PAG-M03-C001` = `AUDIT_FAILED / PARTIALLY_REMEDIATED`
- `PAG-M03-C002` = `AUDIT_FAILED / REMEDIATED_BY_C003`
- `PAG-M03-C003` = `AUDIT_PASSED / TASK_COMPLETE`

## Authority

GitHub repository `Sekiph82/ScrubBots-Level-Factory` is the sole prompt/audit/task authority. `tasks.md` remains canonical task truth.
