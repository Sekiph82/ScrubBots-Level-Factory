# SB-LF07-010-C001 — Deterministic Mutation Regression Closure — Implementation Prompt

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main

Authoritative audit criteria: `.hiveai/audit-criteria/SB-LF07-010-C001_DETERMINISTIC_MUTATION_REGRESSION_AUDIT_CRITERIA.md`

Implement SB-LF07-010 as the M07 deterministic regression closure.

Create a versioned executable/checksummed regression corpus covering 001..009: immutable lineage, one real hardening and one real easing operator, mandatory re-solve/revalidate, provenance tamper/cycle rejection, Challenge Score targeting, bounded exhaustion, mutate-vs-regenerate comparison, owner-source immutability, Palette V3, and rejection of size/color difficulty shortcuts.

Run repeated clean deterministic executions and prove canonical digests/attempt sequences match. Include negative tamper cases that genuinely fail and pre/post non-mutation proofs for parent/source artifacts. Run the complete retained M03/M04/M05/M06/M07/full repository gates. Do not mark M07 PASS/CLOSED yourself. Publish implementation + terminal log commits and the task-specific builder log.

Builder log: `.hiveai/codex-logs/SB-LF07-010-C001_DETERMINISTIC_MUTATION_REGRESSION_CODEX_LOG.md`
