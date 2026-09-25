# SB-LF07-006-C001 — Challenge Score Range Targeting — Implementation Prompt

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main

Authoritative audit criteria: `.hiveai/audit-criteria/SB-LF07-006-C001_TARGET_CHALLENGE_SCORE_RANGE_AUDIT_CRITERIA.md`

Implement SB-LF07-006 deterministic Challenge Score range targeting on top of the validated mutation pipeline.

The target is an explicit [min,max] Challenge Score interval using the accepted M04 policy/version. Evaluate only real post-mutation M04 evidence. Never infer target progress from dimensions, color count, art complexity or difficulty labels. Required load/risk/retention evidence must be honored when available/required; missing evidence is INCONCLUSIVE/UNAVAILABLE, never default zero or PASS.

Version the deterministic selection/tie policy. A target match requires score in range plus all applicable safety gates. Do not implement unbounded attempts yet. Add stale-policy/evidence, missing-constraint, tie, no-match and forbidden-proxy tests. Run required gates and publish separate task log/commits.

Builder log: `.hiveai/codex-logs/SB-LF07-006-C001_TARGET_CHALLENGE_SCORE_RANGE_CODEX_LOG.md`
