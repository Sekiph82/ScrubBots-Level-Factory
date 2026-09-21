# SB-LFX-014-C001-R01 — Batch Import Real UI, Identity + Runtime Remediation — Strict Audit

## VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Severity:
- BLOCKER: 0
- MAJOR: 3
- MINOR: 0
- NOTE: 1

## Audited chain

- R01 start: `e0872bef72ef85e3062724db4bd13598c9e7961b`
- R01 implementation: `c44165fa118eeb90220894ca5c8aa96fbc39971d`
- R01 terminal log-only: `5c89b9a00d58f6459e29981933725672ff61d0c7`

## Material improvements

R01 adds:
- a real Studio-triggered batch-import operation;
- per-run projection in the Batch Import surface;
- a runtime scenario with two distinct valid PNGs, duplicate bytes and one corrupt file;
- truthful partial-success counts;
- duplicate-byte source-ID reuse;
- distinct-file identity separation.

These improvements are retained.

## MAJOR-001 — repeated-identical-batch evidence collision remains unresolved

The original audit explicitly identified that:

- `batch_id` is derived only from item results;
- persisted payload also includes a fresh `created_at`;
- immutable write therefore conflicts when an identical batch is run again with the same batch ID but different timestamp.

R01 does not modify `batch_import()` at all.

The same defect therefore remains.

### Required remediation

Choose and implement one explicit contract:
- unique immutable run ID per execution; or
- fully deterministic content-addressed batch record including deterministic time semantics.

Then add a repeat-identical-batch test proving the second execution behaves intentionally and never collides silently.

## MAJOR-002 — Studio input UX does not satisfy the multi-file selection contract

The R01 surface asks the operator to type absolute PNG paths separated by `|`.

The original criteria and remediation prompt require a real multi-file FileDialog and optionally drag/drop.

A pipe-delimited text field is not a practical multi-file import UI and bypasses the intended explicit file-selection boundary.

### Required remediation

Use a FileDialog configured for multiple file selection. Drag/drop is optional if not reliable.

Keep the programmatic setter only for headless testing.

## MAJOR-003 — required runtime evidence remains incomplete

The R01 runtime proves per-item identities and partial outcomes, but does not prove:
- external fixture bytes remain unchanged;
- batch-run record can be reloaded after Studio restart;
- repeat-identical-batch behavior;
- persisted batch-run record identity/immutability;
- same-name/different-byte case specifically under identical display filename;
- per-item provenance survives reload.

### Required remediation

Extend the real integration to:
1. snapshot all external input bytes before import and prove unchanged;
2. use same display filename in different directories for different bytes;
3. rerun an identical batch and assert the chosen idempotence/run-identity policy;
4. restart/reload Studio and reload the persisted batch-run record;
5. prove item source IDs/errors/counts remain intact.

## NOTE

The remediation-batch global suite retains the unrelated protected tracker-contract failure.

## Disposition

`SB-LFX-014` remains open pending R02.
