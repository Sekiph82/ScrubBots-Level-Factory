# M17-CP06-C001-R01 — F02 Interrupted FIRING Recovery (ONE FIX ONLY)

**CODEX implementation task** in `Sekiph82/ScrubBots-Level-Factory`. Independent GPT audit follows.

Sources of authority:
- Canonical LF `TASKS.md`.
- Corrected independent audit: `.hiveai/audits/M17_CP06_C001_STAGE1_STRICT_AUDIT_V02_CORRECTION.md`.
- Audit criteria: `.hiveai/audit-criteria/M17_CP06_C001_R01_F02_INTERRUPTED_FIRING_RECOVERY_AUDIT_CRITERIA.md`.
- Standing owner process: `docs/process/CODEX_SYNC_PUBLISH_STANDARD_V01.md`.
- Builder log target: `.hiveai/codex-logs/M17_CP06_C001_R01_F02_INTERRUPTED_FIRING_RECOVERY_CODEX_LOG.md`.

## Exact authorized scope

**ONLY F02**, `SB-CP06-005/007/008` schedule-run claim recovery. Fix recovery/retry when a scheduled operation is already in the `FIRING` revision after process interruption. Published `content_pipeline/src/scrubbots_content_pipeline/m17_release_controls.py` `run_due()` derives the idempotency key from `revision.revision`; the journal advances SCHEDULED revision 1 to FIRING revision 2, where deriving another key prevents recovery with the persisted claim. Preserve the original claim identity across both states, exact same idempotency key on retry, explicit revalidation on recovery, and fail-closed prevention of double effects when a remote activation acknowledgment is uncertain.

**Do NOT implement F01.** GPT audit V02 expressly withdrew F01 as false: canonical `ContentManifestV1.__post_init__` already sorts `disabled_levels` before serialization. No multi-ID sort fix or F01 test is authorized. Preserve all accepted Stage 1 code and all existing test outcomes.

## Owner workspace and files

- Work ONLY in existing `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`, correct LF repository. No TEMP/AppData worktrees, extra clones, project copies, large scratch, 150 PNG solves or full tests.
- Owner explicitly ruled **leave all 55 pre-existing untracked paths and two test scratch directories as they are**. Do NOT add, delete, modify, move, rename, `git clean`, commit or try to tidy any of the 57 paths, including `Release/`, `ScrubBots_Factory_Studio.ico`, `level_factory/addons/`, `*.gd.uid`, and the two `.m17-...-pytest-*` directories. No disk inventory/cleanup work in this task.
- Check Desktop repo and fetch `origin/main`; safe fast-forward when possible. Never reset --hard, forced checkout/push, rebase, or discard owner-local changes. On true conflicting change, stop and identify paths instead of creating a new worktree.
- Codex **must not edit root `TASKS.md` or `.hiveai/audits/**`**. No edits to Scrubbots game repository, no live R2 deployment.

## Minimal implementation

1. Inspect `run_due()`, schedule revision transitions, and `ScheduleJournal` protocol. Read existing local SQLite fixture `SQLiteLocalProvider.claim_due()` and `finish_due()` in `tests/unit/test_m17_release_controls.py`.
2. Retain one stable persisted claim/idempotency identity from original SCHEDULED attempt through FIRING and retries. Prefer the smallest contract-compatible change; do not introduce a new scheduler/provider, rewrite unrelated validation or weaken CAS, UTC/DST, owner-approval/current-game replay boundaries.
3. If `FIRING` is observed after interruption: recover the original claim identity, revalidate all gates, and either finish successfully with the **same** activation idempotency key or fail closed. Do not generate a new activation identity when old activation may already have occurred. Respect journal's real CAS and terminal states; no double fire of cancelled/completed intents.
4. Add **only targeted new/modified F02 test(s)** which exercise `SCHEDULED→FIRING`, interruption before activation or after activation before finalization, same-key recovery, no duplicate side effects, stale/blocked rejection, and idempotent final state. A tiny local deterministic fixture is adequate. Avoid filesystem scratch and expensive test setup where possible.
5. **DO NOT RE-RUN** already completed M17 7 focused and 63 regression tests, compileall, broad pytest, Godot, solver, VOID suites or disk-heavy checks. The published original M17 builder log already records their PASS. Run only the *new/changed F02 case(s)* once if safe, and perform lightweight Git diff/secret checks. If test evidence exposes a genuine new defect, apply narrow fix and rerun only that failing test, documenting why. Do not turn publication into a repeat verification cycle.
6. Source/tests commit, then single R01 builder log commit. Fetch and normal fast-forward push **directly to GitHub `main`**. Verify published HEAD/origin parity (0/0) and preserve all 57 owner untracked entries untouched. If safe publication impossible, stop with exact blocker and preserve all changes. Final response only the real GitHub R01 builder-log link, or precise blocker if unpublished.

## Closure boundaries

R01 stops after this single F02 correction. No R05 work, no M17 Stage 2 real provider/CP03 activation, weekly registry, `SB-CP06-004/010` game-runtime tasks, R2 live publishing or milestone-complete claim. GPT will independently audit the published diff and update LF `TASKS.md`. All prior accepted results remain valid.
