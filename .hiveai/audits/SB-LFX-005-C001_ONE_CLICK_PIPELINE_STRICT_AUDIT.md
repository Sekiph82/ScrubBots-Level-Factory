# SB-LFX-005-C001 — One-Click Pipeline — Strict Audit

## VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Severity:
- BLOCKER: 0
- MAJOR: 2
- MINOR: 0
- NOTE: 1

## Audited chain

- Start: `a6b87e6cd22a9553e0e0347654f6c4c1e16d5b95`
- Implementation: `4c61d69ec6ca822005b0b8fbc93db7203b015e37`
- Task-final log-only: `a6e7e43a2a2d612ff4771db9a1557606419f1e49`
- Final shared hardening: `f4001e3060c83b6a2cf9f51b72cc8f974110cba8`

## Accepted implementation semantics

The orchestrator correctly avoids fabricating M03/M04/M05/review truth and preserves OWNER_UPLOAD source bytes. Exact owner sources use canonical validation; generated candidates are discovered from canonical bundles; runs are separately persisted and later stages stop as NOT_AVAILABLE after a hard dependency.

No blocker was found.

## MAJOR-001 — stage lineage contract is incomplete

The audit criteria require **each stage** to bind canonical input/output identities and an exact failure/reason.

Current stage dictionaries are inconsistent:
- SOURCE has identities;
- NORMALIZE/DERIVE commonly has no input/output identity;
- PALETTE/STRUCTURE may contain only an evidence path or one input identity;
- CANDIDATE may have output identity but not input identity;
- SOLVE/DIFFICULTY/QA/REVIEW lack canonical input/output identity bindings.

This weakens durable stage lineage and makes later recovery/retry reasoning ambiguous.

### Required remediation

Define a consistent stage record contract with:
- stage name;
- disposition;
- input identity/reference(s);
- output identity/reference(s) when produced;
- evidence reference;
- exact reason.

Populate it for every stage, including NOT_APPLICABLE / NOT_AVAILABLE stages.

## MAJOR-002 — required runtime matrix is incomplete

The criteria/prompt require real integration coverage for:
- exact OWNER_UPLOAD path;
- Generate/canonical candidate path;
- validation failure;
- unavailable dependency stop;
- deterministic retained stage evidence / rerun lineage;
- source immutability;
- no false review/readiness.

The committed Godot integration covers only an exact OWNER_UPLOAD path and unavailable SOLVE/DIFFICULTY. Focused Python similarly covers the owner-upload stop.

No committed real acceptance evidence exercises:
- a real generated/canonical candidate pipeline path;
- a validation-failure pipeline path;
- rerun/history retention;
- no-redo behavior over retained successful evidence.

### Required remediation

Extend committed real integration to cover those missing paths and prove immutable prior run evidence remains intact.

## Publication / regression

Task-final publication is log-only. The final batch checkpoint reports 759 passed, 1 warning.

## NOTE

The shared regression-hardening commit improves the extension transport and static guard compatibility but does not resolve either MAJOR finding.

## Disposition

`SB-LFX-005` remains open pending remediation and re-audit.
