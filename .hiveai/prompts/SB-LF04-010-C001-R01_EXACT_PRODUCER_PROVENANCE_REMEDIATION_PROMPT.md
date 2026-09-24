# SB-LF04-010-C001-R01 — Exact Producer Provenance Remediation

Target: SB-LF04-010

Audit:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF04-010-C001_METRIC_PROVENANCE_VERSIONING_STRICT_AUDIT.md

Builder log:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF04-010-C001-R01_EXACT_PRODUCER_PROVENANCE_CODEX_LOG.md

Do not edit TASKS.md.

Stop auto-filling generic producer identities.

For every populated metric, DifficultyAnalysis construction must receive/derive the exact accepted producer identity:
- 002 witness metrics use an explicit versioned solver-witness producer identity;
- 003 complexity metrics use an explicit versioned solver-metrics producer identity;
- any future VERIFIED_CANONICAL 004–007 value carries its exact provider id/version from verified evidence.

Missing exact provenance for a populated metric is an error. Extra provenance for absent/unavailable metrics is an error.

Restrict metric_provenance and component_availability to the closed MetricId catalog. Require exact consistency: AVAILABLE populated metric <=> exact provider identity. Preserve LevelData/authority/evidence/LevelMetrics/score/lane digest cross-binding and operational telemetry exclusion.

Add parser/direct-constructor negative tests for unknown names, missing providers, extra providers and mixed lineage.