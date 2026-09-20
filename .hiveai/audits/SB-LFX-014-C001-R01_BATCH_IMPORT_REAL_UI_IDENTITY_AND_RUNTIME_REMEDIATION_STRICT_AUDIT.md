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
- a real Studio call into the existing canonical `batch-import` operation;
- per-run aggregate count rendering;
- real Godot integration with two valid PNG inputs, a duplicate path and a corrupt file;
- proof of truthful 3-success / 1-failure partial outcome;
- proof duplicate bytes reuse one content identity;
- proof two different-byte fixtures produce distinct source identities.

These improvements are retained.

## MAJOR-001 — batch-run identity / immutable evidence collision remains unresolved

The original audit found that:
- `batch_id` is derived only from `items`;
- persisted payload also contains fresh `created_at`;
- immutable write uses the batch ID path.

R01 does not modify `batch_import()` at all.

Current code still computes:

`batch_id = batch-import-<digest(items)>`

then writes a payload containing a new timestamp.

Therefore running an identical batch again can target the same immutable evidence path with different bytes and conflict instead of:
- creating a new run identity; or
- idempotently reusing a fully deterministic identical record.

### Required follow-up

Implement one explicit run-evidence policy:
- unique immutable run identity per execution, with a separately stable input fingerprint if useful; or
- complete deterministic content-addressed payload with no changing fields.

Add repeat-execution runtime proof.

## MAJOR-002 — real Studio input control does not satisfy multi-file FileDialog / drag-drop requirement

The authoritative criteria require:

> Support multi-file FileDialog and/or OS drag/drop.

The R01 Studio surface instead exposes one free-form `LineEdit` expecting absolute PNG paths separated by `|`.

This is a programmable test hook, not a real bounded multi-file operator selector. It also requires the operator to type/paste raw absolute paths.

### Required follow-up

Add a real Godot multi-file FileDialog with multiple selection enabled, or safe OS drag/drop. Keep a programmatic setter only as a test aid. Render selected files and per-item results.

## MAJOR-003 — required runtime matrix remains incomplete

The new integration proves partial success and duplicate identity, but it does not prove several explicit criteria:

1. **same filename + different bytes**:
   - fixtures are `first.png` and `nested-second.png`, not two different files with the same display filename;
2. **external input immutability**:
   - original fixture bytes are not snapshotted before import and compared afterward;
3. **restart/reload of persisted batch result**:
   - Studio is not restarted and batch evidence is not reloaded from durable record;
4. **repeat execution behavior**:
   - the same batch is not run twice, so MAJOR-001 cannot be observed/prevented;
5. **no-overwrite proof**:
   - source records are indirectly content-addressed, but the runtime does not snapshot the first source before the other imports/repeat run.

### Required follow-up

Extend the real integration to cover those exact cases while preserving canonical per-file LFX-002 import semantics.

## Publication / regression

Task-final publication is log-only.

Builder reports focused unit PASS and real batch-import integration PASS. The remediation-batch global suite retains the unrelated protected tracker-contract failure.

## NOTE

No backend source/import semantics were regressed by R01. The remaining issues are run-evidence identity, actual multi-file operator selection and the missing acceptance cases.

## Disposition

`SB-LFX-014` remains open pending a focused R02 remediation and re-audit.
