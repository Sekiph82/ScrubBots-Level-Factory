# SB-LFX-006-C001 — Candidate Inbox + Owner Review Queue — Strict Audit

## VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Severity:
- BLOCKER: 0
- MAJOR: 3
- MINOR: 0
- NOTE: 1

## Audited chain

- Start: `a6e7e43a2a2d612ff4771db9a1557606419f1e49`
- Implementation: `be48aea3dd938142d63ef0d431a4a63b03254f01`
- Task-final log-only: `2398ae5235a71971ba7749f23ece951d0378a1c5`

## Accepted implementation semantics

The implementation correctly derives candidates from canonical bundles, keeps source-only OWNER_UPLOAD records out of the Inbox, writes append-only review files, binds new reviews to candidate/artwork identities, preserves candidate bundle bytes in the focused test, and keeps solver/difficulty unavailable.

## MAJOR-001 — review evidence is not fail-closed on read

`_latest_review()` accepts any readable JSON object whose `candidate_id` and optional `artwork_sha256` match. It does not validate:
- review schema/version;
- review ID;
- disposition;
- sequence;
- previous-review lineage;
- candidate_identity_hash;
- reason/note types;
- candidate identity hash against the current candidate.

A malformed/tampered review file can therefore become the latest owner-review truth.

### Required remediation

Add a canonical review-record validator and chain reader. Reject/quarantine malformed/tampered records, verify candidate/artwork/grid identity binding and sequence/previous-review lineage before deriving queue state.

## MAJOR-002 — required real Godot review integration is absent

The criteria require real Studio evidence using at least two candidates and proving:
- queue derivation;
- ACCEPT and REJECT;
- history retention;
- candidate/source byte immutability;
- identity binding;
- corrupt review fail-closed;
- truthful unavailable fields.

The task contains only a Python unit test and a headless Studio boot. No committed real Godot Candidate/Review integration suite was added.

### Required remediation

Add a real Factory Studio integration exercising the full review workflow and corruption path.

## MAJOR-003 — Candidate Inbox UI omits required canonical evidence

The Python projection contains useful candidate fields, but the actual `FactoryStudioCandidates` UI renders only:

`candidate_id = owner_review disposition`

It does not present the required candidate-level evidence such as:
- source/provenance identity;
- current artwork/preview identity;
- dimensions;
- structural/QA evidence;
- solver/difficulty unavailable evidence;
- lineage/reference to immutable evidence.

### Required remediation

Render a selected-candidate detail/evidence panel or equivalent truthful UI sourced from the canonical Inbox projection. Do not recompute truth in GDScript.

## Publication / regression

Task-final publication is log-only. Final batch regression later reports 759 passed, 1 warning.

## NOTE

The focused unit test proves append-only ACCEPT→REJECT file creation and candidate-byte immutability for one candidate, but it cannot substitute for the required runtime/corruption evidence.

## Disposition

`SB-LFX-006` remains open pending remediation and re-audit.
