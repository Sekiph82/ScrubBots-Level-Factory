# SB-LF04-007-C001-R01 — Canonical Ordered-Trace Boundary Remediation

Target: SB-LF04-007

Audit:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF04-007-C001_CANONICAL_STATE_VOLATILITY_STRICT_AUDIT.md

Builder log:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF04-007-C001-R01_CANONICAL_ORDERED_TRACE_BOUNDARY_CODEX_LOG.md

Do not edit TASKS.md.

Retain the documented normalized V1 volatility formula. Make VolatilitySnapshot-based calculation fixture/non-production unless backed by verified canonical ordered-trace evidence.

Production volatility must remain UNAVAILABLE until an actual canonical trace provider exists. Caller-created counts/capacities and copied provider ids may not populate production LevelMetrics.

Tests prove fixture results cannot cross production boundary, unavailable remains absent, provider/authority/state/evidence mismatches fail closed, and art fragmentation remains unused.