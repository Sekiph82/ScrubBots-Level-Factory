# SB-LF04-004-C001-R02 — No Generic Canonical Evidence Minting

Document role: CODEX REMEDIATION PROMPT

Target:
`SB-LF04-004 — Add dependency depth only when canonical.`

R01 re-audit:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF04-004-C001-R01_CANONICAL_PROVIDER_BOUNDARY_STRICT_REAUDIT.md

Builder log:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF04-004-C001-R02_NO_GENERIC_CANONICAL_EVIDENCE_MINTING_CODEX_LOG.md

Do not edit root TASKS.md.

## Finding

The generic `verified_canonical_evidence()` helper can mint VERIFIED_CANONICAL from a caller-authored mapping without executing any canonical provider.

## Required remediation

Current production dependency-depth semantics are unavailable.

Therefore:
- remove or hard-disable any generic caller-facing API that creates VERIFIED_CANONICAL from arbitrary proof mappings;
- keep FIXTURE calculations available only as non-production evidence;
- production `populate_dependency_depth()` must have no successful AVAILABLE path in the current codebase unless a concrete canonical provider implementation actually executes canonical authority and owns receipt issuance;
- do not replace the generic helper with another caller boolean/string/token factory;
- do not derive dependency depth from solution depth, move order, adjacency, colors, WFC or heuristics.

If you keep a future provider abstraction, it may expose capability UNAVAILABLE today. A future concrete provider must issue its own receipt internally as a consequence of actual canonical execution.

## Tests

Prove:
- no public/generic function can mint VERIFIED_CANONICAL from caller-authored proof data;
- direct FIXTURE result cannot populate;
- copying canonical-looking provider id/version cannot populate;
- current production provider is UNAVAILABLE;
- dependency_depth remains absent;
- no path-depth heuristic appears;
- retained 005–007 shared boundary tests stay compatible.

Run focused + retained M04/M03 + full repository gates. Publish R02 implementation/log/terminal commit.
