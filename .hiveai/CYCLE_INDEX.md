# ScrubBots Level Factory — H!veAI Cycle Index

This is the cycle history/index for implementation prompts, builder logs, and independent audits.

## Naming contract

Every cycle uses one shared identity and title across all three records.

Example cycle identity:

`PAG-M00-C001 — Repository Bootstrap & Governance`

Matching files:

- Prompt: `.hiveai/prompts/PAG-M00-C001_REPOSITORY_BOOTSTRAP_AND_GOVERNANCE_PROMPT.md`
- Codex log: `.hiveai/codex-logs/PAG-M00-C001_REPOSITORY_BOOTSTRAP_AND_GOVERNANCE_CODEX_LOG.md`
- Audit: `.hiveai/audits/PAG-M00-C001_REPOSITORY_BOOTSTRAP_AND_GOVERNANCE_STRICT_AUDIT.md`

All three files must use the exact same H1 title:

`# PAG-M00-C001 — Repository Bootstrap & Governance`

Document role is declared below the H1, not by changing the cycle title.

## Workflow states

`PROMPT_REQUIRED`
→ `PROMPT_READY`
→ `READY_FOR_IMPLEMENTATION`
→ `CODEX_RUNNING`
→ `IMPLEMENTATION_COMPLETE`
→ `AUDIT_REQUIRED`
→ `GPT_AUDIT_RUNNING`
→ `AUDIT_PASSED` or `AUDIT_FAILED`
→ `TASK_COMPLETE` or `FIX_REQUIRED`
→ remediation `PROMPT_READY` when necessary.

Only ChatGPT may author independent audit verdicts or move audited task/tracker state.

## Historical immutability

Once a prompt has been used, a Codex log has been submitted, or an audit has been issued, that record is historical evidence and must not be rewritten to hide failures or make prior claims match later reality.

A correction gets a new cycle ID, for example:

- `PAG-M00-C001` initial implementation
- `PAG-M00-C002` bounded remediation

## Active cycle

Cycle: `PAG-M02-C002`
Title: `Result Integrity & Provenance Remediation`
State: `READY_FOR_IMPLEMENTATION`
Actor: `CODEX`

## Failed / remediation-required cycles

### PAG-M02-C001 — Deterministic Generation Core
State: `AUDIT_FAILED / FIX_REQUIRED`
Audit: `.hiveai/audits/PAG-M02-C001_DETERMINISTIC_GENERATION_CORE_STRICT_AUDIT.md`
Open findings: `F-PAG-M02-C001-001`, `F-PAG-M02-C001-002`, `F-PAG-M02-C001-003`
Terminal builder-era HEAD independently observed: `e5274894725209834849b59d43be9999b2f31f9a`


### PAG-M00-C002 — Repository Bootstrap & Governance
State: `AUDIT_FAILED / REMEDIATED_BY_PAG-M00-C003`
Audit: `.hiveai/audits/PAG-M00-C002_REPOSITORY_BOOTSTRAP_AND_GOVERNANCE_STRICT_AUDIT.md`
Open findings: `F-PAG-M00-C002-001`, `F-PAG-M00-C002-002`

## Closed cycles

### PAG-M01-C001 — Canonical SCRUBBOTS Contracts
State: `AUDIT_PASSED / TASK_COMPLETE`
Audit: `.hiveai/audits/PAG-M01-C001_CANONICAL_SCRUBBOTS_CONTRACTS_STRICT_AUDIT.md`
Closes milestone: `PAG-M01 — Canonical SCRUBBOTS Contracts`
Terminal builder-era HEAD independently observed: `41601910c133f42753272877ad648db098ff7306`


### PAG-M00-C003 — Bootstrap Reliability & Offline Enforcement Remediation
State: `AUDIT_PASSED / TASK_COMPLETE`
Audit: `.hiveai/audits/PAG-M00-C003_BOOTSTRAP_RELIABILITY_AND_OFFLINE_ENFORCEMENT_REMEDIATION_STRICT_AUDIT.md`
Closes milestone: `PAG-M00 — Repository Bootstrap & Governance`


### RECOVERY-R001 — Revert Mistaken ScrubBots Local Edits
State: `AUDIT_PASSED / TASK_COMPLETE`
Audit: `.hiveai/audits/RECOVERY-R001_REVERT_MISTAKEN_SCRUBBOTS_LOCAL_EDITS_STRICT_AUDIT.md`

## Superseded cycles

### PAG-M00-C001 — Repository Bootstrap & Governance
State: `ABORTED_BEFORE_IMPLEMENTATION / SUPERSEDED`
Reason: initial handoff allowed wrong local-repository discovery; no PAG-M00 implementation was accepted from this cycle.
