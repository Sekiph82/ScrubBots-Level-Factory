# SB-LFX-015-C001-R01 — Session Secret Containment, Reference Recovery + Runtime Remediation — Strict Audit

## VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Severity:
- BLOCKER: 1
- MAJOR: 3
- MINOR: 0
- NOTE: 1

## Audited chain

- R01 start: `5c89b9a00d58f6459e29981933725672ff61d0c7`
- R01 implementation: `fc3ad43aa27f4deb574c661cade9644bda5bfc04`
- R01 terminal log-only: `0eb2a401781c407dc4d3c3af98ee9f586960bcdf`

## Material improvements

R01 now:
- recursively removes secret-like keys from nested dictionaries/lists;
- validates session schema/version/session ID;
- adds Save / Restore controls in Studio;
- distinguishes RESUMED vs NEEDS_OPERATOR_ACTION in one narrow syntactic path;
- adds a real Godot session save/restore test.

These improvements are retained.

## BLOCKER-001 — session persistence still uses heuristic scrubbing instead of an explicit allowlist schema

The original remediation explicitly required an allowlist-based session contract.

Current `_scrub_session_value()` still accepts arbitrary nested mappings/lists/scalars and removes keys only when their names contain strings such as:
- secret;
- token;
- password;
- api_key;
- credential.

This remains heuristic filtering, not an explicit approved-state schema.

A sensitive value under an innocuous key can still persist.

### Required remediation

Replace generic recursive preservation with a versioned typed allowlist of approved session fields, for example:
- selected surface;
- selected canonical record IDs;
- active durable job references;
- safe bounded draft fields;
- autosave generation.

Reject unknown keys/structures instead of persisting them.

## MAJOR-001 — canonical references are still not actually revalidated

`_session_reference_checks()` treats every key ending in `_id` as VALID when the value merely matches a regex.

It does not resolve or validate:
- batch IDs;
- pipeline run IDs;
- retry IDs;
- source IDs;
- candidate IDs;
- revision IDs.

The real Godot test stores:

`active_batch_id = "batch-runtime"`

without creating any canonical batch record, yet restore reports:

`validated_references = true`

This reproduces the original false-evidence problem in a different form.

### Required remediation

Use typed reference fields and route each through its canonical reader/validator. A nonexistent `batch-runtime` must never validate.

## MAJOR-002 — recovery classification remains fabricated from syntactic validity

Current restore logic is:

- all reference strings regex-valid -> RESUMED;
- otherwise -> NEEDS_OPERATOR_ACTION.

It does not determine whether work is:
- actually resumable;
- already completed;
- failed and requiring RETRIED;
- NEW;
- NOT_RESUMABLE.

It also does not prove completed durable stages will be reused rather than rerun.

### Required remediation

Derive recovery disposition from real durable job/stage state and operation-specific resume capability.

## MAJOR-003 — required interruption/restart matrix is still absent

The real integration saves and restores one synthetic session inside the same runtime.

It does not:
- create a real pipeline/batch/retry job;
- interrupt the application mid-work;
- restart Studio;
- prove completed stage IDs remain unchanged;
- prove eligible work resumes;
- prove no duplicate source/candidate creation;
- corrupt a session and fail closed;
- delete/mismatch a referenced canonical record and report it;
- prove RETRIED / NEW / NOT_RESUMABLE classifications.

### Required remediation

Add a true restart/interruption integration using real durable work.

## NOTE

The global remediation batch retains the unrelated tracker-contract test failure.

## Disposition

`SB-LFX-015` remains open pending R02.
