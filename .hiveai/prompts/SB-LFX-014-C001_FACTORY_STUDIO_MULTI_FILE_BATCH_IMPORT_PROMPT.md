# SB-LFX-014-C001 — Factory Studio Multi-File Pixel Art Batch Import

Builder log:
`.hiveai/codex-logs/SB-LFX-014-C001_MULTI_FILE_BATCH_IMPORT_CODEX_LOG.md`

Create log first. Work only on LFX-014.

Reuse the canonical LFX-002 OWNER_UPLOAD import operation per file. Do not create a second importer.

Add multi-file selection and, where Godot supports it reliably, drag/drop handling. Maintain per-item result/progress.

Persist only a versioned batch-run record of references/dispositions, never source truth.

Test same-name/different-bytes, duplicate bytes, corrupt item, partial success, restart/reload, source/external immutability and independent provenance.

If offering Import+Validate or Run Pipeline, it must call existing LFX-004/005 per item and keep evidence isolated. It must be explicit, not implicit owner acceptance.

No recovery/similarity/provider work. No TASKS edit.

Commit/push implementation then one task-final log-only commit; continue only under batch master.
