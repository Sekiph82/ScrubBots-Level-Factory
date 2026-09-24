# SB-LF04-010-C001-R02 — Verified Producer Binding Provenance

Document role: CODEX REMEDIATION PROMPT

Target:
`SB-LF04-010 — Keep metric provenance/versioning.`

R01 re-audit:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF04-010-C001-R01_EXACT_PRODUCER_PROVENANCE_STRICT_REAUDIT.md

Builder log:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF04-010-C001-R02_VERIFIED_PRODUCER_BINDING_PROVENANCE_CODEX_LOG.md

Do not edit root TASKS.md.

## Finding

Optional metric provenance is still a caller-supplied provider id/version, not a binding to the producing result/evidence.

## Required design

Introduce a closed immutable producer binding for optional 004–007 metrics, for example `MetricProducerBinding`.

It must bind at minimum:
- exact MetricId;
- provider id/version;
- provider result schema/version if applicable;
- provider result digest;
- MetricEvidence disposition;
- exact MetricEvidence canonical digest/proof digest when verified;
- LevelData source SHA;
- solver evidence digest;
- canonical gameplay authority identity.

The binding must be constructed from the actual provider result object, not from arbitrary strings.

Rules:
- core 002/003 metrics continue to use their fixed accepted producer identities;
- optional 004–007 metric present in LevelMetrics requires a matching verified producer binding;
- current production 004–007 providers are unavailable, so no optional production metric can currently obtain a verified binding;
- caller-supplied provider id/version alone is insufficient;
- missing/extra/cross-metric/cross-level/cross-evidence bindings fail closed;
- closed MetricId catalog retained;
- score/lane/LevelMetrics lineage checks retained;
- operational telemetry excluded.

Do not fabricate optional provenance merely to make a manually constructed LevelMetrics pass.

Tests must prove:
- direct LevelMetrics optional value + provider strings cannot build DifficultyAnalysis;
- fixture provider result cannot produce verified binding;
- unavailable provider cannot produce binding;
- wrong metric/result/evidence/authority rejected;
- core 002/003 still work;
- parser round-trip remains deterministic.

Run focused + retained/full gates and publish R02 task log/commits.
