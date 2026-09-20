# SB-LFX-014-C001 — Drag-and-Drop Multi-File OWNER_UPLOAD Batch Import — Strict Audit Criteria

Target:
`SB-LFX-014 — Support drag-and-drop multi-file Pixel Art batch import with independent immutable provenance per file. [EXTENSION]`

## Principle

Batch import is orchestration over independent LFX-002 imports. Files never share identity/provenance and one failure never corrupts another source.

## BLOCKERS

FAIL if:
- same-named files overwrite each other;
- a batch-level identity replaces per-file SHA/source identity;
- original files are modified;
- one failure rolls back/deletes prior successful immutable imports;
- provenance is merged across files;
- batch import silently accepts/validates/promotes all items;
- TASKS is edited.

## Batch record

A versioned batch-import run may persist references:
- batch import ID;
- ordered input display entries;
- per-item source path display metadata;
- resulting source ID or error;
- import disposition;
- validation/pipeline reference if explicitly run.

It must not copy source bytes or become source authority.

## UI

Support multi-file FileDialog and/or OS drag/drop. Show per-item progress/result and aggregate counts.

Re-import/idempotence must reuse LFX-002 semantics.

Optionally invoke the existing validation/pipeline per item only if explicitly configured, recording each independently. No owner acceptance.

## Real integration

Use multiple files including:
- two same-name different-byte PNGs;
- duplicate bytes;
- corrupt/unsupported file.

Prove independent identities, partial success, no overwrite, external immutability, per-item validation/pipeline isolation if enabled, restart/reload of batch result, and cleanup.

## PASS rule

PASS when multi-file import is a bounded per-file orchestration with independent immutable provenance and truthful partial-failure handling.
