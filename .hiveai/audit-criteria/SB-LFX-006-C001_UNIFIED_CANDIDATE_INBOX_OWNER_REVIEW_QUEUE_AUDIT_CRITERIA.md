# SB-LFX-006-C001 — Unified Candidate Inbox + Owner Review Queue — Strict Audit Criteria

Target:
`SB-LFX-006 — Build unified Candidate Inbox and owner Review Queue across provider, procedural, owner-upload and library-derived candidates. [EXTENSION]`

## Truth boundary

Only actual canonical candidate records/artifacts may enter the Candidate Inbox. A source record alone is not automatically a candidate.

Owner review is explicit, durable, auditable evidence and is independent from structural QA.

## BLOCKERS

FAIL if:
- source/library membership is treated as candidate acceptance;
- QA PASS auto-accepts owner review;
- review mutates candidate/source bytes;
- ACCEPT/REJECT overwrites prior review evidence;
- provider/procedural/owner origins are fabricated;
- unavailable solver/difficulty is shown as passed;
- a second candidate compiler/store becomes authority;
- TASKS is modified.

## Candidate aggregation

Inbox must derive candidates from committed canonical candidate/bundle/pipeline records available at runtime.

For every candidate display:
- candidate identity;
- source/provenance identity;
- current canonical preview/artwork identity;
- dimensions;
- QA/structural evidence if real;
- solver/difficulty evidence if real, otherwise NOT AVAILABLE;
- owner-review latest disposition;
- lineage/reference to immutable evidence.

Unsupported source families remain absent or explicitly unavailable, never synthesized.

## Owner review record

Implement a versioned append-only owner-review evidence contract bound to exact candidate identity/artwork hash.

At minimum:
- review record ID;
- candidate ID and immutable identity hash;
- disposition ACCEPT / REJECT;
- reason/note;
- review sequence/timestamp using an existing deterministic/auditable policy;
- previous-review reference where applicable.

A new review creates new evidence. It must not silently rewrite history.

## Review queue

Queue states must be derived:
- NEEDS_REVIEW where no valid owner review exists;
- ACCEPTED / REJECTED from latest valid owner-review evidence.

Do not infer review from QA.

## Real integration

Prove at least two real candidates from available canonical origins, queue derivation, ACCEPT, REJECT, review-history retention, source/candidate byte immutability, candidate identity binding, corrupt review fail-closed, and truthful unavailable fields.

## PASS rule

PASS when Candidate Inbox is a derived view over real candidates and owner review is explicit append-only evidence that cannot be confused with QA or mutate candidate/source truth.
