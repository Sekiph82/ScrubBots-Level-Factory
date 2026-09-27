# SB-LF08-006-C001 — Strict Audit
Document role: INDEPENDENT CHATGPT STRICT AUDIT

## Result

CHANGES_REQUIRED / ARTIFACT PROVENANCE SET IS INCOMPLETE

## Scope and evidence

- Live audited SHA: `a0c7fc7198c3b5f9692b8f962336e076108b3c7c`.
- Product task commit: `45521d502a8b9dac5650290a9554e4ffd2483149`; builder log: `ab27ea0442b0573d30ebd694172f43f825d26562`.
- Sources: [M08-006 criteria](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/a0c7fc7198c3b5f9692b8f962336e076108b3c7c/.hiveai/audit-criteria/SB-LF08-006-C001_ACCEPTED_BATCH_RESULT_ARTIFACT_SET_AUDIT_CRITERIA.md), [artifact implementation](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/a0c7fc7198c3b5f9692b8f962336e076108b3c7c/src/scrubbots_pixel_factory/m08_batch.py), [builder log](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/a0c7fc7198c3b5f9692b8f962336e076108b3c7c/.hiveai/codex-logs/SB-LF08-006-C001_ACCEPTED_BATCH_RESULT_ARTIFACT_SET_CODEX_LOG.md).

## Findings

1. `CandidateEvidence` carries generation request, generation result and generation metadata digests, but `verify_artifact_set()` verifies only `generation_ref` against `generation_metadata_digest`. The request and result digests have no referenced immutable bytes or cross-check, so the required complete generation identity is not proven.
2. The manifest exposes requested, attempted and accepted counts per lane, but rejection, duplicate, unavailable, inconclusive and error reconciliation is only global. The strict contract requires per-lane requested-versus-attempted/generated-versus-accepted and rejection/inconclusive/unavailable statistics in the deterministic batch result.
3. The batch-result restore path inherits the M08-001 defects: arbitrary `history_digest`, missing exact plan binding on raw attempts, no finite-budget enforcement, and no requested-count cap. Therefore a forged result can be a self-consistent accepted artifact set over an inflated history.
4. Digest equality alone does not establish that the bytes represented by each reference belong to the same candidate/source/art lineage. The contract needs an explicit canonical cross-binding record (or the accepted existing artifact identity contract) for the generation request/result/metadata and all candidate artifacts.

Safe relative references and no-regeneration behavior are present, but these are necessary conditions only.

## Required remediation

Extend the accepted-entry/artifact contract with separately verifiable generation request/result/metadata identities and an exact lineage binding. Materialize deterministic per-lane statistics and recompute all manifest digests from canonical bytes/history. Add cross-candidate swap, stale generation identity, missing request/result bytes, per-lane-statistics tamper, over-budget and accepted-count inflation tests.

## Disposition

Not closed. Re-audit only after the complete authorized R01 batch.
