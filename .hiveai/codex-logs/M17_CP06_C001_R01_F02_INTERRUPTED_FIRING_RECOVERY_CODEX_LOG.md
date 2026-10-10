# M17-CP06-C001-R01 — F02 Interrupted FIRING Recovery (ONE FIX ONLY)
Document role: CODEX BUILDER LOG

## Chronological Record

### 2026-10-10 17:38 UTC — Desktop-only session start and authorization
- Canonical root: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`; `origin` is `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`; current branch `main`.
- Fetched current `origin/main` and fast-forwarded Desktop from `d569d075e6eae01332d4a997d671fa5b34d5ee84` to `556074ad4259fcb2063ecd1a648c55610987be4e`; HEAD and origin now match, 0 ahead / 0 behind.
- Initial Desktop status had 57 untracked paths: 55 pre-existing owner paths plus the two existing `.m17-cp06-c001-pytest-*` directories. All 57 are protected by the R01 prompt and remain untouched. No staged or tracked modifications were present before this log.
- Read current `TASKS.md`, `.hiveai/prompts/M17_CP06_C001_R01_F02_INTERRUPTED_FIRING_RECOVERY_PROMPT.md`, `.hiveai/audits/M17_CP06_C001_STAGE1_STRICT_AUDIT_V02_CORRECTION.md`, `.hiveai/audit-criteria/M17_CP06_C001_R01_F02_INTERRUPTED_FIRING_RECOVERY_AUDIT_CRITERIA.md`, and `docs/process/CODEX_SYNC_PUBLISH_STANDARD_V01.md` from fetched current main.
- Exact scope is F02 in `run_due()` only: recover interrupted `FIRING` schedules with the original durable claim/idempotency key, revalidate before retry, and prevent duplicate activation effects under uncertain acknowledgments. F01 is withdrawn and will not be changed. Existing Stage 1 7/63 PASS evidence will not be rerun.
- Inspected `run_due()`, `CandidateActivator`, `ScheduleJournal`, and `SQLiteLocalProvider.claim_due()`/`finish_due()` plus existing due-run tests. Confirmed `claim_due()` persists `f"{schedule_id}:{scheduled_revision}:{candidate_sha256}"` when SCHEDULED becomes FIRING and requires that exact key on FIRING recovery, while current `run_due()` uses the incremented observed revision and therefore produces a different key.
- Planned bounded evidence: add only new F02 interruption/recovery cases using an in-memory SQLite-backed journal fixture to avoid creating more filesystem scratch. Run only the new F02 tests once. No broad suites, compileall, Godot, solver, VOID, or disk-heavy checks.
- No product source or existing test content has been edited at this entry.

## Implementation and Verification

(To be updated chronologically with exact changes, targeted F02 test result, failures/corrections if any, diff/secret checks, commits, push and final parity.)
### 2026-10-10 17:38–17:41 UTC — F02 implementation and focused evidence
- Source change: `run_due()` now reconstructs the original SCHEDULED claim revision when the current journal head is FIRING (`firing.revision - 1`), preserving the already persisted key format `schedule_id:scheduled_revision:candidate_sha256`. Invalid FIRING revision 1 fails closed. Due-time revalidation still runs before every recovered activation.
- Added the `CandidateActivator` protocol requirement that activation effects be durably deduplicated by the idempotency key. A false result or exception may represent a lost remote acknowledgment; the operation remains FIRING and retries with the same key.
- Test fixture change: `SQLiteLocalProvider` now accepts an existing SQLite connection as well as a path, using a retained `:memory:` connection for the F02 cases. File-backed behavior for existing cases remains routed through the same `_connect()` helper. The new tests create no filesystem scratch.
- Added only F02-focused tests: parameterized process interruption before activation and after activation but before finalization, including persisted-claim equality, revalidation on recovery, exact same activation key, one deduplicated side effect and terminal idempotency; plus stale-revalidation blocking and terminal non-reactivation.
- An initial grouped patch did not match the test fixture context; it made no file changes. The fixture was then updated with narrower edits. No test failed.
- Ran only the new F02 cases once: `python -m pytest tests/unit/test_m17_release_controls.py -q -p no:cacheprovider -k f02_interrupted_firing` — 3 passed, 7 deselected in 0.82s. The existing M17 7-test and 63-test results were not rerun; no compileall or broad verification was run.
- `git diff --cached --check` passed; targeted credential-pattern scan of the changed module and test file found no matches. No owner-untracked path was staged or touched. The 57 protected untracked paths remain; this new log is the only additional untracked file before its separate commit.
- Source/test commit: `01d65c0` (`Fix F02 interrupted FIRING claim recovery`).
