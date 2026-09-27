# SB-LF09-001-C001-R02 — Complete Cross-Candidate Artifact Identity Remediation

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main

## Authorization

Remediate only finding `LF09-001-R01-AUD-001` from the independent R01 audit.
Preserve the accepted experimental-selection scope, M00-M08 evidence, root
`TASKS.md`, and all ChatGPT audit files. Do not begin SB-LF09-002 or any later
M09, Content Platform, main-game, provider, or production-publication work.

## Required remediation

1. Complete the versioned cross-candidate artifact identity policy for every
   `CandidateEvidence` artifact identity that can reach the selector, including
   optional `preview_ref`/`preview_digest` and `mutation_ref`/`mutation_digest`.
2. Enforce the selected policy before ranking. Candidate-specific identities
   must fail closed on cross-candidate reference or digest collisions. If any
   identity is intentionally shareable, encode that exception explicitly in the
   versioned policy and immutable selection provenance; implicit sharing is
   prohibited.
3. Keep the canonical `verify_artifact_set()` byte/reference boundary, exact
   opt-in, deterministic replay, finite budgets, source-art immutability,
   M03/M04/M05/M07 acceptance gates, and no production promotion unchanged.
4. Add focused tests for every policy-listed candidate-specific artifact pair,
   including both optional pairs, plus a positive test for each explicitly
   declared shared identity if one is introduced. Retain all R01 and prior
   focused tests.

## Boundaries

- Do not edit `TASKS.md` or `.hiveai/audits/**`.
- Create the matching CODEX builder log before edits and keep implementation
  and log-publication commits separate.
- No network, provider, telemetry, API key, runtime HTTP, cloud image
  generation, production router, or publication integration.
- Do not weaken, skip, or xfail tests; preserve truthful unavailable canonical
  bridge skips.
- Stop with `AWAITING_CHATGPT_AUDIT` after non-forceful publication.

## Required evidence

- Full GitHub prompt and criteria URLs in the builder log.
- Exact implementation and separate log-publication SHAs and GitHub URLs.
- Focused R02 tests, retained M08/M07 regressions, full pytest, compileall,
  Godot headless boot, diff-check, and protected-file checks.
- Record every failed command and correction chronologically.
