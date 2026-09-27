# SB-LF09-001-C001-R02 — Complete Cross-Candidate Artifact Identity Remediation — Strict Audit Criteria

PASS requires the R01 selector to remain versioned, deterministic, explicitly
opt-in, finite, offline, and isolated from production while closing the
remaining identity-policy finding.

1. The versioned policy must enumerate every `CandidateEvidence` artifact
   identity admitted to selection, including optional preview and mutation
   reference/digest pairs, or explicitly declare a versioned shared-identity
   exception for any field that is intentionally shareable.
2. Every policy-listed candidate-specific reference and digest collision across
   distinct candidates must fail closed before ranking. Missing or malformed
   reference/digest pairs must also fail closed.
3. Any shared-identity exception must appear in immutable selection provenance
   and have a focused positive test. Unlisted or implicit sharing is a failure.
4. Existing R01 positive selection, verified missing/stale bytes, deterministic
   replay, finite-budget, opt-in isolation, duplicate, lineage, and
   no-production-promotion tests must remain green.
5. Retained M08/M07 regressions, full pytest, compileall, Godot headless boot,
   diff/protected-file checks, and truthful unavailable-capability reporting are
   required. No owner-only, native-device, physical, subjective, or unavailable
   bridge acceptance may be claimed.
