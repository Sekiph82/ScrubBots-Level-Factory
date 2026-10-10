# SB-LFX-018-C001-R02-R05-R02 | Independent Audit Criteria

Authority: `Sekiph82/ScrubBots-Level-Factory` `main`
Parent independent audit: `.hiveai/audits/SB-LFX-018-C001-R02-R05-R01_DESKTOP_HISTORY_RESUME_STRICT_AUDIT_V01.md`
Builder task: `.hiveai/prompts/SB-LFX-018-C001-R02-R05-R02_POST_ACTIVATION_RECOVERY_EVIDENCE_PROMPT.md`
Builder appends existing single R05 log: `.hiveai/codex-logs/SB-LFX-018-C001-R02-R05_PRODUCTION_HISTORY_FULL_REGRESSION_EVIDENCE_CODEX_LOG.md`

## Acceptance for narrow R02 only

- **Safe operational boundaries**: Desktop existing LF repo only, preserve all 57 owner-untracked paths including Release and existing scratch folders byte-for-byte; no new TEMP/AppData worktree/clone, no multi-GB scratch, no unapproved R2 production actions or other-repo modification. No Codex root TASKS/audits writes.
- **G1 continuity**: Does not change canonical M13 schema, CP03-008/009, M11 event authority or invent missing proof. Exercises the *actual post-activation failure window* with a small provider-shaped stateful fixture: live N+1 active but M13 still tip N, then verified existing M11 release ledger/activation identity, exact manifest byte/hash/version/replay/approval proof and idempotent conditional repair of only the missing successor. Repair must STOP on absent/contradictory records and avoid unintended second activation or rewriting history. Any live repair is owner-approval-gated; R02 does not actually perform R2 writes.
- **Crash/uncertain acknowledgment**: A conditional write could have succeeded despite a lost acknowledgment. Retry proves existing durable exact tip is idempotently accepted with correct readback; mismatched tip refuses; CAS conflicts refuse; further future successor resumes only after verified gap closure. No "just append because manifest exists" trust shortcut. If a safe repair cannot be constructed from existing immutable records, report `OPERATOR_AUTHORITY_REQUIRED`, avoid code that guesses history.
- **G2 evidence distinction**: Synthetic provider checks must never be passed off as live CP03-008/009 or owner-approved R2 publish. Correct log's incorrect expanded SHA for original implementation to actual GitHub commit `6b68ce456dd174db2c9ac7a9509d60585b5bbf16`. Evidence matrix labels previously accepted vs new PASS vs still NOT RUN.
- **Minimal testing**: Run only newly changed R02 focused tests once, with `PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider`. Do not repeat the R01 4-PASS suite, M17 7/63/3, prior R04 suites, 150 solver jobs, full pytest, Godot, screenshots or installer. Never produce disposable directories that cannot be removed.
- **Delivery**: Preserve existing code/evidence, source/test commit then append-only existing R05 log commit, ordinary safe non-force main publication, real published log and post-push HEAD/origin parity. If R02 cannot be completed without larger operations/approval, publish only genuinely safe finished code/evidence with exact blocker, not fictitious PASS.

R02 acceptance **does not** close full R05. Mandatory outstanding real provider/owner live permission, actual end-to-end CP03, original full LF regression, native Windows picker, final R05 install/screenshot and Alpix availability must be recorded accurately for future owner decisions. GPT independently audits and alone updates root TASKS.
