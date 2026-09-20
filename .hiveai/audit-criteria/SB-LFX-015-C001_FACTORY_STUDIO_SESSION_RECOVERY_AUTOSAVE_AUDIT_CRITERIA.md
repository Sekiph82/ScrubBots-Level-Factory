# SB-LFX-015-C001 — Factory Studio Session Recovery / Autosave — Strict Audit Criteria

Target:
`SB-LFX-015 — Add Factory Studio session recovery/autosave that resumes eligible durable jobs without redoing successful stages. [EXTENSION]`

## Principle

Recovery references durable canonical truth. Autosave is not a shadow copy of source/candidate/job truth.

## BLOCKERS

FAIL if:
- session file becomes authoritative over canonical artifacts;
- recovery reruns successful durable stages by default;
- source/candidate bytes are restored from stale copied blobs instead of canonical records;
- RESUMED/RETRIED/NEW work is not distinguishable;
- corrupted session can overwrite valid canonical state;
- secrets/provider tokens are persisted;
- TASKS is edited.

## Session record

Persist only enough versioned state to restore operator context and eligible work:
- selected surface/record IDs;
- active pipeline/batch/retry job references;
- current durable stage/attempt identity;
- unsaved UI draft values where safe and clearly non-canonical;
- autosave generation/revision.

On load, every canonical reference must be revalidated.

## Recovery behavior

Classify work as:
- RESUMED: continues an interrupted eligible stage/job;
- RETRIED: explicit new attempt after recorded failure;
- NEW: newly started work.

Already successful durable stages remain reused and are not silently rerun.

Unsafe/non-resumable operations must be marked NEEDS_OPERATOR_ACTION or NOT_RESUMABLE.

## Real interruption test

Simulate application/process interruption during a multi-stage/batch workflow, restart Studio, load recovery state and prove:
- completed stage identities unchanged;
- eligible work resumes;
- no duplicate source/candidate creation;
- session corruption fails closed;
- deleted/mismatched canonical references are reported rather than recreated;
- owner local secrets are absent.

## PASS rule

PASS when recovery restores operator continuity from verified canonical references without duplicating completed work or creating a second truth store.
