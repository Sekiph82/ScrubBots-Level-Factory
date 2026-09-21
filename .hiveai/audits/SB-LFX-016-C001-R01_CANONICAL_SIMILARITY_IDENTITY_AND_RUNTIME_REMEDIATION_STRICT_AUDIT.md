# SB-LFX-016-C001-R01 — Canonical Similarity Identity + Runtime Remediation — Strict Audit

## VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Severity:
- BLOCKER: 0
- MAJOR: 3
- MINOR: 0
- NOTE: 1

## Audited chain

- R01 start: `0eb2a401781c407dc4d3c3af98ee9f586960bcdf`
- R01 implementation: `910e53c88972b0556e3663ca3be90e22b5216edb`
- R01 terminal log-only: `18d92cfc42d49c3289c9d9d1a7a2d81ab61b7870`

## Material improvements

R01 closes the original arbitrary-caller identity blocker for canonical candidates:
- launcher operation now accepts canonical IDs rather than caller-supplied cells/hashes;
- candidate bundle identity is re-read and verified;
- logical grid hashes are recomputed/checked;
- arbitrary representation input is rejected;
- threshold is bounded to [0,1];
- versioned `SIMILARITY_POLICY_V1` is emitted;
- exact / near / distinct comparisons are advisory only;
- real Studio Compare action exists;
- tampered revision cells/hash are rejected in the tested path.

## MAJOR-001 — revision-backed similarity inherits the unresolved weak revision-chain authority

`_similarity_artifact()` resolves revision IDs through `load_revision()`.

SB-LFX-012-R01 remains CHANGES_REQUIRED because `load_revision()/list_revisions()` do not fully validate:
- revision content identity;
- source artwork binding;
- parent/sequence chain;
- baseline semantics;
- immutable record digest.

Similarity recomputes only the selected revision's logical grid hash.

Therefore a revision record that is self-consistent at the cells/grid-hash level but invalid in its canonical lineage can still be accepted as a similarity artifact.

### Required remediation

Consume only the fully validated revision-chain reader from the eventual SB-LFX-012 follow-up. Until then, revision-backed similarity must be unavailable/stale rather than trusting a partially validated revision record.

## MAJOR-002 — advisory similarity is not integrated into Candidate / Comparison / Search surfaces

The criteria require advisory evidence to be visible in Candidate/Comparison/Search surfaces.

R01 implements only the dedicated `FactoryStudioSimilarity` page.

No candidate detail, side-by-side comparison, or search result surface consumes or displays the identity-bound similarity evidence.

### Required remediation

Expose the same canonical advisory evidence in at least the relevant Candidate and Comparison/Search views without recomputing it in GDScript.

The wording must remain explicit that similarity never changes review/readiness/production disposition.

## MAJOR-003 — required acceptance matrix is still incomplete

The real R01 integration proves:
- exact duplicate;
- arbitrary input rejection;
- one-cell near duplicate;
- distinct candidate;
- one tampered revision rejection;
- UI invocation.

It does not explicitly prove:
- deterministic repeated identical comparison returns byte/field-equivalent evidence;
- threshold-boundary behavior;
- palette/color-change case at a known threshold;
- stale identity after a legitimate revision/edit transition;
- candidate disposition/review files remain byte-identical before/after similarity;
- no automatic review mutation in real runtime.

### Required remediation

Extend the existing real integration with those exact assertions.

## NOTE

The global remediation-batch suite retains the unrelated protected tracker-contract failure.

## Disposition

`SB-LFX-016` remains open pending R02.
