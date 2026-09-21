# SB-LFX-012-C001-R02 — Editor-Bound Revision History Remediation — Strict Audit

## VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Severity:
- BLOCKER: 0
- MAJOR: 1
- MINOR: 0

## Material closure

R02 substantially completes the product contract:
- revision 0 is enforced as the exact canonical source baseline;
- revision records use a versioned schema and content digest;
- source artwork identity, grid hash, sequence, parent chain, change count and edit-operation indices are revalidated fail-closed;
- branch-after-undo is supported without deleting later history;
- real Save Revision / Select-Undo / Compare / Restore Source controls exist;
- revision saves source their cells from the real manual editor working copy;
- source artwork bytes remain immutable.

## MAJOR-001 — required restart/operator-path acceptance matrix is not fully executed

The R02 prompt requires a real Studio restart/reload and proof that the operator controls themselves perform select/undo/compare/restore.

The integration calls `revision-list` again in the same instantiated Studio and labels that a restart/reload proof. It does not destroy/reinstantiate the Studio or start a fresh process/session before reconstructing history.

The test also bypasses the actual Select/Undo UI method for the key state transition by directly calling `revision-load` and `editor.load_revision_cells`. Compare is similarly asserted through the gateway rather than the surface method.

Finally, the required “validation/review/promotion evidence does not leak” matrix only checks revision validation is not PASS; it does not create and preserve real owner-review/promotion evidence around revision transitions.

### Required follow-up

Run the matrix through the real surface:
- save R0/R1/R2;
- invoke Compare through the revision surface;
- invoke Select/Undo through the surface;
- branch R3;
- Restore Source through the surface;
- destroy/reinstantiate Studio (or a true fresh-process test) and reconstruct the same immutable history;
- include real review/acceptance evidence and prove revisions never inherit or rewrite it;
- retain corruption fail-closed and source-byte immutability checks.

## Disposition

`SB-LFX-012` remains open for R03.
