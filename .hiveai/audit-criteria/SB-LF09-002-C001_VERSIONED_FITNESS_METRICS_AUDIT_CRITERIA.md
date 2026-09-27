# SB-LF09-002-C001 — Versioned Fitness Metrics

Document role: STRICT AUDIT CRITERIA

PASS requires the next M09 experimental lane to expose a truthful,
versioned, deterministic fitness contract without changing accepted evidence
or production behavior.

1. A closed metric catalog and versioned fitness policy must be explicit,
   canonically serializable, and included in the policy digest. Each metric's
   meaning, units or normalization, direction, and aggregation are stated.
2. Fitness results must be deterministically derived from accepted candidate
   evidence and the selected policy. Repeated evaluation with identical input
   must produce identical canonical values, digests, and ordering.
3. Every fitness result must bind to the exact candidate lineage identity and
   fitness-policy digest. Missing, malformed, caller-forged, stale, or
   cross-candidate fitness bindings must fail closed.
4. The metric path must remain finite, offline, side-effect free, explicitly
   experimental, and isolated from production generation/publication. It must
   not relabel difficulty, replace gameplay semantics, mutate source art, or
   bypass M03/M04/M05/M07 acceptance.
5. Focused tests must cover catalog/version canonicalization, deterministic
   replay, lineage and policy binding, malformed/missing metrics, finite
   evaluation, and production isolation. Existing LF09-001 and retained
   M07/M08 regressions remain green.
6. Full pytest, compileall, Godot headless boot, diff/protected-file checks,
   and truthful unavailable-capability reporting must pass. No owner-only,
   native-device, physical, subjective, or unavailable bridge acceptance may
   be claimed.
