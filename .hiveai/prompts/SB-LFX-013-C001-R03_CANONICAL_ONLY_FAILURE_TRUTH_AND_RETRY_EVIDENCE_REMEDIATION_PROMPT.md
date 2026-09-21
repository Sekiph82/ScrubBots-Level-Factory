# SB-LFX-013-C001-R03 — Canonical-Only Failure Truth + Retry Evidence Remediation

Work only on:
`.hiveai/audits/SB-LFX-013-C001-R02_CANONICAL_FAILURE_DISCOVERY_AND_RETRY_UI_REMEDIATION_STRICT_AUDIT.md`

Create builder log first:
`.hiveai/codex-logs/SB-LFX-013-C001-R03_CANONICAL_ONLY_FAILURE_TRUTH_AND_RETRY_EVIDENCE_REMEDIATION_CODEX_LOG.md`

Retain the R02 derived Failure Inbox, evidence binding and eligibility UI.

Required closure:

1. Remove `record-failure` from the product/Studio launcher path, or isolate it behind a test-only boundary that cannot create product Failure Inbox truth.
2. Remove the production retry fallback that loads caller-created free-form failure JSON when an ID is not present in the verified canonical scanner.
3. Product retry must accept only a failure entry derived from canonical validation/pipeline/batch/job evidence.
4. Generate a real canonical failure/rejection/inconclusive case and a successful control case.
5. Prove successful control work never appears as retryable failure truth.
6. Snapshot the originating canonical failure evidence bytes/hash before retry; prove unchanged after retry.
7. Prove a retry creates a separate append-only attempt with parent failure/evidence identity.
8. Prove already-successful prior stage identities/evidence are reused and are not silently rerun.
9. Keep SOLVE/DIFFICULTY unavailable stages non-retryable and prove the Studio Retry action is disabled with the reason.

No fabricated failure authority. No TASKS edit.

Publish one R03 implementation SHA and one terminal log-only SHA.
