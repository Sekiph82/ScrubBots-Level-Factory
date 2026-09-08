# ScrubBots Level Factory — H!veAI Handoff

## Current

Active cycle: `PAG-M00-C002`
Cycle title: `Repository Bootstrap & Governance`
Workflow state: `READY_FOR_IMPLEMENTATION`
Required actor: `CODEX`
Authority repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`
Canonical implementation prompt: `.hiveai/prompts/PAG-M00-C002_REPOSITORY_BOOTSTRAP_AND_GOVERNANCE_PROMPT.md`
Previous independent audit: `.hiveai/audits/RECOVERY-R001_REVERT_MISTAKEN_SCRUBBOTS_LOCAL_EDITS_STRICT_AUDIT.md`
Expected Codex log: `.hiveai/codex-logs/PAG-M00-C002_REPOSITORY_BOOTSTRAP_AND_GOVERNANCE_CODEX_LOG.md`
Canonical task ledger: `tasks.md`

## Next

Codex must use GitHub as the sole task authority, read the full authoritative prompt from GitHub, synchronize the Level Factory mirror only if the prompt requires it, implement only PAG-M00-C002, run required tests, create the matching Codex builder log, commit and push.

After Codex completion, ChatGPT performs the independent strict audit. Codex must not audit or close tracker/task state.

## Completed recovery

`RECOVERY-R001 — Revert Mistaken ScrubBots Local Edits` = `AUDIT_PASSED / CLOSED`.

## Blockers

None currently known.

## Waiting

Waiting for Codex implementation of `PAG-M00-C002`.

## Authority

This handoff is operational state only. `tasks.md` remains canonical task authority. GitHub repository `Sekiph82/ScrubBots-Level-Factory` is the sole prompt/audit/task authority.
