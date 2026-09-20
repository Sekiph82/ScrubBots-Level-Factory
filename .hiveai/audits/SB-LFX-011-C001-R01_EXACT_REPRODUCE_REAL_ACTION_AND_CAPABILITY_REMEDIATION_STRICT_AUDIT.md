# SB-LFX-011-C001-R01 — Exact Reproduce Real Action + Capability Remediation — Strict Audit

## VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Severity:
- BLOCKER: 1
- MAJOR: 2
- MINOR: 0
- NOTE: 1

## Audited chain

- R01 start: `d3fd15b3b39d875a9651c6d0fbf19d674c717d68`
- R01 implementation: `4e11fbe034f154944c4c27a122b4958145ad1a83`
- R01 terminal log-only: `d81d88cfecc0215022c17ea03c6e40a4e7dd49a7`

## Material improvements

The remediation now:
- validates canonical bundle/metadata/request identity before claiming exact replay;
- invokes the accepted canonical Factory Core Reproduce path;
- requires MATCH;
- compares complete reproduced/original bundle bytes;
- writes separate immutable reproduction evidence;
- preserves original bundle bytes;
- provides a real Exact Reproduce Studio action;
- rejects tampered metadata as STALE/INVALID.

These close most of the original implementation gap.

## BLOCKER-001 — Exact Reproduce UI action is not capability-gated

The task criteria explicitly require:

> Expose action only when capability permits it.

The real `FactoryStudioReproduce` UI creates an `Exact Reproduce` button and never disables it based on capability state.

Any arbitrary/stale/unsupported candidate ID therefore still receives an enabled Exact Reproduce action in the UI, even though the backend later rejects it.

This matches the original blocker condition:

> an unsupported/stale candidate gets an enabled Exact Reproduce action.

### Required remediation

- keep a reference to the Exact Reproduce button;
- disable it by default;
- enable it only after current selected identity has a fresh `EXACT_REPRODUCIBLE` capability result;
- any candidate-ID change must invalidate/disable the prior capability result until rechecked;
- SOURCE_RETRIEVABLE_ONLY / NOT_REPRODUCIBLE / STALE/INVALID / ERROR must keep Exact Reproduce disabled and display the reason.

## MAJOR-001 — nonexistent OWNER_UPLOAD IDs are falsely reported source-retrievable

Current capability code does:

`if candidate_id.startswith("owner-upload-"): SOURCE_RETRIEVABLE_ONLY`

when no canonical candidate exists.

It does not verify that a real immutable OWNER_UPLOAD source record/bytes actually exist.

The real integration even uses `owner-upload-missing` and expects SOURCE_RETRIEVABLE_ONLY, codifying the false capability claim.

### Required remediation

Resolve OWNER_UPLOAD capability only through the canonical owner-source reader/verifier:
- real verified OWNER_UPLOAD source -> SOURCE_RETRIEVABLE_ONLY;
- nonexistent/tampered source -> STALE/INVALID or NOT_REPRODUCIBLE;
- never infer retrievability from an ID prefix.

Add real positive and negative owner-source cases.

## MAJOR-002 — required draft/preset divergence and unsupported-path evidence is still absent

The R01 prompt requires proof that:
- changing current draft/preset values does not affect replay;
- unsupported/provider-like path remains disabled.

The committed R01 integration does not alter current Generate draft/preset state before replay, and does not test a real unsupported/provider-like canonical record.

### Required remediation

Extend the real Godot integration:
1. generate a deterministic candidate;
2. change current Studio draft values and/or a preset to materially different values;
3. run Exact Reproduce and prove output remains byte-identical to the recorded candidate;
4. create/use a real unsupported/non-replayable record and prove capability + UI action remain disabled;
5. retain the existing tampered-metadata and byte-immutability checks.

## NOTE

The remediation-batch global suite retains the unrelated protected tracker-contract failure.

## Disposition

`SB-LFX-011` remains open pending a narrow capability/UI/runtime follow-up.
