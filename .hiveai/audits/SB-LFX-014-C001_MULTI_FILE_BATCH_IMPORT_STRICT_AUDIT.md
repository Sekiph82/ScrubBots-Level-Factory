# SB-LFX-014-C001 — Multi-File OWNER_UPLOAD Batch Import — Strict Audit

## VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Severity:
- BLOCKER: 0
- MAJOR: 3
- MINOR: 0
- NOTE: 0

## Audited chain

- Start: `861ac9e9fd87d19275207ad1e7401dd0c80e8abd`
- Implementation: `2026a80fb1d364918e384b9e82c1d1d8b88bf51d`
- Task-final log-only: `70d441e39d7f3f39b1307b5df412bd50c7660617`

## Accepted implementation semantics

`batch_import()` correctly delegates each item to the canonical LFX-002 importer rather than creating a second importer. Focused coverage demonstrates:
- same filename + different bytes -> separate source IDs;
- duplicate bytes -> same content-addressed source ID;
- corrupt input -> per-item failure;
- truthful partial-success counts.

The persisted batch record stores references/results, not source bytes.

## MAJOR-001 — real Studio batch-import interaction is not implemented

`FactoryStudioBatchImport` is informational only. It provides no:
- multi-file FileDialog;
- OS drag/drop;
- selected-file list;
- Import action;
- per-item progress/result;
- aggregate runtime counts.

Its snapshot always says AVAILABLE without executing a batch.

### Required remediation

Connect the real Studio surface to the canonical batch operation, with multi-file selection and per-item result rendering. Add drag/drop if the current Godot shell can support it safely; FileDialog multi-select is sufficient if drag/drop is not reliable.

## MAJOR-002 — required real integration/reload/immutability evidence is absent

No real Godot batch-import integration was committed.

The required runtime matrix must prove:
- same-name/different-byte files;
- duplicate bytes;
- corrupt item;
- partial success;
- no overwrite;
- external input bytes unchanged;
- independent per-file provenance;
- restart/reload of persisted batch result;
- cleanup.

The focused Python test does not verify external-file immutability or restart/reload through Studio.

## MAJOR-003 — repeated identical batch can collide with immutable evidence

`batch_id` is derived only from the item result list, while the persisted immutable payload also contains a fresh `created_at`.

Running an identical batch again can produce the same batch ID/path but different payload bytes due to timestamp, causing immutable-write conflict rather than recording a new run or idempotently reusing identical evidence.

### Required remediation

Choose one explicit policy:
- unique run identity that includes a canonical run nonce/sequence/time component; or
- content-addressed batch evidence whose complete persisted payload is deterministic.

Prove repeat execution behavior.

## Disposition

`SB-LFX-014` remains open pending remediation and re-audit.
