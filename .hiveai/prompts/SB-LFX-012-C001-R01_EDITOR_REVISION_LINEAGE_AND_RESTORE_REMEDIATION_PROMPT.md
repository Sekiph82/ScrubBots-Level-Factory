# SB-LFX-012-C001-R01 — Editor Revision Lineage + Undo / Restore Remediation

Work only on:
.hiveai/audits/SB-LFX-012-C001_MANUAL_EDIT_REVISION_HISTORY_STRICT_AUDIT.md

Original criteria:
.hiveai/audit-criteria/SB-LFX-012-C001_IMMUTABLE_MANUAL_EDIT_REVISION_HISTORY_AUDIT_CRITERIA.md

Builder log:
.hiveai/codex-logs/SB-LFX-012-C001-R01_EDITOR_REVISION_LINEAGE_AND_RESTORE_REMEDIATION_CODEX_LOG.md

Create the builder log before edits.

## Mission
Close MAJOR-001..005 while preserving immutable source/editor truth.

### Revision contract
Bind revisions to the real manual-editor source and working-copy snapshot.
Validate schema/version, content-derived revision identity, source candidate/artwork/grid identity, parent lineage, width/height, exact C-ID cells, recomputed working-grid hash, deterministic change_count, sequence, immutable baseline/source revision and validation-evidence binding.
Corrupt lineage must fail closed.

### Studio operations
Implement real Save Revision, revision list/select, compare, undo/select prior revision, Restore Source and branch-after-undo controls.
Selecting/restoring must load the chosen grid into the existing memory-only editor working copy.
Never overwrite source bundle or prior revisions.
A new edit makes prior validation non-current for the new working hash.

### Real integration
Use the actual editor: R0 source -> edit/save R1 -> edit/save R2 -> compare -> select R1 -> edit/save branch R3 -> prove R2 retained -> restore source -> restart/reload history -> corrupt revision fail closed -> prove review/validation/promotion not inherited incorrectly.

No production promotion. No TASKS edit. Run full regressions and publish one R01 terminal log-only commit.