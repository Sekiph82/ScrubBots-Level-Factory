# SB-LF07-008-C001-R02 — Strict Re-Audit

## Result
CHANGES_REQUIRED / REAL RESULT TYPES USED, MATCHED-WORKLOAD AND ACCOUNTING AUTHORITY STILL OPEN

## Material improvement
- Mutation counters are now derived from `AttemptReport`.
- Regeneration uses a real `GenerationResult`.

## Remaining blockers
1. `RegenerationRouteEvidence.from_generation_result()` accepts an arbitrary caller-supplied `EfficiencyWorkload` and arbitrary `config_digest`; it does not derive/cross-check target, seed/config, validation policy or budget identity from the generation request/result.
2. Solver workload for regeneration is always zero rather than derived from accepted evidence when available.
3. `TrustedAccountingEvidence.from_cost_usage()` treats any caller-constructed `CostUsageRecord` as trusted. This directly conflicts with the accepted `SB-LFX-017-C001-R02` audit, which concluded the repository currently has **no authoritative provider/job accounting producer** and financial truth must remain UNKNOWN/NOT AVAILABLE.
4. Tests create `CostUsageRecord(provider_attempt_count=1)` directly, proving the claimed accounting authority is self-asserted.

## R03 requirement
Derive matched workload identities from actual mutation/generation inputs/results. Cross-check seed/config/validation/budget. For accounting, follow accepted SB-LFX-017 truth: no authoritative producer means cost/credits are unavailable, not trusted. Remove caller-created CostUsageRecord as financial authority.

## Disposition
OPEN / R03 REQUIRED.