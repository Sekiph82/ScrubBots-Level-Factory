# SB-LF09-002-C001 — Versioned Fitness Metrics

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main

## Authorization

Implement only the next ordered M09 task `SB-LF09-002` after the independent
PASS/CLOSED audit of `SB-LF09-001-C001-R02`. Preserve accepted M00-M08
evidence, the closed LF09-001 experimental selector, root `TASKS.md`, and all
ChatGPT audit files. Do not begin SB-LF09-003 or any later M09, Content
Platform, main-game, provider, or production-publication work.

## Required implementation

1. Add a closed, versioned fitness-metric contract for the experimental
   evolutionary-selection lane. The metric catalog, schema/version, units or
   normalization rules, direction, and aggregation policy must be explicit and
   canonically serializable.
2. Compute fitness deterministically from accepted candidate evidence and the
   selected fitness policy. Bind each computed result to the exact candidate
   lineage identity and fitness-policy digest; caller-authored or mismatched
   fitness evidence must fail closed.
3. Keep fitness evaluation finite, offline, and side-effect free. It must not
   infer or overwrite owner-locked difficulty, gameplay semantics, source-art
   provenance, M03/M04/M05/M07 acceptance, or production-promotion state.
4. Preserve LF09-001's explicit opt-in, deterministic replay, complete
   candidate-artifact identity policy, accepted-artifact byte verification,
   source-art immutability, and no-production-promotion boundary.
5. Add focused tests for catalog/version canonicalization, deterministic
   replay, candidate-lineage and policy-digest binding, malformed or missing
   metric rejection, finite evaluation behavior, and isolation from production.
   Retain all LF09-001 and M07/M08 focused tests.

## Boundaries

- Create the matching CODEX builder log before implementation or tests.
- Do not edit `TASKS.md` or `.hiveai/audits/**`.
- Keep implementation and log-publication commits separate.
- No network, provider, telemetry, API key, runtime HTTP, cloud image
  generation, production router, main-game code, or publication integration.
- Do not weaken, skip, or xfail tests. Preserve truthful unavailable canonical
  bridge skips.
- Stop after non-forceful publication with `AWAITING_CHATGPT_AUDIT`.

## Required evidence

- Full GitHub prompt and audit-criteria URLs in the builder log.
- Exact implementation and separate log-publication SHAs and GitHub URLs.
- Focused LF09-002 tests, retained LF09-001/M07/M08 regressions, full pytest,
  compileall, Godot headless boot, diff-check, and protected-file checks.
- Record every failed command and correction chronologically.
