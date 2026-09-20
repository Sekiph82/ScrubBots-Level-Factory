# SB-LFX-016-C001-R01 — Canonical Similarity Identity + Runtime Remediation — Strict Audit

## VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Severity:
- BLOCKER: 1
- MAJOR: 2
- MINOR: 0
- NOTE: 1

## Audited chain

- R01 start: `0eb2a401781c407dc4d3c3af98ee9f586960bcdf`
- R01 implementation: `910e53c88972b0556e3663ca3be90e22b5216edb`
- R01 terminal log-only: `18d92cfc42d49c3289c9d9d1a7a2d81ab61b7870`

## Material improvements

R01 closes a large part of the original identity-boundary defect:
- Studio/launcher no longer accepts arbitrary caller-supplied cells/grid hashes as the product similarity authority;
- candidate/revision IDs are resolved internally;
- candidate bundles are read through canonical bundle validation;
- candidate artwork SHA and grid hash are verified;
- revision working-grid hash is recomputed from stored cells;
- threshold is bounded to 0..1;
- a versioned `SIMILARITY_POLICY_V1` is exposed;
- Studio now has real left/right selectors and an advisory Compare action;
- real Godot integration covers candidate exact duplicate, arbitrary-input rejection, one-cell near duplicate, distinct candidate comparison, UI invocation and a grossly corrupt revision record.

No auto-review/reject/promote action is introduced.

## BLOCKER-001 — revision similarity evidence is still not bound to an immutable revision identity

The R01 resolver calls `load_revision()` and then verifies:

`working_grid_hash == logical_grid_hash(width, height, cells)`

However SB-LFX-012-R01 remains non-fail-closed:
- revision ID is sequence-based, not content-derived;
- revision record has no independently verified content digest;
- list/load does not verify source artwork identity, parent chain, sequence or immutable record content.

Therefore a revision file can be modified by changing:
- `cells`; and
- `working_grid_hash`

consistently while keeping the same `revision_id`.

`_similarity_artifact()` will then accept that modified representation under the same artifact identity.

The criteria explicitly make **scores unbound to artifact identities** a blocker.

### Required follow-up

Depend on the remediated SB-LFX-012 canonical revision validator/content identity:
- revision ID or revision digest must bind exact immutable revision content;
- similarity must load only a fully validated revision chain record;
- evidence must record that immutable revision identity/digest;
- any content mutation under the old revision identity must fail closed.

Do not add an independent competing revision validator inside similarity.

## MAJOR-001 — advisory evidence is not exposed in Candidate / Comparison / Search surfaces

The authoritative criteria require advisory similarity evidence to be shown in Candidate/Comparison/Search surfaces.

R01 adds a dedicated `FactoryStudioSimilarity` page only.

The Candidate Inbox, side-by-side Comparison and Search/Discovery surfaces do not display:
- existing similarity evidence;
- near-duplicate advisory markers;
- linked pair identity/score/threshold.

### Required follow-up

Integrate read-only advisory similarity summaries/links into the appropriate existing Candidate/Comparison/Search views. Do not recompute similarity in GDScript and do not auto-rank or auto-reject.

## MAJOR-002 — required acceptance matrix remains incomplete

The real R01 integration proves useful core cases but does not explicitly prove:
- repeated identical comparison returns deterministic byte/value-equivalent evidence;
- exact threshold-boundary behavior;
- materially different canonical palette/color-change scenario beyond one near-cell mutation;
- candidate/review disposition records remain byte-identical before/after similarity;
- stale identity after a legitimate edit/new revision, rather than only replacing the revision JSON with malformed `{"tampered":true}`.

### Required follow-up

Extend the real runtime test with:
1. deterministic repeated comparison equality;
2. score exactly at / immediately across the configured threshold;
3. canonical color-change case;
4. snapshot owner-review/candidate evidence before and after comparison;
5. old-vs-new revision identity behavior after a legitimate revision change/branch.

## Publication / regression

Task-final publication is log-only.

Builder reports compileall PASS and real canonical similarity integration PASS. The remediation-batch global suite retains the unrelated protected tracker-contract failure.

## NOTE

R01 correctly removed the most dangerous arbitrary-representation product path. The remaining blocker is specifically the unresolved immutable revision-identity dependency inherited from SB-LFX-012.

## Disposition

`SB-LFX-016` remains open pending revision-identity hardening plus advisory-surface/runtime follow-up.
