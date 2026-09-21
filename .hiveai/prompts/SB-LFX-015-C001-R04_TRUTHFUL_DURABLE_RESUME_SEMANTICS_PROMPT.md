# SB-LFX-015-C001-R04 — Truthful Durable Resume Semantics

Work only on:
`.hiveai/audits/SB-LFX-015-C001-R03_REAL_RECOVERY_RESUME_COORDINATOR_REMEDIATION_STRICT_AUDIT.md`

Create builder log first:
`.hiveai/codex-logs/SB-LFX-015-C001-R04_TRUTHFUL_DURABLE_RESUME_SEMANTICS_CODEX_LOG.md`

Retain all accepted R03 behavior:
- typed allowlist session schema;
- session integrity digest;
- canonical reference validation;
- fresh Studio teardown/reinstantiate test;
- immutable original pipeline evidence;
- idempotent recovery evidence;
- missing/corrupt/secret-bearing fail-closed behavior;
- batch-only NOT_RESUMABLE behavior.

The remaining finding is the meaning of RESUMED.

Current post-CANDIDATE `CANDIDATE_REENTRY` alone must not be called RESUMED unless real remaining canonical work advances beyond the interruption boundary.

Choose the truthful implementation supported by current repository capability:

### Option A — real continuation

If a genuinely executable pipeline stage can be interrupted before completion:
1. establish a durable interruption before that executable stage;
2. recovery must execute that exact remaining stage once;
3. previously successful stages are reused by reference/digest and not rerun;
4. repeated restore returns the same immutable recovery evidence and does not execute work twice;
5. prove no duplicate source/candidate/job creation.

### Option B — truthful non-resumability

If no current stage can safely continue after the interruption boundary:
1. do not fabricate a resume stage;
2. classify the restored pipeline as `NOT_RESUMABLE` or `NEEDS_OPERATOR_ACTION`;
3. explain the canonical reason, e.g. next stage unavailable;
4. preserve successful prior-stage evidence and operator context;
5. do not claim `RESUMED`.

In either option:
- RESUMED must mean real canonical work advanced beyond the interrupted boundary;
- RETRIED remains an explicit new retry attempt after failure;
- session remains non-authoritative over source/candidate/job truth;
- real restart integration must inspect the actual recovery disposition and evidence.

Do not invent solver/difficulty capability. Do not edit TASKS.md.

Publish one R04 implementation SHA and one terminal log-only SHA.
