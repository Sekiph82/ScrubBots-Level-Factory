# SB-LF07-007-C001 — Bounded Mutation Attempts — Implementation Prompt

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main

Authoritative audit criteria: `.hiveai/audit-criteria/SB-LF07-007-C001_BOUNDED_MUTATION_ATTEMPTS_AUDIT_CRITERIA.md`

Implement SB-LF07-007 deterministic bounded mutation attempts.

Create a versioned finite attempt-budget contract. Every mutation attempt has a deterministic ordinal in provenance and still passes the SB-LF07-004 validation chain. No loop/recursion/provider path may execute beyond the declared limit. Exhaustion must be explicit and must never mean UNSOLVABLE or SUCCESS. Wall-clock timeout remains operational telemetry, not canonical budget truth.

Add exact-limit, one-attempt, invalid-budget, no-post-limit-call, replay and timeout-separation tests. Run required gates and publish task-specific builder logs/commits.

Builder log: `.hiveai/codex-logs/SB-LF07-007-C001_BOUNDED_MUTATION_ATTEMPTS_CODEX_LOG.md`
