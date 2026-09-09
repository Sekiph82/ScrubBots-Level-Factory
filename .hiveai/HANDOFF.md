# ScrubBots Level Factory — H!veAI Handoff

## Current

Active cycle: `PAG-M04-C002`
Cycle title: `Geometry Fidelity, Operation Semantics & Recipe Diversity Remediation`
Workflow state: `READY_FOR_IMPLEMENTATION`
Required actor: `CODEX`
Authority repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`
Canonical remediation prompt: `.hiveai/prompts/PAG-M04-C002_GEOMETRY_FIDELITY_OPERATION_SEMANTICS_AND_RECIPE_DIVERSITY_REMEDIATION_PROMPT.md`
Previous independent audit: `.hiveai/audits/PAG-M04-C001_PROCEDURAL_SHAPE_RULE_GENERATOR_STRICT_AUDIT.md`
Expected Codex log: `.hiveai/codex-logs/PAG-M04-C002_GEOMETRY_FIDELITY_OPERATION_SEMANTICS_AND_RECIPE_DIVERSITY_REMEDIATION_CODEX_LOG.md`
Canonical task ledger: `tasks.md`

## Current findings

- `F-PAG-M04-C001-001` — BLOCKER — final coloring is not bound to RuleCanvas occupied/negative geometry.
- `F-PAG-M04-C001-002` — MAJOR — POCKET paints instead of carving.
- `F-PAG-M04-C001-003` — MAJOR — BRIDGE_GAP duplicates FILL_NOTCH behavior.
- `F-PAG-M04-C001-004` — MAJOR — protected occupied semantic labels can be overwritten.
- `F-PAG-M04-C001-005` — MAJOR — four recipes are seed-invariant at fixed dimensions.
- `F-PAG-M04-C001-PROC-001` — MINOR — primitive review singleton diagnostic is hardcoded.

Open/revalidation task IDs:

- `PAG-0405`
- `PAG-0421`
- `PAG-0425`
- `PAG-0426`
- `PAG-0428`
- `PAG-0430`
- `PAG-0431`
- `PAG-0433`
- `PAG-0437`
- `PAG-0438`
- `PAG-0439`
- `PAG-0440`
- `PAG-0442`

Blocked forward dependency:

- `PAG-0441` — M10 V1 performance budget not yet established.

## Next

Codex must read the C002 remediation prompt directly from GitHub, fix only the audited M04 semantic/diversity findings, preserve validated M04 infrastructure, regenerate affected goldens/review evidence, rerun the 140-candidate acceptance matrix and full regression, refresh 59×59 benchmark evidence without inventing a budget, publish the matching builder log, and stop.

After publication, ChatGPT performs the independent strict re-audit and manual review.

PAG-M05+ remains blocked until M04 receives independent acceptance for its currently testable scope.

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
- `PAG-M04-C001` = `AUDIT_FAILED / FIX_REQUIRED`

## Authority

GitHub repository `Sekiph82/ScrubBots-Level-Factory` is the sole prompt/audit/task authority. `tasks.md` remains canonical task truth.
