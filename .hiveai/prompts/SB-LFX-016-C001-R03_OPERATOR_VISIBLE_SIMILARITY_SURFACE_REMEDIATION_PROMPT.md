# SB-LFX-016-C001-R03 — Operator-Visible Similarity Surface Remediation

Work only on:
`.hiveai/audits/SB-LFX-016-C001-R02_REVISION_AUTHORITY_SURFACE_INTEGRATION_AND_MATRIX_REMEDIATION_STRICT_AUDIT.md`

Dependency:
SB-LFX-012-R03 must already be complete before this task is finalized.

Create builder log first:
`.hiveai/codex-logs/SB-LFX-016-C001-R03_OPERATOR_VISIBLE_SIMILARITY_SURFACE_REMEDIATION_CODEX_LOG.md`

Retain the accepted deterministic local `SIMILARITY_POLICY_V1`, canonical identity binding, revision validation and advisory-only semantics.

Required UI closure:

1. Comparison continues to show the real canonical pair result.
2. Candidate surface must provide a bounded canonical peer-selection/compare path, or visibly show NOT AVAILABLE with the reason/action required to select a peer. A generic hidden backend placeholder is insufficient.
3. Search surface must visibly render `similarity_advisory` state/evidence for the relevant result context. The current renderer must not silently discard the backend field.
4. Candidate / Comparison / Search language must explicitly state that similarity is advisory only and owner review decides significance.
5. Never recompute similarity in GDScript. All scores/evidence come from the canonical backend.
6. No similarity outcome may auto-reject, auto-rank, auto-promote or mutate review/readiness.

Real runtime must inspect rendered/surface state, not only backend dictionaries, and retain:
- exact duplicate;
- near duplicate;
- distinct/color-change;
- deterministic repeat;
- threshold boundary;
- validated revision transition;
- unchanged owner-review/candidate evidence.

No TASKS edit.

Publish one R03 implementation SHA and one terminal log-only SHA.
