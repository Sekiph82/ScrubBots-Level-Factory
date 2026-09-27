# SB-LF08-009-C001 — Strict Audit
Document role: INDEPENDENT CHATGPT STRICT AUDIT

## Result

CHANGES_REQUIRED / TERMINAL HISTORY RESTORE IS NOT FAIL-CLOSED

## Scope and evidence

- Live audited SHA: `a0c7fc7198c3b5f9692b8f962336e076108b3c7c`.
- Product task commit: `4c1279dcc8356da3750a9976442243f78ca5452d`; builder log: `a69072a402a2afa669fc660e45b3931a9c541e13`.
- Builder reported full regression `1055 passed, 2 skipped`, compileall, Godot headless and diff checks; the final master handoff is [here](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/a0c7fc7198c3b5f9692b8f962336e076108b3c7c/.hiveai/codex-logs/SB-LF08-C001_MASTER_BATCH_CODEX_LOG.md). These are builder evidence, not independent acceptance.
- Sources: [M08-009 criteria](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/a0c7fc7198c3b5f9692b8f962336e076108b3c7c/.hiveai/audit-criteria/SB-LF08-009-C001_HIGH_REJECTION_STRESS_SAFETY_AUDIT_CRITERIA.md), [implementation](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/a0c7fc7198c3b5f9692b8f962336e076108b3c7c/src/scrubbots_pixel_factory/m08_batch.py).

## Findings

1. The high-rejection hardening reconciles counters for the in-memory run, but `BatchResult.from_dict()` does not reapply finite budgets, contiguous-prefix rules, exact per-attempt plan binding, requested-count caps or a recomputed history digest. A forged terminal EXHAUSTED/COMPLETE history can therefore exceed a lane budget or accepted target while remaining structurally self-consistent.
2. The required stress matrix is not independently established by the focused tests: the committed suite does not cover every specified combination of repeated duplicates, lane-specific unavailable/inconclusive terminal truth, source-linked preservation, and tampered high-rejection restore semantics.
3. Because the restored manifest can be inflated, rerun/idempotence claims apply only to honest histories and do not prove corruption-safe terminal reruns.

## Required remediation

Close the shared restore/manifest invariants first, then add deterministic offline tests for every required stress row, including tampered history/counters, one-lane terminal asymmetry, interruption/resume after long rejection history, COMPLETE and EXHAUSTED reruns, and source-linked preservation. Keep finite budgets and all acceptance thresholds unchanged.

## Disposition

Not closed. Re-audit only after the complete authorized R01 batch.
