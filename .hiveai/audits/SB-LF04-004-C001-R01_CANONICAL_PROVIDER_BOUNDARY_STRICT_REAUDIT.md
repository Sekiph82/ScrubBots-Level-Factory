# SB-LF04-004-C001-R01 — Canonical Provider Boundary — Strict Re-Audit

Document role: INDEPENDENT CHATGPT STRICT RE-AUDIT

## VERDICT

**CHANGES_REQUIRED**

- BLOCKER: 1
- MAJOR: 0
- MINOR: 0

## Audited chain

- R01 implementation: `4426755cd51f89f2087acc716b23ebeff1ed9785`
- R01 terminal log: `7fd678f58c97b05c4c1772a320c3e00f1a108941`
- R01 master publication: `e8ab678ad8500a3c5381a152a633aec06526fd52`

## Accepted progress

Fixture AVAILABLE dependency results are now rejected by `populate_dependency_depth()` unless their `MetricEvidence` disposition is VERIFIED_CANONICAL.

## BLOCKER-001 — VERIFIED_CANONICAL can still be minted from caller-supplied data

The shared function `verified_canonical_evidence()` is not backed by an executable canonical provider.

It accepts a caller-supplied mapping containing:
- authority;
- LevelData hash;
- state digest;
- evidence digest;
- provider id/version;
- arbitrary non-empty observations.

If those values echo the current LevelMetrics, the function computes a proof digest and injects the private token, creating VERIFIED_CANONICAL evidence.

No ScrubBots canonical provider is invoked and no canonical source independently attests the observations.

Therefore a caller can:
1. choose any dependency depth;
2. construct matching proof data;
3. call `verified_canonical_evidence()`;
4. attach the returned receipt to an AVAILABLE DependencyDepthResult;
5. populate production LevelMetrics.

This is still the exact fixture-to-production authority leak the R01 was meant to close.

## Required remediation

Until a real executable canonical dependency provider exists, there must be no generic caller-facing path that mints VERIFIED_CANONICAL evidence.

Remove/disable generic `verified_canonical_evidence()` minting. Current production dependency depth remains strictly UNAVAILABLE.

A future concrete provider may issue a verified receipt only as a consequence of executing and validating actual canonical authority, not by validating a caller-authored dictionary.
