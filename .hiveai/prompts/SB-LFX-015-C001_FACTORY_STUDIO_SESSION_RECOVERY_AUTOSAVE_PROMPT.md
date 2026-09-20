# SB-LFX-015-C001 — Factory Studio Session Recovery / Autosave

Builder log:
`.hiveai/codex-logs/SB-LFX-015-C001_SESSION_RECOVERY_AUTOSAVE_CODEX_LOG.md`

Create log first. Work only on LFX-015.

Add a versioned session/autosave record containing references and UI continuity only, never copied canonical source/candidate truth or secrets.

On restore, revalidate every referenced source/candidate/batch/pipeline/revision record.

Implement explicit recovery labels:
RESUMED / RETRIED / NEW / NOT_RESUMABLE / NEEDS_OPERATOR_ACTION.

Do not redo successful durable stages. Resume only operations whose contracts safely support resume; otherwise require operator action.

Add a real restart/interruption integration using existing pipeline/batch import work. Prove completed stages are reused, duplicates are not generated, corrupted/missing references fail closed, and session data contains no secrets.

No LFX-016+ work. No TASKS edit.

Commit/push implementation then one task-final log-only commit; continue only under batch master.
