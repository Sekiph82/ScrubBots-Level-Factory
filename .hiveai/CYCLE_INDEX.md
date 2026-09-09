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

Cycle: `PAG-M04-C002`
Title: `Geometry Fidelity, Operation Semantics & Recipe Diversity Remediation`
State: `READY_FOR_IMPLEMENTATION`
Actor: `CODEX`

## Failed / remediation-required cycles

### PAG-M04-C001 — Procedural Shape / Rule Generator
State: `AUDIT_FAILED / FIX_REQUIRED`
Audit: `.hiveai/audits/PAG-M04-C001_PROCEDURAL_SHAPE_RULE_GENERATOR_STRICT_AUDIT.md`
Open findings: `F-PAG-M04-C001-001`, `F-PAG-M04-C001-002`, `F-PAG-M04-C001-003`, `F-PAG-M04-C001-004`, `F-PAG-M04-C001-005`
Forward dependency: `PAG-0441` blocked on M10 performance budget
Terminal builder-era HEAD independently observed: `315233b77211d4771832b1732d9f9e52af66364a`


### PAG-M03-C002 — Reproducibility, Region Quality & Recognizability Remediation
State: `AUDIT_FAILED / REMEDIATED_BY_PAG-M03-C003`
Audit: `.hiveai/audits/PAG-M03-C002_REPRODUCIBILITY_REGION_QUALITY_AND_RECOGNIZABILITY_REMEDIATION_STRICT_AUDIT.md`
Closed findings: `F-PAG-M03-C001-001`, `F-PAG-M03-C001-002`
Open findings: `F-PAG-M03-C002-001`, `F-PAG-M03-C002-002`
Terminal builder-era HEAD independently observed: `9dc2eb7ae6620f655d21b6b2481a74c5783149dd`


### PAG-M03-C001 — Mask / Sprite Generator
State: `AUDIT_FAILED / PARTIALLY_REMEDIATED`
Audit: `.hiveai/audits/PAG-M03-C001_MASK_SPRITE_GENERATOR_STRICT_AUDIT.md`
Open findings: `F-PAG-M03-C001-001`, `F-PAG-M03-C001-002`, `F-PAG-M03-C001-003`, `F-PAG-M03-C001-004`
Terminal builder-era HEAD independently observed: `15363eb9d49d4e8791bfe0e038f9e83017c503fc`


### PAG-M02-C002 — Result Integrity & Provenance Remediation
State: `AUDIT_FAILED / REMEDIATED_BY_PAG-M02-C003`
Audit: `.hiveai/audits/PAG-M02-C002_RESULT_INTEGRITY_AND_PROVENANCE_REMEDIATION_STRICT_AUDIT.md`
Closed findings: `F-PAG-M02-C001-002`, `F-PAG-M02-C001-003`
Open finding: `F-PAG-M02-C002-001`
Terminal builder-era HEAD independently observed: `7ccbc1ad3209d0e2d3f4e03d4c19127a69b33ce6`


### PAG-M02-C001 — Deterministic Generation Core
State: `AUDIT_FAILED / PARTIALLY_REMEDIATED`
Audit: `.hiveai/audits/PAG-M02-C001_DETERMINISTIC_GENERATION_CORE_STRICT_AUDIT.md`
Open findings: `F-PAG-M02-C001-001`, `F-PAG-M02-C001-002`, `F-PAG-M02-C001-003`
Terminal builder-era HEAD independently observed: `e5274894725209834849b59d43be9999b2f31f9a`


### PAG-M00-C002 — Repository Bootstrap & Governance
State: `AUDIT_FAILED / REMEDIATED_BY_PAG-M00-C003`
Audit: `.hiveai/audits/PAG-M00-C002_REPOSITORY_BOOTSTRAP_AND_GOVERNANCE_STRICT_AUDIT.md`
Open findings: `F-PAG-M00-C002-001`, `F-PAG-M00-C002-002`

## Closed cycles

### PAG-M03-C003 — Semantic Role Binding & Weak-Family Recognizability Remediation
State: `AUDIT_PASSED / TASK_COMPLETE`
Audit: `.hiveai/audits/PAG-M03-C003_SEMANTIC_ROLE_BINDING_AND_WEAK_FAMILY_RECOGNIZABILITY_REMEDIATION_STRICT_AUDIT.md`
Closes milestone: `PAG-M03 — Mask / Sprite Generator`
Terminal builder-era HEAD independently observed: `1fda888a3a080cb4024d542c440f08d00ed393c1`


### PAG-M02-C003 — Result Construction Boundary Remediation
State: `AUDIT_PASSED / TASK_COMPLETE`
Audit: `.hiveai/audits/PAG-M02-C003_RESULT_CONSTRUCTION_BOUNDARY_REMEDIATION_STRICT_AUDIT.md`
Closes milestone: `PAG-M02 — Deterministic Generation Core`
Terminal builder-era HEAD independently observed: `4f0c803c7c4ab565700356735e6f665aeae7805b`


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
