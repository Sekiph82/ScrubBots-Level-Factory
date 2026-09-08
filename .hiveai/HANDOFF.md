# ScrubBots Level Factory — H!veAI Handoff

## Current

Active cycle: `RECOVERY-R001`
Cycle title: `Revert Mistaken ScrubBots Local Edits`
Workflow state: `READY_FOR_IMPLEMENTATION`
Required actor: `CODEX`
Authority repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`
Canonical recovery prompt: `.hiveai/prompts/RECOVERY-R001_REVERT_MISTAKEN_SCRUBBOTS_LOCAL_EDITS_PROMPT.md`
Expected Codex log: `.hiveai/codex-logs/RECOVERY-R001_REVERT_MISTAKEN_SCRUBBOTS_LOCAL_EDITS_CODEX_LOG.md`

## Next

Codex must read the recovery prompt from GitHub, surgically revert only the mistaken local edits in the main ScrubBots worktree, preserve all pre-existing dirty changes, and push only the matching recovery log to this Level Factory repository.

After Codex completion, ChatGPT performs the independent recovery audit. PAG-M00-C001 remains paused until RECOVERY-R001 is accepted.

## Blockers

PAG-M00-C001 is paused pending successful independent verification of RECOVERY-R001.

## Waiting

Waiting for Codex recovery execution.

## Authority

This handoff is operational state only. `tasks.md` remains the canonical task ledger. ChatGPT is the sole tracker/audit authority.
