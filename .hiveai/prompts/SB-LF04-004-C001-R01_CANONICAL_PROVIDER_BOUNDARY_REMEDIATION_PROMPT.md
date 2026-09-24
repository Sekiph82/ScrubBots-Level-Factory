# SB-LF04-004-C001-R01 — Canonical Provider Boundary Remediation

Target: SB-LF04-004

Audit:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF04-004-C001_CANONICAL_DEPENDENCY_DEPTH_STRICT_AUDIT.md

Builder log:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF04-004-C001-R01_CANONICAL_PROVIDER_BOUNDARY_CODEX_LOG.md

Do not edit TASKS.md.

Close the fixture-to-production authority leak. Fixture AVAILABLE dependency results must be explicitly non-production and must not populate production LevelMetrics. Until a real executable canonical dependency-semantics provider exists, production dependency_depth remains UNAVAILABLE/absent.

Introduce a versioned provider/evidence disposition that distinguishes VERIFIED_CANONICAL from FIXTURE/UNAVAILABLE/ERROR. A VERIFIED_CANONICAL result must be bound to exact authority, source, state/evidence and verifiable provider evidence. Do not make a caller boolean sufficient.

Tests must prove fixture AVAILABLE cannot populate production metrics, copied provider strings cannot elevate trust, production unavailable remains absent, mismatched state/evidence fails closed, and no path-depth heuristic is introduced.