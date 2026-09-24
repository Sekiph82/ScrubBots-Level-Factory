# SB-LF04-008-C001-R01 — Challenge Score Result Integrity Remediation

Target: SB-LF04-008

Audit:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF04-008-C001_DIFFICULTY_V1_CHALLENGE_SCORE_STRICT_AUDIT.md

Builder log:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF04-008-C001-R01_CHALLENGE_SCORE_RESULT_INTEGRITY_CODEX_LOG.md

Do not edit TASKS.md.

The calculate_challenge_score formula is retained.

Make ChallengeScoreResult fail closed unless it is internally consistent with DIFFICULTY_V1:
- exact ordered component names;
- exact coefficients move=.25, states=.25, dead_end=.15, branching=.15, forced=.20;
- each contribution equals normalized*coefficient;
- score equals 100*sum(contributions), subject only to the documented deterministic numeric tolerance/representation;
- all values finite/bounded;
- source LevelMetrics digest valid.

Do not permit direct construction of arbitrary score with zero/fake components.

Update 009 tests to obtain valid threshold score fixtures through a strictly validated fixture constructor/policy-aware helper, not impossible ChallengeScoreResult objects.