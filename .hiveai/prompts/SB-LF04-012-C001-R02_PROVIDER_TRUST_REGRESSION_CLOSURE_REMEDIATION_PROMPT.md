# SB-LF04-012-C001-R02 — Provider Trust Regression Closure

Document role: CODEX REMEDIATION PROMPT

Target:
`SB-LF04-012 — Tests prove analysis does not mutate gameplay/art source.`

R01 re-audit:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF04-012-C001-R01_EXECUTABLE_CORPUS_AND_NON_MUTATION_CLOSURE_STRICT_REAUDIT.md

Builder log:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF04-012-C001-R02_PROVIDER_TRUST_REGRESSION_CLOSURE_CODEX_LOG.md

Do not edit root TASKS.md.

Run after 004–007 and 010 R02.

## Mission

Retain the payload-driven checksummed corpus and all current non-mutation checks.

Add declarative regression cases that prove the corrected trust boundaries:

1. a caller-authored mapping cannot mint VERIFIED_CANONICAL evidence;
2. current production dependency_depth remains UNAVAILABLE;
3. current production slot_pressure remains UNAVAILABLE;
4. current production bait_deadlock remains UNAVAILABLE;
5. current production volatility remains UNAVAILABLE;
6. optional metric provenance cannot be encoded from provider id/version strings alone;
7. a fixture provider result cannot produce a verified producer binding;
8. missing/cross-wired producer binding fails closed.

Update corpus checksums and make tests consume these payloads.

Retain:
- executable 001–011 behavior-driven cases;
- ChallengeScore/Lane integrity cases;
- exact Level Data bytes/SHA non-mutation;
- exact logical-art bytes/SHA non-mutation;
- capability-gated canonical checkout status/source immutability;
- calibration disabled state;
- full repository green gate.

Do not create a fake canonical provider just to make a positive optional metric case.

Run full M04/M03/repository gates and publish R02 task log/commits.
