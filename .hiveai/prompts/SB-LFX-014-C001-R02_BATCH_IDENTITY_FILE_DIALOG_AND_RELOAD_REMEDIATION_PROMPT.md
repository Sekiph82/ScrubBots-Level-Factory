# SB-LFX-014-C001-R02 — Batch Identity + FileDialog + Reload Remediation

Work only on:
`.hiveai/audits/SB-LFX-014-C001-R01_BATCH_IMPORT_REAL_UI_IDENTITY_AND_RUNTIME_REMEDIATION_STRICT_AUDIT.md`

Create log first:
`.hiveai/codex-logs/SB-LFX-014-C001-R02_BATCH_IDENTITY_FILE_DIALOG_AND_RELOAD_REMEDIATION_CODEX_LOG.md`

Fix repeated-identical-batch evidence identity explicitly:
- either unique run ID per execution;
- or fully deterministic content-addressed payload.
No stable-ID/fresh-timestamp immutable-write conflict.

Replace pipe-delimited manual path entry as the primary UI with a real multi-file FileDialog. A programmatic setter may remain for tests.

Real integration must:
- use same display filename in different directories with different bytes;
- include duplicate bytes + corrupt file;
- snapshot external files and prove unchanged;
- run identical batch twice and prove intentional idempotence/run-identity behavior;
- restart/reload Studio and reload persisted batch-run record;
- prove per-item source IDs/errors/counts/provenance survive reload.

No implicit validation/promotion/acceptance. No TASKS edit.
