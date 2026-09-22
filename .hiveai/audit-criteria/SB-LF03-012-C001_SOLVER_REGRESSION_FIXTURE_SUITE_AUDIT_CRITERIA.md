# SB-LF03-012-C001 - Solver Regression Fixture Suite - Strict Audit Criteria

Target:
`SB-LF03-012 - Add regression fixtures.`

## Fixture goals

Create durable, deterministic regression fixtures covering the accepted LF03 contracts.

At minimum include fixture families for:
- legal move provider validation;
- branching solved search;
- proven no-solution/exhausted search;
- repeated-state/memoization;
- bounded INCONCLUSIVE;
- multiple-solution counting;
- reproduction MATCH and tamper DIVERGED;
- authority/source mismatch fail-closed;
- canonical bridge integration when available;
- large/rectangular workload evidence where practical.

## Canonical fixtures

At least one committed/capability-gated fixture must exercise real canonical `Sekiph82/Scrubbots` gameplay authority from SB-LF03-009.

Fixture-only fake providers may remain for algorithm isolation, but they must be labeled as non-production.

## Determinism

Fixtures must:
- have stable identifiers;
- store declarative inputs/expected truth;
- avoid absolute paths/timestamps;
- validate checksums;
- reproduce identical deterministic evidence under same versions.

Do not commit giant transient output or user-specific cache.

## Failure semantics

A missing external canonical checkout may SKIP the real cross-repo integration fixture only when the skip reason is explicit and local algorithm/contract fixtures still run.

When canonical checkout capability is supplied, the integration fixture must execute and pass; it cannot silently skip after capability discovery.

## Full gate

SB-LF03-012 closes only when the complete LF03 retained suite and repository-wide suite are green.

## PASS

PASS when LF03 has a durable regression corpus that protects both generic search machinery and canonical gameplay integration without conflating fixtures with production authority.
