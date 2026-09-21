# SB-LFX-012-C001-R02 — Editor-Bound Revision History Remediation

Work only on:
`.hiveai/audits/SB-LFX-012-C001-R01_REVISION_LINEAGE_EDITOR_OPERATIONS_AND_RUNTIME_REMEDIATION_STRICT_AUDIT.md`

Create log first:
`.hiveai/codex-logs/SB-LFX-012-C001-R02_EDITOR_BOUND_REVISION_HISTORY_REMEDIATION_CODEX_LOG.md`

This is a substantive completion task, not a narrow test patch.

Required:
- revisions must be created from the real manual editor working-copy/source snapshot, not arbitrary caller cells;
- enforce immutable revision 0 as exact source baseline;
- add canonical revision validator/chain reader validating schema, content-derived revision digest/ID, source artwork identity, dimensions, palette cells, recomputed grid hash, sequence, parent chain, change_count/edit_operations;
- corrupt lineage must fail closed.

Studio must provide real:
- Save Revision;
- list/select;
- compare;
- undo/select prior revision;
- Restore Source;
- branch-after-undo.

Selecting/restoring must actually replace the manual editor working grid, never source bundle bytes.

Real integration:
R0 -> real editor edit/save R1 -> edit/save R2 -> compare -> select R1 -> edit/save branch R3 while R2 remains -> Restore Source -> restart Studio/reload history -> corrupt revision fail closed -> prove source bytes unchanged and validation/review/promotion evidence does not leak.

No TASKS edit.
