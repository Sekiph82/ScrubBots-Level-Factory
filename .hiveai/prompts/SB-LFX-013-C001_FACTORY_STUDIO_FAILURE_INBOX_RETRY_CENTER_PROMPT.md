# SB-LFX-013-C001 — Factory Studio Failure Inbox / Retry Center

Builder log:
`.hiveai/codex-logs/SB-LFX-013-C001_FAILURE_INBOX_RETRY_CENTER_CODEX_LOG.md`

Create log first. Work only on LFX-013.

Build a derived failure inbox over real batch/pipeline/validation/job evidence.

Define retry eligibility per real operation. Retry only eligible FAILED/REJECTED/INCONCLUSIVE work. Preserve original failure evidence forever and create a new retry attempt linked to it.

Reuse exact original canonical inputs/config unless the operator explicitly changes a field allowed by that operation, in which case record the change.

Never retry successful stages in “failed only” mode. Keep unavailable stages disabled with reason.

Real tests must prove multiple failure types, successful control item, lineage, retained failure evidence, no redo of successful work, duplicate safety and retry outcome recording.

No batch-import/recovery/similarity work. No TASKS edit.

Commit/push implementation then one task-final log-only commit; continue only under batch master.
