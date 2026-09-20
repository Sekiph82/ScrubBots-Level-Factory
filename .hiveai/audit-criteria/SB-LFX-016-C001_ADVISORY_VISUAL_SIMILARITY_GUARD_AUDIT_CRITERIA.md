# SB-LFX-016-C001 — Advisory Visual-Similarity Guard — Strict Audit Criteria

Target:
`SB-LFX-016 — Add advisory visual-similarity guard for near-duplicate artwork/candidates while retaining exact identity checks and avoiding silent auto-reject policy. [EXTENSION]`

## Principle

Similarity evidence is advisory. Exact SHA/grid identity remains authoritative for exact duplicates. Similarity never auto-rejects, auto-ranks or auto-promotes.

## Required algorithm contract

Use a deterministic local versioned algorithm over an explicitly defined canonical raster/logical representation.

Evidence must record:
- algorithm/policy version;
- left/right artifact identities;
- representation hashes;
- similarity score/distance;
- threshold;
- disposition such as DISTINCT / POSSIBLE_SIMILAR / EXACT_DUPLICATE.

The algorithm must be reproducible offline and must not call external vision/AI services.

## BLOCKERS

FAIL if:
- POSSIBLE_SIMILAR silently rejects work;
- similarity replaces exact duplicate identity;
- algorithm uses mutable presentation screenshots instead of canonical representation;
- scores are unbound to artifact identities;
- threshold changes rewrite old evidence;
- semantic/content claims exceed what the pixel metric proves;
- network/provider inference is added;
- TASKS is edited.

## UI

Show advisory evidence in Candidate/Comparison/Search surfaces with clear language that owner review decides significance.

## Real tests

Include:
- exact duplicate;
- one/few-pixel near duplicate;
- materially different artwork;
- palette/color changes;
- deterministic repeatability;
- threshold boundary;
- stale identity after edit/revision;
- proof no candidate disposition/review state changes automatically.

## PASS rule

PASS when near-duplicate evidence is deterministic, identity-bound and advisory only.
