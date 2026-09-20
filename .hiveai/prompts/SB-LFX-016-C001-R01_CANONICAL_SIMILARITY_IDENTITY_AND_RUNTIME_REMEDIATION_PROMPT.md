# SB-LFX-016-C001-R01 — Canonical Similarity Identity + Runtime Remediation

Work only on:
.hiveai/audits/SB-LFX-016-C001_ADVISORY_VISUAL_SIMILARITY_GUARD_STRICT_AUDIT.md

Original criteria:
.hiveai/audit-criteria/SB-LFX-016-C001_ADVISORY_VISUAL_SIMILARITY_GUARD_AUDIT_CRITERIA.md

Builder log:
.hiveai/codex-logs/SB-LFX-016-C001-R01_CANONICAL_SIMILARITY_IDENTITY_AND_RUNTIME_REMEDIATION_CODEX_LOG.md

Create the builder log before edits.

## Mission
Close BLOCKER-001 and MAJOR-001..003.

### Canonical identity boundary
Similarity requests must select canonical candidate/revision artifact IDs, not submit arbitrary cells/grid hashes as authority.
Load and validate canonical logical representations internally. Recompute/verify grid hashes from exact cells.
EXACT_DUPLICATE requires authoritative exact identity/equality, never just equal caller-supplied hash strings.

### Versioned policy
Define a versioned similarity policy with bounded threshold and legal canonical representation requirements.
Reject invalid dimensions, cell counts, palette IDs and unverified identities.
Keep exact duplicate identity stronger than advisory similarity.

### Real UI
Add real candidate/revision selectors and an advisory Compare Similarity action.
Display algorithm version, left/right identities, representation hashes, distance, score, threshold and disposition.
Expose advisory evidence in Candidate/Comparison/Search where appropriate, with clear no-auto-reject wording.

### Real tests
Cover exact duplicate, one/few-cell near duplicate, materially different art, color changes, deterministic repeatability, threshold boundary, stale edited revision, canonical identity tampering and proof that review/candidate disposition does not change.

Correct stale master-batch SHA metadata in R01 evidence. No network/provider calls. No TASKS edit.

Run full regressions and publish one R01 terminal log-only commit.