# ScrubBots Level Factory — H!veAI Handoff

## Current

Active cycle: `PAG-M05-C001`
Cycle title: `Wave Function Collapse Generator`
Workflow state: `READY_FOR_IMPLEMENTATION`
Required actor: `CODEX`
Authority repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`
Canonical implementation prompt: `.hiveai/prompts/PAG-M05-C001_WAVE_FUNCTION_COLLAPSE_GENERATOR_PROMPT.md`
Previous independent audit: `.hiveai/audits/PAG-M04-C002_GEOMETRY_FIDELITY_OPERATION_SEMANTICS_AND_RECIPE_DIVERSITY_REMEDIATION_STRICT_AUDIT.md`
Expected Codex log: `.hiveai/codex-logs/PAG-M05-C001_WAVE_FUNCTION_COLLAPSE_GENERATOR_CODEX_LOG.md`
Canonical task ledger: `tasks.md`

## Current milestone

`PAG-M04 — Procedural Shape / Rule Generator` = `FUNCTIONAL PASS / PERFORMANCE GATE DEFERRED`.

`PAG-M05 — Wave Function Collapse Generator` = `ACTIVE`.

## M04 forward dependency

`PAG-0441` remains `[!] BLOCKED` until M10 establishes the V1 performance budget.

This does not block M05.

## Next

Codex must read the M05-C001 authoritative prompt directly from GitHub, create the matching builder log before any edit, implement only the deterministic offline WFC milestone, use synthetic test-only exemplars plus an empty owner exemplar inbox, generate golden/review evidence, run the acceptance matrix and 59×59 benchmarks, publish implementation and log, and stop.

After publication, ChatGPT performs the independent strict audit and review.

PAG-M06+ remains blocked until M05 receives an unconditional independent PASS.

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
- `PAG-M04-C001` = `AUDIT_FAILED / REMEDIATED_BY_C002`
- `PAG-M04-C002` = `AUDIT_PASSED / FUNCTIONAL_SCOPE_COMPLETE`

## Authority

GitHub repository `Sekiph82/ScrubBots-Level-Factory` is the sole prompt/audit/task authority. `tasks.md` remains canonical task truth.
