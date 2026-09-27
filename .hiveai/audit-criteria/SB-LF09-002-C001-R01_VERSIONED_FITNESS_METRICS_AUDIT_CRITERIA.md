# SB-LF09-002-C001-R01 — Fitness Result Integrity Remediation

Document role: STRICT AUDIT CRITERIA

PASS requires the closed LF09-002 fitness contract to reject caller-authored
or ambiguous result containers at every public reconstitution boundary while
preserving deterministic offline experimental behavior.

1. `FitnessEvaluation` rejects duplicate candidate IDs and duplicate lineage
   identities during direct construction and `from_dict()` restoration, while
   retaining strict canonical candidate ordering and self-digest checks.
2. A caller cannot alter metric values, recompute the result/evaluation
   self-digests, preserve candidate ID/lineage/policy fields, and retrieve the
   forged result through any public evaluation lookup. Retrieval must
   recompute or equivalently verify against the exact accepted artifact bytes.
3. Missing, malformed, stale, cross-candidate, and policy-mismatched fitness
   bindings fail closed. The exact positive candidate validation and replay
   path remains deterministic and byte-identical.
4. Finite integer basis-point scoring, canonical policy/catalog serialization,
   candidate-specific artifact identity checks, explicit experimental opt-in,
   source-art immutability, and no-production-promotion boundaries remain
   unchanged.
5. Focused tests cover the two audit defects, cross-candidate/stale evidence,
   policy binding, deterministic replay, and the retained positive path.
6. Retained LF09-001 and M07/M08 regression tests remain green. Full pytest,
   compileall, Godot headless boot, diff/protected-file checks, and truthful
   unavailable-capability reporting pass. No owner-only, native-device,
   physical, subjective, or unavailable bridge acceptance may be claimed.

