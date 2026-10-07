# M14-R01 — CPX-002 TEMP-Only Closure Master

Document role: CODEX MASTER REMEDIATION PROMPT

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Child remediation:
`.hiveai/prompts/SB-CPX-002-C001-R01_TEMP_ONLY_AUTHORITY_EVIDENCE_CLOSURE_PROMPT.md`

Master criteria:
`.hiveai/audit-criteria/M14-R01_CPX002_TEMP_ONLY_CLOSURE_MASTER_AUDIT_CRITERIA.md`

## Authority

This master contains exactly one open M14 remediation child:
`SB-CPX-002-C001-R01`

CP03-001..012 are not to be reimplemented. CP03-008..012 already passed independent audit and remain closed unless R01 changes CPX-002 receipt semantics or directly breaks their regressions.

## Execution

1. Perform the child prompt completely.
2. Before the child begins, synchronize Level Factory safely with current `origin/main` exactly as the child requires.
3. Before any Factory/solver/replay action, create and bind the fresh TEMP-only ScrubBots current-main authority.
4. Never select or inspect an owner Desktop ScrubBots checkout as game authority.
5. Remediate ordinary in-scope failures and continue until all R01 gates are green or a true non-resolvable blocker exists.
6. Publish implementation separately from builder evidence if code changes.
7. Append R01 evidence to the existing M14 master log.
8. Fetch after publication and require clean 0/0 parity.
9. Stop for independent ChatGPT audit. Do not start M15.

## Final response

Return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-CPX-002-C001-R01_TEMP_ONLY_AUTHORITY_EVIDENCE_CODEX_LOG.md
