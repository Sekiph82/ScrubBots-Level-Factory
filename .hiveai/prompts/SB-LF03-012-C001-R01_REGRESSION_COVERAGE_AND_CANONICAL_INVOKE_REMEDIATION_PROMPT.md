# SB-LF03-012-C001-R01 — Regression Coverage + Canonical Invoke Remediation

Document role: CODEX REMEDIATION PROMPT

Target: `SB-LF03-012 — Add regression fixtures.`

Audit:
`.hiveai/audits/SB-LF03-012-C001_SOLVER_REGRESSION_FIXTURE_SUITE_STRICT_AUDIT.md`

Create first:
`.hiveai/codex-logs/SB-LF03-012-C001-R01_REGRESSION_COVERAGE_AND_CANONICAL_INVOKE_REMEDIATION_CODEX_LOG.md`

Do not edit `TASKS.md`.

## Mission

After 003/004/005/006/008/009/010/011 R01 changes are present, expand the durable regression corpus to lock those fixes.

Required new negative fixtures/tests:
- legal result bound to another query/state;
- canonical key result bound to another state;
- transition child authority drift;
- enumeration wrong-query result;
- true frontier peak on wide shallow graph;
- reproduction candidate/LevelData/version tamper;
- actual max-visited execution stop;
- timeout metadata excluded from canonical evidence.

## Real canonical fixture

Replace capability-only bridge coverage with a real `CanonicalHeadlessBridge.invoke()` integration using the committed SB-LF03-009 R01 external runner.

Exercise actual canonical gameplay behavior and deterministic repeat while proving canonical checkout immutability.

If the canonical checkout is available, this test must execute and cannot silently skip.

Keep fake graph fixtures explicitly non-production.

Run complete retained LF03 suite, full pytest, compileall, Godot headless, real bridge fixture, diff-check and TASKS no-diff.

Publish R01 implementation/log/terminal commit.
