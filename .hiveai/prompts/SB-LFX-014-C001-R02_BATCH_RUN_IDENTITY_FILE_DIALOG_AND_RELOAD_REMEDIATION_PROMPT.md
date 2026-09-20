# SB-LFX-014-C001-R02 — Batch Run Identity + Multi-File Dialog + Reload Remediation

Work only on:
`.hiveai/audits/SB-LFX-014-C001-R01_BATCH_IMPORT_REAL_UI_IDENTITY_AND_RUNTIME_REMEDIATION_STRICT_AUDIT.md`

Original criteria:
`.hiveai/audit-criteria/SB-LFX-014-C001_MULTI_FILE_OWNER_UPLOAD_BATCH_IMPORT_AUDIT_CRITERIA.md`

Builder log:
`.hiveai/codex-logs/SB-LFX-014-C001-R02_BATCH_RUN_IDENTITY_FILE_DIALOG_AND_RELOAD_REMEDIATION_CODEX_LOG.md`

Create log before edits.

## Mission

Close all remaining R01 findings.

### Batch-run evidence identity
Fix identical rerun collision using one explicit policy.

Preferred:
- every execution gets a unique immutable `batch_run_id`;
- store a separate deterministic `input_fingerprint` over ordered input identities/results where useful;
- created_at may remain only because run identity is unique.

Alternatively use fully deterministic content-addressed evidence with no changing fields. Whichever contract you choose, prove identical repeated executions are safe.

### Real multi-file operator selection
Add a Godot multi-file FileDialog with multi-selection enabled.
- selected list visible;
- Import Batch action;
- per-item disposition/source ID/error visible;
- aggregate counts visible.
Keep programmatic set_paths only as a headless test hook if needed.

OS drag/drop is optional if multi-file FileDialog is reliable.

### Runtime matrix
Use:
- two files with the same display filename but different bytes in separate directories;
- a duplicate-byte file/path;
- corrupt PNG.

Snapshot every external fixture before import and prove unchanged afterward.

Prove:
- distinct same-name bytes -> distinct source IDs;
- duplicate bytes -> same source ID;
- partial success;
- no overwrite;
- run same ordered batch twice safely according to run identity policy;
- restart/reinstantiate Studio and reload persisted batch-run result;
- cleanup.

Do not automatically validate/promote/review imports.

Run full regressions. One R02 implementation + terminal log-only commit. Do not edit TASKS.md.
