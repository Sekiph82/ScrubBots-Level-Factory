# SB-LF04-005-C001-R01 — Canonical Slot-Trace Boundary Remediation

Target: SB-LF04-005

Audit:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF04-005-C001_CANONICAL_SLOT_PRESSURE_STRICT_AUDIT.md

Builder log:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF04-005-C001-R01_CANONICAL_SLOT_TRACE_BOUNDARY_CODEX_LOG.md

Do not edit TASKS.md.

Keep the accepted max-occupancy formula, but stop arbitrary SlotSnapshot tuples from becoming production canonical evidence. Fixture calculators must be explicitly non-production and rejected by production LevelMetrics population.

If no canonical trace provider is executable, production remains UNAVAILABLE. If you establish one, bind exact authority/state/evidence/provider and canonical slot capacity semantics from ScrubBots rather than caller-supplied trust.

Tests: fixture result rejected for production population, unavailable remains absent, arbitrary capacity cannot claim canonical provider, verified-provider mismatch fails closed, deterministic fixture math retained.