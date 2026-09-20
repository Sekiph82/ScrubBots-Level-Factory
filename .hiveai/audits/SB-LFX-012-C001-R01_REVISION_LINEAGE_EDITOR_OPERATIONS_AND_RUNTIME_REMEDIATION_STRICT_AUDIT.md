# SB-LFX-012-C001-R01 — Revision Lineage, Editor Operations + Runtime Remediation — Strict Audit

## VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Severity:
- BLOCKER: 0
- MAJOR: 4
- MINOR: 0
- NOTE: 1

## Audited chain

- R01 start: `d81d88cfecc0215022c17ea03c6e40a4e7dd49a7`
- R01 implementation: `4fb6d88d65655c26a114b6109489a6ed7067dc51`
- R01 terminal log-only: `23ef20b37fa20d766e5fe380e14c9c946a06973a`

## Material improvements

R01 improves the standalone revision record path by:
- requiring explicit parent after the first revision;
- loading/validating parent dimensions/grid shape;
- computing exact changed-cell count;
- persisting bounded edit-operation metadata;
- adding revision-create/list/compare gateway operations;
- adding a real Godot suite that creates root/child revisions, compares them, checks exact change count and rejects a post-root revision without a parent.

These improvements are retained.

## MAJOR-001 — the real manual editor is still not the revision authority

The task requires revision history to extend the accepted manual logical-pixel editor.

R01 still creates revisions from caller-supplied:
- candidate_id;
- width/height;
- cells;
- parent revision ID.

The real Godot integration reads `artwork.json` and submits cell arrays directly through the Gateway. It does not:
- load the candidate into the accepted manual editor;
- make logical-pixel edits through the editor;
- bind Save Revision to the editor's current source/working-copy snapshot;
- prove the revision is the editor's exact current working-grid identity.

### Required follow-up

Save Revision must source its candidate/artwork/grid identity and exact working cells from the real editor state, not from arbitrary caller-supplied cells.

## MAJOR-002 — required Save / select / compare / undo / restore UI is still absent

The real `FactoryStudioRevisions` surface exposes only:
- candidate ID input;
- List revisions.

There are still no operator controls for:
- Save Revision;
- select/load revision;
- compare two selected revisions;
- Undo/select prior revision;
- Restore Source;
- branch-after-undo.

The product requirement is therefore not implemented as an operator workflow.

## MAJOR-003 — durable revision lineage is still not fully fail-closed

The criteria require immutable revision identity/content binding and corruption-safe reload.

Current records still have no independently verified content hash/revision digest.

`list_revisions()` currently checks only:
- revision schema;
- candidate ID.

It does not revalidate:
- exact key/schema completeness;
- source artwork SHA against the current canonical candidate;
- width/height/cell-count legality;
- C01..C16 cells;
- recomputed working-grid hash;
- sequence consistency;
- parent existence/identity;
- parent-chain continuity;
- change_count/edit_operations against actual parent delta;
- immutable source-baseline semantics.

A tampered revision can therefore remain visible as valid lineage.

The first/root revision is also merely any caller-supplied legal grid with no parent. It is not enforced to be the exact immutable source baseline.

### Required follow-up

Define one canonical revision validator/chain reader that recomputes and verifies all identity/lineage facts, including a content-derived digest or equivalent immutable record hash. Enforce revision 0 as the exact source baseline.

## MAJOR-004 — undo/restore/restart/corruption acceptance matrix remains absent

The R01 real Godot suite proves create/list/compare only.

It still does not prove:
- source bytes remain unchanged;
- selecting an old revision actually changes the manual editor working grid;
- edit-after-undo creates a branch while retaining later history;
- Restore Source actually restores editor working pixels;
- Studio restart/reload reconstructs the history;
- corrupt revision fails closed;
- validation evidence becomes non-current after a different revision/edit;
- owner review/promotion truth is not inherited incorrectly.

This leaves the core undo/restore behavior from the original audit unresolved.

## Publication / regression

The task-final publication is log-only.

Builder reports focused revision test PASS and real revision-lineage integration PASS. The remediation-batch global suite retains the unrelated protected tracker-contract failure.

## NOTE

R01 narrows some original contract gaps but its own builder-log scope describes "create/list/compare" rather than the full editor-linked undo/restore workflow required by the authoritative criteria. The independent audit therefore retains the partial implementation instead of treating the narrower builder scope as task closure.

## Disposition

`SB-LFX-012` remains open pending a substantive editor-linked revision-history follow-up and re-audit.
