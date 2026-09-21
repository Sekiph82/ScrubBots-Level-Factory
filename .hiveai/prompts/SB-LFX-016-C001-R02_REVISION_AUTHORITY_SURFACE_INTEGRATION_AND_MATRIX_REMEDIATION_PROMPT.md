# SB-LFX-016-C001-R02 — Revision Authority + Surface Integration + Matrix Remediation

Work only on:
`.hiveai/audits/SB-LFX-016-C001-R01_CANONICAL_SIMILARITY_IDENTITY_AND_RUNTIME_REMEDIATION_STRICT_AUDIT.md`

Create log first:
`.hiveai/codex-logs/SB-LFX-016-C001-R02_REVISION_AUTHORITY_SURFACE_INTEGRATION_AND_MATRIX_REMEDIATION_CODEX_LOG.md`

Dependency rule:
- consume only the fully validated revision reader produced by SB-LFX-012-R02;
- if revision validation is not available, revision-backed similarity must be STALE/NOT_AVAILABLE.

Integrate canonical advisory similarity evidence into existing Candidate and Comparison/Search surfaces without recomputing it in GDScript.

Extend real runtime matrix:
- repeated identical comparison -> deterministic identical evidence fields;
- threshold boundary;
- explicit color/palette-cell change case;
- valid revision then edited/new revision causing stale/changed identity behavior;
- snapshot owner-review/candidate disposition files before and after similarity and prove unchanged;
- exact duplicate remains stronger than POSSIBLE_SIMILAR.

Keep local/offline/advisory only. No TASKS edit.
