# ScrubBots Level Factory — H!veAI Handoff

## Current

Active cycle: `PAG-M05-C002`
Cycle title: `Exemplar Contract, Diagnostics & Acceptance Evidence Remediation`
Workflow state: `READY_FOR_IMPLEMENTATION`
Required actor: `CODEX`
Authority repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`
Canonical remediation prompt: `.hiveai/prompts/PAG-M05-C002_EXEMPLAR_CONTRACT_DIAGNOSTICS_AND_ACCEPTANCE_EVIDENCE_REMEDIATION_PROMPT.md`
Previous independent audit: `.hiveai/audits/PAG-M05-C001_WAVE_FUNCTION_COLLAPSE_GENERATOR_STRICT_AUDIT.md`
Expected Codex log: `.hiveai/codex-logs/PAG-M05-C002_EXEMPLAR_CONTRACT_DIAGNOSTICS_AND_ACCEPTANCE_EVIDENCE_REMEDIATION_CODEX_LOG.md`
Canonical task ledger: `tasks.md`

## Current findings

- `F-PAG-M05-C001-001` — MAJOR — production artifact exemplar dimensions are not validated through M01 difficulty bands.
- `F-PAG-M05-C001-002` — MAJOR — terminal contradiction/rejection diagnostics are discarded and adversarial retry evidence is missing.
- `F-PAG-M05-C001-003` — MAJOR — extracted pattern-count metadata is transform-expanded rather than raw-window truth.
- `F-PAG-M05-C001-004` — MAJOR — review/golden/rectangle acceptance evidence is incomplete.

Open/revalidation task IDs:
- `PAG-0515`
- `PAG-0524`
- `PAG-0530`
- `PAG-0533`

Cross-cutting review remediation:
- expand M05 review pack from 4 to >=12 accepted candidates;
- render exemplar motif beside generated output;
- add rectangular and 10-color golden evidence.

## Next

Codex must read the C002 remediation prompt directly from GitHub, fix only the four audited findings, preserve the validated WFC core, expand the acceptance/review/golden evidence, rerun >=120 acceptance candidates and full regression, refresh the benchmark, publish the matching builder log, and stop.

After publication, ChatGPT performs the independent strict re-audit.

PAG-M06+ remains blocked until M05 receives unconditional independent PASS.

## Existing forward dependency

`PAG-0441` remains blocked until M10 establishes the V1 performance budget.

## Historical

- `PAG-M04-C002` = `AUDIT_PASSED / FUNCTIONAL_SCOPE_COMPLETE`
- `PAG-M05-C001` = `AUDIT_FAILED / FIX_REQUIRED`

## Authority

GitHub repository `Sekiph82/ScrubBots-Level-Factory` is the sole prompt/audit/task authority.
