# SB-LFX-006-C001-R01 — Review Validation + Runtime + Evidence UI Remediation

Work only on:
`.hiveai/audits/SB-LFX-006-C001_CANDIDATE_INBOX_OWNER_REVIEW_QUEUE_STRICT_AUDIT.md`

Original criteria:
`.hiveai/audit-criteria/SB-LFX-006-C001_UNIFIED_CANDIDATE_INBOX_OWNER_REVIEW_QUEUE_AUDIT_CRITERIA.md`

Builder log:
`.hiveai/codex-logs/SB-LFX-006-C001-R01_REVIEW_VALIDATION_RUNTIME_AND_EVIDENCE_UI_REMEDIATION_CODEX_LOG.md`

Create log before edits.

## Mission

Close all three MAJOR findings.

### Canonical review validator
Implement one canonical Python review-record/chain validator that verifies:
- schema/version;
- review ID;
- candidate ID;
- candidate identity hash;
- artwork/grid identity;
- disposition;
- sequence;
- previous-review reference;
- bounded reason/note;
- chain continuity.

Candidate Inbox and all downstream review consumers must use only validated current review evidence. Corrupt/mismatched review files fail closed or are quarantined, never current truth.

### Candidate evidence UI
Render selected-candidate details from the canonical Inbox projection:
- candidate/artwork/grid identity;
- source/provenance/origin;
- dimensions;
- structural/QA evidence that actually exists;
- owner-review current state + evidence;
- solver/difficulty as NOT AVAILABLE where appropriate;
- immutable evidence/source references.

### Real Godot integration
Use at least two real candidates. Prove:
- NEEDS_REVIEW;
- ACCEPT;
- REJECT;
- second review preserves history;
- reload derives latest valid review;
- corrupt/tampered review fails closed;
- candidate/source bytes unchanged;
- unavailable fields remain unavailable.

Do not implement comparison/promotion. No TASKS edit.

Run full required regressions and finish with one R01 log-only commit.
