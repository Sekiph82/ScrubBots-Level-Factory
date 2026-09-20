# SB-LFX-016-C001 — Advisory Visual-Similarity Guard — Strict Audit

## VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Severity:
- BLOCKER: 1
- MAJOR: 3
- MINOR: 0
- NOTE: 1

## Audited chain

- Start: `d92a5a236dfb36b54e5513572a1b3a193d22179e`
- Actual implementation: `5061c14096eacc0d73d3bc687fee6402f32a4b8b`
- Actual task-final log-only: `1bbf65bcb33fc52593e8652527c27efc93a8ae39`

## Accepted implementation semantics

The Hamming-style logical-cell metric is local, deterministic in its arithmetic, records an algorithm name, score, distance and threshold, and has no automatic review/reject/promote side effect in the helper itself.

## BLOCKER-001 — exact/similarity evidence is not bound to canonical artifacts

`similarity(left, right, threshold)` accepts arbitrary caller-provided mappings containing:
- candidate_id;
- width/height;
- cells;
- grid_hash.

It does not load or validate canonical candidate/revision artifacts.

Worse, `EXACT_DUPLICATE` is returned solely when:

`left.grid_hash == right.grid_hash`

without recomputing either hash from the supplied cells or binding the identity to canonical bytes/grid evidence.

A caller can therefore provide different logical cells with the same claimed grid hash and obtain `EXACT_DUPLICATE`.

This violates the criteria's exact-identity authority and identity-binding requirements.

### Required remediation

Expose similarity by canonical artifact/revision IDs, load verified representations internally, recompute/verify logical-grid hashes, and use exact canonical identity for EXACT_DUPLICATE. Arbitrary caller mappings must not establish identity truth.

## MAJOR-001 — Similarity Studio surface is only a placeholder

`FactoryStudioSimilarity` contains explanatory text only.

It provides no:
- candidate/revision selectors;
- similarity action;
- score/distance/threshold display;
- artifact identity display;
- comparison/search/candidate integration.

The criteria require advisory evidence to be visible in Candidate/Comparison/Search surfaces.

## MAJOR-002 — required acceptance matrix is incomplete

The focused unit test covers exact/one-cell-near/different examples only.

Missing required proof includes:
- deterministic repeatability assertion;
- threshold boundary behavior;
- stale identity after edit/revision;
- canonical palette/color-change cases bound to real artifacts;
- explicit proof that owner-review/candidate disposition files remain unchanged;
- real Godot runtime integration.

## MAJOR-003 — threshold and representation contract are insufficiently validated

The helper accepts any numeric threshold without enforcing a canonical bounded range/policy version, and accepts arbitrary cell values/dimensions without validating canonical palette membership, exact cell count or representation hash.

### Required remediation

Define and validate a versioned similarity policy, bounded threshold, legal canonical logical representation and representation-hash binding.

## NOTE — master batch summary SHA mismatch

The master batch log recorded different SB-LFX-016 implementation/publication SHAs. The task's own builder log and GitHub commit search establish the actual chain above. Correct the batch/remediation evidence so future audits do not depend on stale summary SHAs.

## Disposition

`SB-LFX-016` remains open pending remediation and re-audit.
