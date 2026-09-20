# SB-LFX-012-C001-R02 — Editor-Bound Immutable Revision History Remediation

Work only on:
`.hiveai/audits/SB-LFX-012-C001-R01_REVISION_LINEAGE_EDITOR_OPERATIONS_AND_RUNTIME_REMEDIATION_STRICT_AUDIT.md`

Original criteria:
`.hiveai/audit-criteria/SB-LFX-012-C001_IMMUTABLE_MANUAL_EDIT_REVISION_HISTORY_AUDIT_CRITERIA.md`

Builder log:
`.hiveai/codex-logs/SB-LFX-012-C001-R02_EDITOR_BOUND_REVISION_HISTORY_REMEDIATION_CODEX_LOG.md`

Create log before edits.

## Mission

This is substantive. Close all remaining editor/lineage/runtime findings while preserving accepted LF06 editor truth.

### Canonical revision lineage
Create one canonical validator/chain reader that verifies every revision:
- exact schema/version/key set;
- content-derived immutable revision digest/identity;
- canonical source candidate/artwork/grid identity;
- revision 0 equals exact immutable source baseline;
- sequence;
- parent existence + parent identity;
- width/height;
- exact C01..C16 cells;
- recomputed working-grid hash;
- change_count and edit_operations against actual parent delta;
- validation reference/state binding.

Any modified content under an existing revision identity must fail closed.

### Real editor authority
Save Revision must obtain candidate/source identity, dimensions and cells directly from the accepted manual editor current snapshot/working grid. Do not accept arbitrary caller cells as the Studio product authority path.

### Real Studio operations
Implement:
- Save Revision;
- revision list/select;
- compare two revisions;
- Undo/select prior revision;
- Restore Source;
- branch-after-undo.

Selecting a revision or source must actually load that exact grid into the accepted memory-only editor working copy without changing canonical source bytes.

### Validation truth
When the working grid changes/selects:
- prior revalidation evidence must become non-current unless hash-identical;
- owner review/promotion truth must never be inherited into a new manual revision.

### Real restart integration
Prove:
R0 exact source baseline → editor edit/save R1 → edit/save R2 → compare → load R1 → edit/save branch R3 → R2 still retained → restore source → editor exact source grid → restart/reinstantiate Studio → reload lineage → corrupt revision → fail closed.

Snapshot canonical source bundle bytes before/after.

This R02 also supplies the immutable revision identity required by SB-LFX-016.

Run focused + LF06 editor/revalidation + full suite. One R02 implementation + terminal log-only commit. Do not edit TASKS.md.
