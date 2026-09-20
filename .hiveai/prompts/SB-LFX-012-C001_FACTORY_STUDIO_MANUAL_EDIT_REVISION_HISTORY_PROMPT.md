# SB-LFX-012-C001 — Factory Studio Manual-Edit Revision History

Builder log:
`.hiveai/codex-logs/SB-LFX-012-C001_MANUAL_EDIT_REVISION_HISTORY_CODEX_LOG.md`

Create log first. Work only on LFX-012.

Extend the accepted memory-only logical-pixel editor with a separate durable immutable revision layer.

Define a versioned revision contract bound to immutable source candidate/artwork identity and exact working grid hash.

Implement:
- baseline/source revision;
- Save Revision;
- revision list;
- compare;
- undo/select prior revision;
- restore source;
- edit-after-undo producing new immutable lineage without deleting later revisions.

Never overwrite source bundle or prior revisions.

Ensure revalidation/review evidence is revision/hash-bound and becomes stale/non-current when the working grid changes.

Real Godot restart/reload integration is required, including corruption fail-closed.

No production promotion, no LFX-013+ work, no TASKS edit.

Commit/push implementation then one task-final log-only commit; continue only under batch master.
