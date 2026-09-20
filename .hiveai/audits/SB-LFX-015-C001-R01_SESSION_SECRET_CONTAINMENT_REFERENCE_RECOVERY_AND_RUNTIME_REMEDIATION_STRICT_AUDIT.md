# SB-LFX-015-C001-R01 — Session Secret Containment, Reference Recovery + Runtime Remediation — Strict Audit

## VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Severity:
- BLOCKER: 1
- MAJOR: 4
- MINOR: 0
- NOTE: 1

## Audited chain

- R01 start: `5c89b9a00d58f6459e29981933725672ff61d0c7`
- R01 implementation: `fc3ad43aa27f4deb574c661cade9644bda5bfc04`
- R01 terminal log-only: `0eb2a401781c407dc4d3c3af98ee9f586960bcdf`
- Later shared hygiene commit inspected: `c340d2cc74f708721b1cf9a44baecb4e9e60bb71`

## Material improvements

R01 materially improves secret containment and basic Studio wiring:
- recursive nested mappings/lists are scrubbed for secret/token/password/api_key/credential-like keys;
- nesting depth is bounded;
- unsupported non-JSON values fail closed;
- session schema/version/session_id are checked on restore;
- real Save / Restore buttons exist;
- real Godot integration inspects persisted bytes and proves nested `api_key` / `token` keys are absent.

The original known nested-secret example is therefore closed.

## BLOCKER-001 — recovery still cannot distinguish durable RESUMED / RETRIED / NEW truth

The authoritative criteria explicitly make it a blocker if:

> RESUMED/RETRIED/NEW work is not distinguishable.

Current `restore_session()` returns only:
- `RESUMED` when all syntactic ID checks pass;
- `NEEDS_OPERATOR_ACTION` otherwise.

It never derives:
- RETRIED;
- NEW;
- NOT_RESUMABLE;

from actual durable job/stage state.

The R01 test codifies the problem by saving a nonexistent `active_batch_id = "batch-runtime"` and asserting `RESUMED`.

### Required follow-up

Recovery disposition must be derived from verified canonical record type + durable job/stage/attempt state:
- RESUMED only for an actually resumable interrupted durable operation;
- RETRIED only when a verified retry attempt is the active continuity target;
- NEW only for continuity with no started durable work;
- NOT_RESUMABLE / NEEDS_OPERATOR_ACTION for unsupported, completed, corrupt or missing states as appropriate.

## MAJOR-001 — “reference validation” is only regex validation

`_session_reference_checks()` treats every state key ending in `_id` as a reference and considers it VALID if its string shape matches a regex.

It does not open or validate:
- batch manifests/batch-import records;
- pipeline runs;
- retry attempts;
- candidates;
- owner sources;
- revisions.

Thus a well-formed but nonexistent ID is reported as a validated canonical reference.

This leaves the original false-`validated_references` finding unresolved.

### Required follow-up

Use explicit typed reference fields and dispatch each through its canonical reader/validator. Store/reference expected identity hashes where needed. Missing, corrupt or mismatched records must fail closed individually.

## MAJOR-002 — session schema remains arbitrary state + heuristic scrubbing rather than allowlisted continuity

The R01 remediation prompt required an **explicit allowlisted versioned session schema**.

Current `save_session()` still accepts an arbitrary mapping and recursively copies all JSON-compatible keys except those whose names match secret-like substrings.

This can persist large/irrelevant mutable state and remains a heuristic rather than a bounded continuity contract.

### Required follow-up

Define exact allowed fields, for example:
- selected surface;
- typed source/candidate/batch/pipeline/retry/revision references;
- current durable stage/attempt reference;
- bounded non-canonical draft values;
- autosave generation.

Reject unknown fields/nested structures. Do not attempt to preserve arbitrary application state.

## MAJOR-003 — real autosave/interruption/restart recovery is absent

The new Studio surface provides manual Save and Restore, but no autosave trigger or durable recovery controller.

The real integration:
- does not start a real pipeline/batch job;
- does not interrupt/close Studio mid-work;
- does not instantiate a new Studio process/session and restore;
- does not prove successful durable stage IDs remain unchanged;
- does not prove no duplicate source/candidate creation;
- does not test missing/deleted canonical reference;
- does not test corrupt session fail-closed.

### Required follow-up

Use a real durable batch/pipeline/retry workflow, save continuity, terminate/reinstantiate Studio, restore and prove the authoritative recovery matrix.

## MAJOR-004 — successful durable stages are not proven reused

Because restore does not resolve real jobs/stages, there is no mechanism or runtime proof that already successful durable stages are reused instead of rerun.

The session currently restores labels/IDs only; it does not actually resume an eligible canonical job from its durable stage boundary.

### Required follow-up

Connect recovery to a real resumable operation contract, explicitly preserve completed stage/output identities, and assert they remain byte/identity-stable across recovery.

## Shared hygiene commit

`c340d2cc...` changes string spelling in the session UI/test and allowlists new Godot test filenames in the project-boundary test. It does not resolve the canonical-reference or recovery-state findings above.

## NOTE

The remediation-batch global suite retains the separate protected tracker-contract failure.

## Disposition

`SB-LFX-015` remains open pending canonical typed-reference and real interruption/recovery remediation.
