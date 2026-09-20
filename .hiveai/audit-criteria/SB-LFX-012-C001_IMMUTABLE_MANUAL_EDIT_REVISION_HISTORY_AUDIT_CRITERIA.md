# SB-LFX-012-C001 — Immutable Manual-Edit Revision History / Undo / Restore Source — Strict Audit Criteria

Target:
`SB-LFX-012 — Add immutable manual-edit revision history with compare/undo/restore-source behavior and no silent source overwrite. [EXTENSION]`

## Principle

Manual edit history is immutable lineage. Undo/restore changes current working selection by creating or selecting explicit revisions; history is never rewritten.

## BLOCKERS

FAIL if:
- source bundle/source artwork bytes are overwritten;
- revision files are mutated in place after publication;
- undo deletes history;
- restore-source silently erases revisions;
- revision identity is not bound to exact logical grid/source identity;
- validation evidence for one revision is reused as current for another;
- revision save implies owner acceptance/promotion;
- TASKS is edited.

## Revision contract

Each durable revision must include:
- versioned schema;
- revision ID/content hash;
- immutable source candidate/artwork identity;
- parent revision/reference;
- exact width/height;
- exact C-ID logical grid or a canonical immutable grid artifact;
- working-grid hash;
- change summary/count;
- creation sequence/time under an auditable policy;
- validation state/evidence reference if separately available.

Revision 0/source baseline must be explicit and immutable.

## Operations

Require:
- Save Revision;
- compare any two revisions with changed-cell facts;
- undo to prior state without deleting later history;
- restore source explicitly;
- branch/new revision after undo if editing continues.

A new edit after a validated revision must make prior validation non-current for the new working state.

## Real integration

Using the real manual editor:
1. load canonical source;
2. make edits and save R1/R2;
3. verify source bytes unchanged;
4. compare R1/R2;
5. undo/select R1;
6. edit again and save branch/new revision without deleting R2;
7. restore source;
8. restart/reload Studio and reconstruct history;
9. corrupt revision and fail closed;
10. prove validation/review/promotion truth is not inherited incorrectly.

## PASS rule

PASS when manual editing has durable immutable revision lineage with explicit compare/undo/restore and zero silent source/history mutation.
