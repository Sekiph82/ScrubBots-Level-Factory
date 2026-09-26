# SB-LF07-008-C001-R03 — Strict Re-Audit

## Result
CHANGES_REQUIRED / ACCOUNTING FIXED, APPLES-TO-APPLES VALIDATION STILL OPEN

## Closed in R03
- Caller-created CostUsageRecord can no longer establish trusted accounting; costs remain None in line with accepted SB-LFX-017 truth.
- Mutation counters derive from AttemptReport.
- Regeneration route retains actual GenerationResult, generator id/version and request digest.
- Caller-supplied workload/config digest override is rejected.

## Remaining blockers
1. Mutation `seed_config_digest` is derived only from `{"seed": base_seed}`. Regeneration workload likewise uses only `{"seed": request.seed}`. Width, height, generator mode, difficulty, palette/options/theme/style and other actual GenerationRequest config are not part of the matched workload identity. Different regeneration configurations with the same seed can therefore compare as “matched.”
2. Regeneration `accepted=1` is inferred directly from `GenerationResult.status == SUCCESS`. A successful generator output has not thereby passed the same M03/M04/M05 eligibility requirements used by mutation. This is not an apples-to-apples accepted/eligible counter.
3. Regeneration solver/evidence workload is always zero rather than derived or truthfully marked unavailable.
4. The comparison inherits the forgeable SB-LF07-006 target authority.

## R04 requirement
Define one matched-case contract carrying the full canonical GenerationRequest/config identity and equivalent mutation starting/config identity. Regenerated candidates must pass the same accepted validation chain before counting accepted/eligible; unavailable solver/evidence counters must remain explicitly unavailable rather than fabricated zero. Compare only sealed target authority.

## Disposition
OPEN / R04 REQUIRED.