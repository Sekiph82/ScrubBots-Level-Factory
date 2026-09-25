# SB-LF07-008-C001 — Mutate vs Regenerate Efficiency Comparison — Implementation Prompt

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main

Authoritative audit criteria: `.hiveai/audit-criteria/SB-LF07-008-C001_MUTATE_VS_REGENERATE_EFFICIENCY_AUDIT_CRITERIA.md`

Implement SB-LF07-008 a reproducible mutate-vs-regenerate efficiency evidence report.

Compare only matched workloads with the same target range/policy, seed/config identity, validation requirements and declared budgets. Use M07 for mutation and an already accepted generation path for regeneration. Record deterministic counters such as attempts, produced/accepted/inconclusive/rejected counts and solver workload; trusted provider cost evidence may be included when already available. Wall-clock/machine metrics are telemetry only and excluded from canonical digest.

Do not pronounce one strategy globally better. Reject mismatched comparisons and keep lineage separate. Add deterministic/mismatch/zero-acceptance/inconclusive/cost-trust tests. Run all gates and publish task logs/commits.

Builder log: `.hiveai/codex-logs/SB-LF07-008-C001_MUTATE_VS_REGENERATE_EFFICIENCY_CODEX_LOG.md`
