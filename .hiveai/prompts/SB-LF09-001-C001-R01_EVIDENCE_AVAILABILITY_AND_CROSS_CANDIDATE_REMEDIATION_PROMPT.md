# SB-LF09-001-C001-R01 — Evidence Availability and Cross-Candidate Identity Remediation

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main

## Authorization

Remediate only the two findings from the independent audit of
`SB-LF09-001-C001`. Preserve the accepted experimental-selection scope,
M00-M08 evidence, the root `TASKS.md`, and `.hiveai/audits/**`. Do not begin
SB-LF09-002 or any later M09, Content Platform, main-game, provider, or
production-publication work.

## Required remediation

1. Make the experimental selector fail closed when any required evidence is
   unavailable, missing, or stale. Use the existing canonical
   `m08_batch.verify_artifact_set()` boundary or an equivalent typed verified
   evidence contract. Do not infer availability from hash-shaped strings alone.
2. Define the complete cross-candidate identity policy for every required
   artifact digest/reference. Reject collisions for candidate-specific
   identities. If a field is intentionally shareable, encode the exception in
   the versioned policy and immutable selection provenance and test it
   explicitly.
3. Preserve deterministic replay, finite population/generation/evaluation
   bounds, exact opt-in isolation, source-art immutability, M03/M04/M05/M07
   acceptance gates, and no production promotion.
4. Add focused tests for missing artifact bytes, stale digest/reference pairs,
   each prohibited cross-candidate identity collision, and any explicitly
   allowed shared identity. Retain all existing focused tests.

## Boundaries

- Do not edit `TASKS.md` or `.hiveai/audits/**`.
- Create the matching builder log before edits and keep implementation and log
  publication commits separate.
- No network, provider, telemetry, API key, runtime HTTP, cloud image
  generation, or production-router/publication integration.
- Do not weaken or skip tests; preserve truthful unavailable canonical-bridge
  skips.
- Stop with `AWAITING_CHATGPT_AUDIT` after non-forceful publication.

## Required evidence

- Full GitHub prompt and criteria URLs in the builder log.
- Exact implementation and separate log-publication SHAs and GitHub URLs.
- Focused R01 tests, retained M08/M07 regressions, full pytest, compileall,
  Godot headless boot, diff-check, and protected-file checks.
- Record any failed command and correction chronologically.
