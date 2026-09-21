# SB-LFX-013-C001-R04 — Stage-Aware Retry Without Successful-Stage Reexecution

Work only on:
`.hiveai/audits/SB-LFX-013-C001-R03_CANONICAL_ONLY_FAILURE_TRUTH_AND_RETRY_EVIDENCE_REMEDIATION_STRICT_AUDIT.md`

Create builder log first:
`.hiveai/codex-logs/SB-LFX-013-C001-R04_STAGE_AWARE_RETRY_CONTINUATION_CODEX_LOG.md`

Retain all accepted R03 behavior:
- canonical-scanner-only Failure Inbox truth;
- no product `record-failure` dispatch;
- no free-form retry fallback;
- immutable originating evidence;
- append-only retry attempt lineage;
- successful control exclusion;
- unavailable SOLVE/DIFFICULTY disabled.

The remaining finding is execution semantics.

Current behavior must not remain:
- collect old PASS stages into `reused_successful_stage_evidence`;
- then call full `run_pipeline()` from the beginning.

Required closure:

1. Define a deterministic stage-aware retry plan from the canonical originating pipeline record and failed stage.
2. Carry forward successful prior stages only by immutable reference/digest. Do not execute their canonical operations again.
3. Execute only the eligible failed stage/continuation and later applicable stages.
4. If the failed stage has no safe partial-stage execution contract, mark that failure NOT RETRYABLE / NOT_AVAILABLE rather than invoking full pipeline restart.
5. Retry evidence must record:
   - parent failure ID;
   - originating pipeline/run ID;
   - reused prior stage IDs/digests;
   - newly attempted stage(s);
   - output identity if any;
   - final retry disposition.
6. Prove with real integration that no new stage execution/evidence is created for prior PASS/NOT_APPLICABLE stages.
7. Prove original pipeline and failure evidence bytes remain unchanged.
8. Prove successful controls remain absent from retryable failure truth.
9. Preserve disabled UI/reason for unavailable stages.

Do not weaken pipeline immutability. Do not edit TASKS.md.

Publish one R04 implementation SHA and one terminal log-only SHA.
