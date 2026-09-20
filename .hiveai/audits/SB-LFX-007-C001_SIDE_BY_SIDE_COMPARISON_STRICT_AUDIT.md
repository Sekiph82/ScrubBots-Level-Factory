# SB-LFX-007-C001 — Side-by-Side Candidate Comparison — Strict Audit

## VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Severity:
- BLOCKER: 0
- MAJOR: 3
- MINOR: 0
- NOTE: 0

## Audited chain

- Start: `2398ae5235a71971ba7749f23ece951d0378a1c5`
- Implementation: `27e76d350db88aa9f40defe98de352d62400dc42`
- Task-final log-only: `5987ec84eaabf2ae7440c25bef6d40f2c048a7f0`

## Accepted implementation semantics

The comparison projection is read-only, requires distinct real candidate IDs, exposes candidate/artwork/grid/dimension/color information, keeps solver/difficulty/cost unavailable, and explicitly refuses to compute a winner. The focused Python test proves two candidate identities and no candidate-byte mutation.

## MAJOR-001 — no real Godot comparison integration

The task prompt and criteria explicitly require real Godot tests covering two candidates, evidence isolation, refresh/reselection and immutability.

No committed comparison integration suite was added. The builder reports only focused Python and a generic headless Studio boot.

### Required remediation

Add real Factory Studio comparison integration covering:
- two distinct candidates;
- correct preview/artwork identities;
- differing canonical metrics;
- unavailable fields;
- bound owner review;
- refresh/reselection without cross-wire;
- zero candidate/review mutation.

## MAJOR-002 — comparison inherits non-fail-closed review evidence

`compare_candidates()` calls the current `_latest_review()`, which does not validate review schema, identity hash or lineage before treating a record as current owner-review evidence.

Therefore comparison cannot currently prove stale/tampered review exclusion as required.

### Required remediation

Consume only review evidence that passes the canonical review validator required by SB-LFX-006 remediation. Mark stale/mismatched evidence unavailable/stale rather than showing it as current.

## MAJOR-003 — required provenance and structural/QA evidence is not rendered

The Python projection includes `origin` and `quality`, but the real `FactoryStudioComparison` UI renders:
- candidate ID;
- artwork SHA;
- dimensions;
- used colors;
- review;
- solver;
- difficulty;
- cost.

It omits:
- source/provenance/origin;
- structural/QA disposition/evidence.

This does not satisfy the required side-by-side evidence surface.

### Required remediation

Render provenance/origin plus canonical structural/QA evidence for each candidate without recomputing those facts in GDScript.

## Disposition

`SB-LFX-007` remains open pending remediation and re-audit.
