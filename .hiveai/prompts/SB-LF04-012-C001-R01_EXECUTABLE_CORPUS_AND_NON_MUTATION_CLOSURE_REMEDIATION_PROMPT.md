# SB-LF04-012-C001-R01 — Executable Corpus & Non-Mutation Closure Remediation

Target: SB-LF04-012

Audit:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF04-012-C001_ANALYSIS_NON_MUTATION_REGRESSION_STRICT_AUDIT.md

Builder log:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF04-012-C001-R01_EXECUTABLE_CORPUS_AND_NON_MUTATION_CLOSURE_CODEX_LOG.md

Do not edit TASKS.md.

Run after 004–010 R01 changes.

Turn sb_lf04_m04_regression_v1.json into executable declarative regression evidence. Each case must contain enough versioned input/mutation/expected-result payload to drive the relevant behavior; tests must consume those payload fields, not merely verify IDs/checksum.

Cover all 001–011 task families, including:
- 004–007 fixture-vs-production UNAVAILABLE boundaries;
- 008 invalid score-result integrity;
- 009 invalid lane/comparison integrity;
- 010 missing/extra exact provenance rejection;
- 011 disabled calibration.

Expand non-mutation proof with exact pre/post bytes/SHA for:
1. an actual Level Data source fixture;
2. a relevant art/logical-grid source fixture;
3. canonical ScrubBots checkout status and required source bytes when bridge capability is exercised.

If canonical checkout capability is genuinely absent, make that proof explicitly capability-gated; do not replace it with an unrelated JSON file.

Keep full repository pytest green and preserve all accepted prior behavior.