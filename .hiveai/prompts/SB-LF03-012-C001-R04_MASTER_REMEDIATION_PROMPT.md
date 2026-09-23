# SB-LF03-012-C001-R04 — Master Remediation Prompt

Document role: CODEX MASTER REMEDIATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch:
`main`

## Authorization

Remediate only:

`SB-LF03-012`

R04 index:
`.hiveai/prompts/SB-LF03-012-C001-R04_REMEDIATION_INDEX.md`

R03 re-audit summary:
`.hiveai/audits/SB-LF03-009-012-C001-R03_STRICT_REAUDIT_SUMMARY.md`

Exact task prompt:
`.hiveai/prompts/SB-LF03-012-C001-R04_HISTORICAL_REGRESSION_FIDELITY_CLOSURE_PROMPT.md`

## Governance

- Do not edit root `TASKS.md`.
- Do not create/edit `.hiveai/audits/**`.
- Do not reopen PASS/CLOSED LF03 tasks.
- Only minimum test-fixture compatibility edits are allowed outside SB-LF03-012.
- Do not alter accepted gameplay/search/budget semantics.
- No force push/reset/clean/stash/discard of unrelated owner work.
- Owner primary ScrubBots checkout remains read-only.
- No gameplay-rule clone in Python.
- No test skips/xfails to hide failures.

## Execution

1. Safely sync current Level Factory `main`.
2. Read R03 audit summary, SB-LF03-012 R03 strict re-audit and exact R04 prompt.
3. Create:
   `.hiveai/codex-logs/SB-LF03-012-C001-R04_HISTORICAL_REGRESSION_FIDELITY_CLOSURE_CODEX_LOG.md`
   before product/test edits.
4. Implement the four narrow regression-corpus corrections:
   - true baseline transition foreign-authority child regression;
   - true SolutionCountEngine binding/foreign-child regression;
   - attached-timeout canonical-invariance declarative regression;
   - stale-LevelData-hash declarative canonical-bridge regression.
5. Recompute fixture payload checksums.
6. Run all task-prompt verification gates.
7. Verify `TASKS.md` zero diff.
8. Commit/push implementation + fixtures/tests + task log.
9. Finalize task log and push terminal log-only commit.
10. Create master R04 log:
   `.hiveai/codex-logs/SB-LF03-C001-R04_MASTER_REMEDIATION_CODEX_LOG.md`
11. Record:
   - R04 builder-log full URL;
   - implementation SHA;
   - terminal log SHA;
   - focused results;
   - retained LF03 result;
   - full pytest result;
   - real canonical invoke result;
   - stale-hash rejection result;
   - TASKS zero diff.
12. Commit/push master R04 log.
13. STOP for independent ChatGPT re-audit.

## Final response

Return only:
1. full GitHub URL of the R04 master remediation log;
2. final master-log commit SHA;
3. full GitHub URL of the SB-LF03-012 R04 builder log;
4. implementation commit SHA;
5. terminal log-only commit SHA.
