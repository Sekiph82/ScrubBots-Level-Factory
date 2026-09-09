# ScrubBots Level Factory — H!veAI Handoff

## Current

Active cycle: `PAG-M03-C002`
Cycle title: `Reproducibility, Region Quality & Recognizability Remediation`
Workflow state: `READY_FOR_IMPLEMENTATION`
Required actor: `CODEX`
Authority repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`
Canonical remediation prompt: `.hiveai/prompts/PAG-M03-C002_REPRODUCIBILITY_REGION_QUALITY_AND_RECOGNIZABILITY_REMEDIATION_PROMPT.md`
Previous independent audit: `.hiveai/audits/PAG-M03-C001_MASK_SPRITE_GENERATOR_STRICT_AUDIT.md`
Expected Codex log: `.hiveai/codex-logs/PAG-M03-C002_REPRODUCIBILITY_REGION_QUALITY_AND_RECOGNIZABILITY_REMEDIATION_CODEX_LOG.md`
Canonical task ledger: `tasks.md`

## Current findings

- `F-PAG-M03-C001-001` — BLOCKER — non-root supplied RNG can pass coherence while driving different executable streams than provenance.
- `F-PAG-M03-C001-002` — MAJOR — default colorization produces single-pixel salt / fragmented regions.
- `F-PAG-M03-C001-003` — MAJOR — semantic outline/body/detail roles are absent.
- `F-PAG-M03-C001-004` — MAJOR — manual review evidence is not sufficiently recognizable/distinct.

Open/revalidation task IDs:

- `PAG-0328`
- `PAG-0329`
- `PAG-0330`
- `PAG-0334`
- `PAG-0335`
- `PAG-0336`

## Next

Codex must read the C002 remediation prompt directly from GitHub, fix only the four audited findings, preserve validated M03 infrastructure, regenerate M03 goldens/review evidence, rerun the >=120 acceptance batch and full regression, publish the matching builder log, and stop.

After publication, ChatGPT performs the independent strict re-audit and manual review.

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
- `PAG-M03-C001` = `AUDIT_FAILED / FIX_REQUIRED`

## Authority

GitHub repository `Sekiph82/ScrubBots-Level-Factory` is the sole prompt/audit/task authority. `tasks.md` remains canonical task truth.
