# SB-LF08-001-C001 — Strict Audit
Document role: INDEPENDENT CHATGPT STRICT AUDIT

## Result

CHANGES_REQUIRED / RESUME AND MANIFEST INTEGRITY NOT CLOSED

## Scope and evidence

- Live authority audited: `origin/main` at `a0c7fc7198c3b5f9692b8f962336e076108b3c7c`.
- Product implementation: `b535ed19da68684502c7e1a7d00b292d8a405dd9`, with later M08 contract changes through the live final SHA.
- Builder evidence: `cf54a0459c370082bca5705c47e81520fa6a6a00`; final master handoff: `a0c7fc7198c3b5f9692b8f962336e076108b3c7c`.
- Sources: [M08-001 criteria](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/a0c7fc7198c3b5f9692b8f962336e076108b3c7c/.hiveai/audit-criteria/SB-LF08-001-C001_ACCEPTED_COUNTS_LANE_CLASS_CADENCE_AUDIT_CRITERIA.md), [implementation](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/a0c7fc7198c3b5f9692b8f962336e076108b3c7c/src/scrubbots_pixel_factory/m08_batch.py), [builder log](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/a0c7fc7198c3b5f9692b8f962336e076108b3c7c/.hiveai/codex-logs/SB-LF08-001-C001_ACCEPTED_COUNTS_LANE_CLASS_CADENCE_CODEX_LOG.md).

## Findings

1. `BatchResult.from_dict()` accepts a self-consistent but inflated accepted history. `BatchResult.__post_init__()` does not enforce each lane's requested count, finite budget, contiguous attempt prefix, or exact attempt `plan_digest` binding when restoring a manifest. A forged history can therefore contain more accepted candidates than requested or more attempts than the lane budget.
2. `history_digest` is only shape-checked as a SHA-256. It is not recomputed from the restored plan, attempts and statistics, so a tampered history can carry an arbitrary replacement digest.
3. `_normalize_history()` permits `AttemptRecord.plan_digest is None`, which violates the exact-plan resume requirement. The accepted-entry path is plan-bound, but raw attempt-history resume is not fail-closed.
4. The focused tests prove ordinary cadence and several negative cases, but do not exercise these restored-manifest inflation and missing-plan-binding cases.

These are acceptance-boundary defects, not owner or unavailable gates. The builder's passing tests are evidence only and do not establish PASS.

## Required remediation

Make restored and resumed history enforce the same invariants as newly produced history: exact plan digest on every attempt, contiguous per-lane prefix, lane membership, finite budgets, accepted-count limits, canonical recomputed history digest, and no accepted-entry/history mismatch. Add adversarial tests for accepted-count inflation, over-budget history, arbitrary history digest, missing/wrong plan digest, and resume idempotence. Preserve accepted M08-002/003/004/005/010 behavior.

## Disposition

Not closed. Re-audit only after the complete authorized R01 batch.
