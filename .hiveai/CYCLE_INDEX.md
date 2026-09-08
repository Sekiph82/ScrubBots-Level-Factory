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

Cycle: `PAG-M00-C001`
Title: `Repository Bootstrap & Governance`
State: `READY_FOR_IMPLEMENTATION`
Actor: `CODEX`
