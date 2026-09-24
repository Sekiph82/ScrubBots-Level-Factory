# SB-LF04-005-C001-R02 — Slot Pressure Production-Unavailable Closure

Document role: CODEX REMEDIATION PROMPT

Target:
`SB-LF04-005 — Add slot pressure only when canonical.`

R01 re-audit:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF04-005-C001-R01_CANONICAL_SLOT_TRACE_BOUNDARY_STRICT_REAUDIT.md

Builder log:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF04-005-C001-R02_SLOT_PRESSURE_PRODUCTION_UNAVAILABLE_CLOSURE_CODEX_LOG.md

Do not edit root TASKS.md.

## Mission

Preserve deterministic fixture slot-pressure math, but close all production trust elevation.

Current code has no executable canonical slot-trace provider.

Requirements:
- caller-created snapshots remain FIXTURE only;
- no generic helper may upgrade them to VERIFIED_CANONICAL;
- production slot_pressure remains UNAVAILABLE/absent;
- arbitrary capacities cannot become canonical truth;
- copied provider id/version cannot elevate trust;
- no art/color heuristic.

A future real provider may be designed as an explicit capability interface, but current implementation must report unavailable until it actually retrieves canonical slot observations.

Update shared evidence API consistently with 004 R02.

Run focused + retained/full gates and publish R02 task log/commits.
