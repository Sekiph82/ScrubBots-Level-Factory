# SB-LFX-016-C001-R02 — Content-Bound Revision Similarity + Surface Integration Remediation

Work only on:
`.hiveai/audits/SB-LFX-016-C001-R01_CANONICAL_SIMILARITY_IDENTITY_AND_RUNTIME_REMEDIATION_STRICT_AUDIT.md`

Original criteria:
`.hiveai/audit-criteria/SB-LFX-016-C001_ADVISORY_VISUAL_SIMILARITY_GUARD_AUDIT_CRITERIA.md`

Builder log:
`.hiveai/codex-logs/SB-LFX-016-C001-R02_CONTENT_BOUND_REVISION_SIMILARITY_AND_SURFACE_INTEGRATION_REMEDIATION_CODEX_LOG.md`

Create log before edits.

## Dependency

SB-LFX-012-R02 must be implemented earlier in the R02 batch.

Reuse its canonical revision validator/content-derived identity. Do not build a second competing revision validator.

## Mission

Close the remaining blocker and two majors.

### Immutable revision identity
Similarity may resolve revisions only through the fully validated SB-LFX-012-R02 revision chain.

Evidence must bind:
- revision immutable ID/digest;
- candidate/source identity;
- recomputed logical representation hash.

Any mutation under an old revision identity must fail closed.

### Surface integration
Keep the dedicated Similarity page, but also expose read-only advisory summaries/links in:
- Candidate Inbox/detail;
- Side-by-Side Comparison;
- Search/Discovery results where relevant.

Do not recompute in GDScript. Do not rank/reject/accept automatically.

### Complete runtime matrix
Prove:
1. candidate exact duplicate;
2. one/few-cell near duplicate;
3. materially different art;
4. canonical color-change case;
5. repeated identical comparison gives deterministic equal result;
6. threshold exact boundary and one side of boundary;
7. valid old revision vs new revision identities after edit/branch;
8. tampered revision identity fails closed;
9. owner-review/candidate disposition evidence bytes unchanged before/after similarity;
10. advisory evidence appears in Candidate/Comparison/Search surfaces;
11. no auto-review/readiness/promotion mutation.

Run full regressions. One R02 implementation + terminal log-only commit. Do not edit TASKS.md.
