# SB-LFX-009-C001 — Search / Filter / Smart Collections Derived Views — Strict Audit Criteria

Target:
`SB-LFX-009 — Add scalable search/filter/smart collections as derived views over canonical source/candidate/level records. [EXTENSION]`

## Principle

Search and smart collections are derived queries, never duplicated state.

## Required domains

Search/filter across currently real records such as:
- OWNER_UPLOAD sources + Library label/tags;
- canonical candidates;
- owner-review evidence;
- dimensions;
- origin/provider;
- used colors/QA where canonical;
- solver/difficulty only where canonical;
- campaign/publication usage only where canonical.

Unavailable domains must be excluded or explicitly NOT AVAILABLE.

## Smart collections

Implement deterministic derived collections only where predicates can be grounded, for example:
- Needs Review;
- Owner Accepted;
- Owner Rejected;
- Imported Sources;
- structurally rejected candidates.

A collection like Ready for Production or Unused in Campaign must remain unavailable unless all required canonical evidence exists.

## BLOCKERS

FAIL if:
- membership is manually stored as truth;
- stale cache overrides canonical records;
- unavailable metrics are inferred;
- search mutates records;
- smart collection membership becomes acceptance/promotion;
- TASKS is read as asset data or edited.

## Scale / determinism

Results must have deterministic ordering, bounded queries, and stable filter semantics. Refresh must reflect canonical record changes.

## Real integration

Create multiple source/candidate/review records, prove combined filters, text search, smart collections, refresh after canonical changes, unavailable collection behavior, and no source/candidate mutation.

## PASS rule

PASS when discovery is a scalable deterministic view over canonical records with no duplicate membership truth.
