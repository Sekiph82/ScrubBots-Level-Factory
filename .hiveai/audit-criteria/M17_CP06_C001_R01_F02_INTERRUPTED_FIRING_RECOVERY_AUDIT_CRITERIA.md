# M17-CP06-C001-R01 — F02 Interrupted FIRING Recovery: Strict Audit Criteria

Authoritative source: `.hiveai/audits/M17_CP06_C001_STAGE1_STRICT_AUDIT_V02_CORRECTION.md`.
Builder prompt: `.hiveai/prompts/M17_CP06_C001_R01_F02_INTERRUPTED_FIRING_RECOVERY_PROMPT.md`.
Log: `.hiveai/codex-logs/M17_CP06_C001_R01_F02_INTERRUPTED_FIRING_RECOVERY_CODEX_LOG.md`.

PASS for **this narrow remediation only** if all are true:

1. **Governance:** Codex works only in Desktop LF repo, publishes to GitHub main using normal non-force fast-forward, owner untracked 55 + two test scratch directories entirely untouched. No TEMP/AppData new worktrees or copied projects. Root TASKS and audits unchanged by Codex. No other repo, R2 production, installer or broad integration touched.
2. **Correct scope:** F01 is not altered or retested. Verify canonical `ContentManifestV1.__post_init__` sorted `disabled_levels` is retained. Accepted Stage1 code untouched outside strictly necessary F02 plumbing.
3. **Recovery safety:** Interrupted SCHEDULED→FIRING retains stable persisted claim/idempotency key. `run_due` can resume already FIRING and uses exact same durable key, not a new key based on the incremented revision. Correct journal CAS; revalidate due-time gates; reactivation either at-most-once by durable idempotency key or provably fail-closed on uncertainty. Cancelled/FIRED/BLOCKED are not reactivated. Nonterminal uncertainty does not silently lose the schedule.
4. **Targeted evidence:** Only new/changed F02 focused regression(s) are run, with an interruption recovery case and no-double-effect assertion; reuse the **existing original 7/63 PASS** log instead of rerunning old tests. Source/test diff checks and secret hygiene. Do not claim full regression was executed.
5. **Publication:** Real implementation/test and log commits safely published; real GitHub source and log independently reviewable; 0/0 parity. No stale tests/result claims; no overwritten owner files.

Verdict may be `R01_F02_PASS_STAGE1_TECHNICAL_READY_STAGE2_PENDING` or `R01_CHANGES_REQUIRED` with precise new deficiency; never label M17 complete while R05 and provider/CP03 activation/durable weekly/game-runtime are pending.
