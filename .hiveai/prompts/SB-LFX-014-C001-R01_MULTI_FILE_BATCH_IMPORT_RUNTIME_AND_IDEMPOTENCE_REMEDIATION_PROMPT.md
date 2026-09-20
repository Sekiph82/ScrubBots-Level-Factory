# SB-LFX-014-C001-R01 — Multi-File Batch Import Runtime + Idempotence Remediation

Work only on:
.hiveai/audits/SB-LFX-014-C001_MULTI_FILE_BATCH_IMPORT_STRICT_AUDIT.md

Original criteria:
.hiveai/audit-criteria/SB-LFX-014-C001_MULTI_FILE_OWNER_UPLOAD_BATCH_IMPORT_AUDIT_CRITERIA.md

Builder log:
.hiveai/codex-logs/SB-LFX-014-C001-R01_MULTI_FILE_BATCH_IMPORT_RUNTIME_AND_IDEMPOTENCE_REMEDIATION_CODEX_LOG.md

Create the builder log before edits.

## Mission
Close MAJOR-001..003.

### Real Studio batch import
Implement a real multi-file Studio surface with FileDialog multi-select and per-item result/progress. Add drag/drop only if the current Godot shell can do it safely; multi-select alone is acceptable.
Use the canonical LFX-002 importer per file. Do not create another importer.

### Batch-run evidence identity
Fix repeated-identical-batch behavior. Choose one explicit contract:
- unique run identity for each execution with immutable evidence; or
- fully deterministic content-addressed evidence whose complete payload, including any time field, is identical.
Never let a repeat run collide because batch_id is stable while created_at changes.

### Real integration
Use two same-name/different-byte PNGs, duplicate bytes and a corrupt file.
Prove partial success, distinct/per-file provenance, duplicate identity reuse, no overwrite, external files unchanged, per-item statuses, persisted batch result reload after Studio restart and bounded cleanup.

Do not implicitly validate/promote/accept items. Do not edit TASKS.md.

Run focused, retained and full regressions, then publish exactly one R01 terminal builder-log-only commit.