# SB-LF09-001-C001-R01 — Evidence Availability and Cross-Candidate Identity Remediation — Strict Audit Criteria

PASS requires the existing experimental selector to remain versioned,
deterministic, explicitly opt-in, finite, offline, and isolated from production
generation/publication while closing both audit findings:

1. Required artifact evidence must be represented by a canonical verified
   evidence contract or verified through `m08_batch.verify_artifact_set()` (or a
   strictly equivalent boundary). Missing bytes, unavailable references, stale
   digest/reference pairs, malformed evidence, and invalid lineage must fail
   closed before ranking.
2. The versioned policy must define all cross-candidate artifact identity rules.
   Candidate-specific digest/reference collisions must fail closed. Any
   intentionally shareable identity must be explicit in policy/provenance and
   covered by a positive test; implicit sharing is not acceptable.
3. Existing positive, deterministic replay, finite-budget, opt-in-isolation,
   duplicate, lineage, and no-production-promotion tests must remain green.
4. Retained M08/M07 regressions, full pytest, compileall, Godot headless boot,
   diff/protected-file checks, and truthful unavailable-capability reporting are
   required. No owner-only, native-device, physical, subjective, or unavailable
   bridge acceptance may be claimed.
