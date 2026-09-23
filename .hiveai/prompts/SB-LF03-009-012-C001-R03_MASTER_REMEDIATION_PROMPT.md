# SB-LF03-009,011,012-C001-R03 — Master Remediation Prompt

Document role: CODEX MASTER REMEDIATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch:
`main`

## Authorization

Remediate only:

`SB-LF03-009 -> SB-LF03-011 -> SB-LF03-012`

R03 index:
`.hiveai/prompts/SB-LF03-009-012-C001-R03_REMEDIATION_INDEX.md`

R02 re-audit summary:
`.hiveai/audits/SB-LF03-005-012-C001-R02_STRICT_REAUDIT_SUMMARY.md`

Do not reopen:
`001,002,003,004,005,006,007,008,010`

except for the smallest compatibility edit strictly required by the accepted 009/011 API changes. Preserve all accepted semantics and retained tests.

## Governance

- Root `TASKS.md` is ChatGPT-owned. Do not edit it.
- Do not create/edit `.hiveai/audits/**`.
- Do not rewrite earlier prompt/log/audit history.
- Each R03 task gets a separate builder log, implementation commit and terminal log-only commit.
- No force push/reset/clean/stash/discard of unrelated owner work.
- Owner's primary ScrubBots checkout remains untouched.
- No gameplay-rule clone in Python.
- No provider-credit/network calls merely for tests.

## Canonical gameplay authority

Resolve current:
https://github.com/Sekiph82/Scrubbots

Use an independent temporary clean Git checkout at the exact canonical SHA for real bridge integration. Source it locally from the owner's Git repository/object store so the dirty primary working tree is never changed.

Verify:
- exact detached SHA;
- clean status;
- exact required source bytes;
- clean/source-identical state after every bridge operation.

## Execution order

For each task:

1. safely sync Level Factory `main`;
2. read its R02 re-audit and exact R03 prompt;
3. create its R03 builder log before product/test edits;
4. implement only the remaining finding;
5. run focused and affected dependency/regression tests;
6. run required retained/full gates;
7. verify `git diff --exit-code -- TASKS.md`;
8. commit/push implementation/tests/docs/log;
9. finalize task log;
10. publish terminal log-only commit;
11. continue to the next R03 task without waiting for ChatGPT.

## 009 closure rule

Real canonical invocation already exists and must remain real.

Close the remaining provenance gap:

**the SHA-256 identified as LevelData source identity must be computed from the exact Level Data V1 source bytes from which the runner constructs canonical LevelData.**

Matching two caller-provided strings is not sufficient.

Use canonical Level Data V1 fields from main-game spec:
`version,id,name,difficulty,width,height,palette,cells`.

Tamper one source field while retaining stale hash and prove bridge rejects it before canonical execution.

## 011 closure rule

Wall-clock timeout must be operational-only.

Do not serialize timeout occurrence into canonical deterministic solver truth, even under a generic label.

If deterministic result exists:
- timeout telemetry may wrap it;
- canonical result bytes remain unchanged.

If physical timeout prevents deterministic result:
- canonical deterministic result is absent/incomplete;
- operational wrapper reports INCONCLUSIVE.

No timeout marker/reason/duration in canonical evidence or reproduction identity.

## 012 closure rule

Create actual declarative payload fixtures, not merely ID strings, for all eight historical negative defect families.

Every fixture must carry:
- stable ID;
- version/family;
- declarative payload;
- expected result;
- production=false where fake;
- canonical payload SHA-256.

Tests must load and execute these payloads.

Also lock:
- 009 exact LevelData source binding + tamper failure;
- 011 timeout occurrence separation;
- real legal_moves/apply_placement/solve bridge operations;
- clean checkout immutability;
- full repository green gate.

## Final R03 verification

After all three:

- focused 009/011/012;
- all retained LF03;
- affected LF00/LF06;
- full `python -m pytest -q`;
- repeat full suite from clean tracked state if practical;
- `python -m compileall -q src tests`;
- Level Factory Godot headless editor boot;
- real canonical bridge legal_moves/apply_placement/solve;
- source-hash tamper rejection;
- `git diff --check`;
- `git diff --exit-code -- TASKS.md`.

Create:
`.hiveai/codex-logs/SB-LF03-C001-R03_MASTER_REMEDIATION_CODEX_LOG.md`

Record each task log URL, implementation SHA, terminal log SHA, focused/full results, canonical invoke evidence, any legitimate skip, and TASKS zero-diff.

Commit/push the master log, then STOP for independent ChatGPT re-audit.

## Final response

Return only:
1. full GitHub URL of R03 master remediation log;
2. final master-log commit SHA;
3. three R03 builder-log GitHub URLs.
