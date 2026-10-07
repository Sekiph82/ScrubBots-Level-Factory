# M18 + CPX-004 R03 — Studio UTC + Production Approval Regression Closure

Document role: CODEX BUILDER LOG

## Chronological Record

### 2026-10-07 20:34 UTC — Session start and safe sync

- Canonical repository: `Sekiph82/ScrubBots-Level-Factory`; canonical persistent root checked: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Persistent checkout identity: root verified; branch `main`; origin `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`; starting HEAD `7c6051589d0a95fc785d7f182ccd0d7f8d7013ce`.
- Persistent checkout was left untouched: it is `0 ahead / 458 behind` after `git fetch --prune origin`, with extensive pre-existing modified and untracked owner-local paths. Existing 18 stashes and all registered worktrees were inventoried. No attempt was made to merge, stash, clean, reset, or discard this work.
- Active execution worktree: `%TEMP%\ScrubBots-Level-Factory\M18-R2-CPX004-R03`, detached at exact fetched `origin/main` `4c7312915c400b5d559a856ec0692d67883d5a9e`; initial status clean. `git worktree add --detach <path> origin/main` created this single authorized TEMP worktree.
- Current tracker state read from fetched `origin/main:TASKS.md`: `SB-CPX-004 — M18/CPX-004 R03 Studio UTC + Production Approval Regression Closure`; `STRICT_AUDIT_CHANGES_REQUIRED / R03_AUTHORIZED / LIVE_R2_AND_RELEASE_BATCH_STILL_EXTERNAL_GATES`.
- Read from current GitHub-tracked `main`: `TASKS.md`, `AGENTS.md`, `GOVERNANCE.md`, `.hiveai/prompts/M18_CPX004_R2_R03_PROMPT.md`, `.hiveai/audit-criteria/M18_CPX004_R2_R03_AUDIT_CRITERIA.md`, and `.hiveai/audits/M18_CPX004_R2_R02_STRICT_REAUDIT_V01.md`.
- R03 scope is limited to canonical Factory Studio UTC timestamp binding/rebuild, permanent production approval adversarial regressions, and requested regression/verification. Root `TASKS.md` and `.hiveai/audits/**` remain protected. No implementation, tests, or product files have been changed at this point.

### 2026-10-07 — Contract inspection and implementation plan

- Inspected `level_factory/scripts/factory_studio_release.gd`, `scripts/scrubbots_publish_handoff.py`, `content_pipeline/src/scrubbots_content_pipeline/scrubpack_spec.py`, `tests/unit/test_sb_cpx_004_scrubbots_publish.py`, and the M14 one-command publisher tests/approval path.
- Confirmed `normalize_created_at_utc()` is the accepted scrubpack authority: it rejects timezone-less/ambiguous values and normalizes explicit offsets to whole-second UTC `Z` form. R03 will call this before pack assembly and use the normalized value in review identity and rebuild inputs; no pack-builder clock read is needed.
- Confirmed the M14 production gate and exact-approval production path already exist. R03 adds adversarial wrong-manifest-SHA and wrong-content-version regression cases, plus retains the existing missing/exact approval tests; no production code redesign is planned.
- One initial shell command used a mistyped R02 TEMP path and failed with an invalid-directory error before running any command or changing any file. The corrected inspection succeeded.

### 2026-10-07 — R03 implementation and regression additions

- Updated `level_factory/scripts/factory_studio_release.gd` to obtain Studio publish time through `_current_utc_timestamp()`, which appends the explicit UTC `Z` to Godot's `utc=true` whole-second system string. The existing preflight/review and STAGING action continue carrying that single timestamp field.
- Updated `scripts/scrubbots_publish_handoff.py` to run `created_at_utc` through the accepted `normalize_created_at_utc()` scrubpack authority before pack assembly and identity construction. Invalid/timezone-less input returns `PREFLIGHT_INPUT_INVALID`; offset-aware values become canonical whole-second UTC. STAGING already re-runs preflight and rebuilds from the same request field, so the reviewed canonical timestamp is revalidated and reused.
- Added CPX-004 regressions for the actual Studio boundary wiring, timezone-less rejection before builder invocation, offset normalization before review, and exact canonical timestamp continuity into the STAGING rebuild.
- Added `level_factory/tests/factory_studio_timestamp_suite.gd`, a focused headless Godot runtime test that invokes the actual Factory Studio timestamp method and checks the generated value against canonical `YYYY-MM-DDTHH:MM:SSZ` shape.
- Added M14 one-command publisher adversarial regressions for same-shape owner approvals with wrong manifest SHA and wrong content_version. Existing tests cover missing approval and successful exact approval; the CPX-004 STAGING test covers `AWAITING_OWNER_PRODUCTION_PROMOTION`.
- Changed files so far: `level_factory/scripts/factory_studio_release.gd`, `scripts/scrubbots_publish_handoff.py`, `tests/unit/test_sb_cpx_004_scrubbots_publish.py`, `tests/unit/test_sb_cp03_011_one_command_publisher.py`, and `level_factory/tests/factory_studio_timestamp_suite.gd`. The builder log is the only evidence file being edited. No dependencies, credentials, live R2 writes, or fabricated release batches were introduced.

- Focused CPX-004 tests passed: `python -m pytest -q tests/unit/test_sb_cpx_004_scrubbots_publish.py` — 13 passed.
- Focused M14 production tests passed: `python -m pytest -q tests/unit/test_sb_cp03_011_one_command_publisher.py tests/unit/test_sb_cp03_008_production_promotion.py tests/unit/test_sb_cp03_009_production_manifest_activation.py` — 23 passed.
- First Godot runtime invocation included `--quit`; Godot returned exit code 0 but emitted no suite result, so it is not counted as a pass. Retry without the immediate-quit option so the SceneTree suite can run and report its own result.
- Two Godot commands using the `godot` GUI executable returned without the suite marker; they were not accepted as test passes. The supported console invocation `godot_console.exe --headless --path level_factory -s res://tests/factory_studio_timestamp_suite.gd` ran the actual helper and printed `M18-CPX004-R03 Studio UTC timestamp boundary PASS: 2026-10-07T20:40:00Z`. That first runtime pass also reported test-object/resource leak warnings at exit; the focused suite now explicitly frees the instantiated release surface, and will be rerun to check the cleanup.
- Corrected Godot runtime invocation passed with no leak warnings: `godot_console.exe --headless --path level_factory -s res://tests/factory_studio_timestamp_suite.gd` — exit 0; marker `M18-CPX004-R03 Studio UTC timestamp boundary PASS: 2026-10-07T20:40:15Z`.
- Focused timestamp/STAGING Python tests — 13 passed; focused M14 production/approval Python tests — 23 passed. The two earlier GUI `godot` invocations remain recorded as non-passing/no-result attempts.

- R01 ledger/idempotency regression selection passed: `python -m pytest -q tests/unit/test_sb_cp03_004_staging_pack_upload.py tests/unit/test_sb_cp03_008_production_promotion.py tests/unit/test_sb_cp03_009_production_manifest_activation.py tests/unit/test_sb_cp03_010_no_silent_live_overwrite.py tests/unit/test_sb_cp03_011_one_command_publisher.py` — 35 passed.
- First M11-M14 grouped regression command used Unix-style path globs that PowerShell passed literally to pytest; pytest reported the path missing and ran no tests. Re-running with PowerShell-expanded file paths.
- M11-M14 and CP07 regression selection passed after expanding file paths in PowerShell: 365 passed in 87.14s. Coverage included CP01/CP02/CP03/CP07 unit tests, CPX-004 unit tests, and the CP03 accepted factory-pack integration.
- Governance suite initial result: 202 passed, 2 failed. Both failures were caused by the newly added standalone GDScript suite: project-boundary policy disallowed a new GDScript filename and its `preload` usage. No existing governance/product behavior failed. To honor repository boundaries, moved the actual runtime assertion into the existing allowlisted `factory_studio_runtime_suite.gd` and removed only the standalone test file created during this task. This preserves actual Factory Studio runtime coverage without changing governance allowlists.
- Re-ran governance/tracker boundary selection after moving the timestamp check: 204 passed in 18.17s.
- Ran actual Factory Studio scene runtime suite with embedded Release-surface timestamp assertion: `godot_console.exe --headless --path level_factory -s res://tests/factory_studio_runtime_suite.gd` — exit 0; `SB-LF06-002-C001-R01 committed runtime suite PASS`.
- Timestamp helper is therefore verified at runtime through the real Factory Studio Release surface, not solely through a source-text assertion.

### 2026-10-07 — Full unfiltered pytest result

- Command: `python -m pytest -q` — **1700 passed, 20 skipped, 2 failed in 547.51s**.
- Failure 1: `tests/integration/test_release_route_a_authentic_verifier.py::test_default_route_a_verifier_runs_against_full_isolated_current_game_archive` confirmed its capability gates then failed to clone `https://github.com/Sekiph82/Scrubbots.git/` because the environment could not resolve `github.com` (`Could not resolve host: github.com`). No test or product files were changed to bypass this external failure.
- Failure 2: `tests/integration/test_sb_cpx_002_current_main_godot_integration.py::test_exact_verified_staging_pack_replays_with_current_main_godot` requires explicit `SCRUBBOTS_PROJECT`; none was configured in this process, so the adapter correctly raised `EXPLICIT_TEMP_GAME_AUTHORITY_REQUIRED`. No Desktop ScrubBots checkout or unverified game authority was used.
- The remaining 20 skips were reported by pytest, including unavailable ScrubBots/Godot integrations and the live R2 credential-gated roundtrip. The two failures are environment/capability failures outside R03 code; full-suite acceptance therefore remains unverified rather than green.

- Revalidated the approved existing TEMP game authority `%TEMP%\ScrubBots-Level-Factory\M18-R2-CPX004-R02-GAME-AUTHORITY`: canonical origin `https://github.com/Sekiph82/Scrubbots.git`, detached clean HEAD and fetched `origin/main` both `19a39876572506bcb1df33aaf339c409f60f5eeb`.
- Retried the CPX-002 current-main Godot integration with process-scoped `SCRUBBOTS_PROJECT` set to that exact TEMP path: 1 passed in 34.02s.
- GitHub connectivity subsequently recovered; `git ls-remote --heads https://github.com/Sekiph82/Scrubbots.git main` resolved `19a39876572506bcb1df33aaf339c409f60f5eeb`. Retrying the route-a verifier integration that failed during the earlier DNS outage before repeating full pytest.
- Retried the formerly DNS-blocked isolated Route A verifier integration after `git ls-remote` recovered: `tests/integration/test_release_route_a_authentic_verifier.py::test_default_route_a_verifier_runs_against_full_isolated_current_game_archive` — 1 passed in 426.33s.
- Both failures from the first full pytest now pass in isolated runs: Route A verifier 1 passed, CPX-002 Godot replay 1 passed against the revalidated TEMP authority. Starting final complete unfiltered pytest with `SCRUBBOTS_PROJECT` set process-locally to that same authority.
### 2026-10-07 21:22 UTC — Final full regression closure

- Final unfiltered command: `SCRUBBOTS_PROJECT=<verified TEMP game authority> python -m pytest -q` (PowerShell process-scoped environment) — **1716 passed, 6 skipped, 0 failed in 1122.92s (18:42)**.
- The six skips were truthful gates: one `SCRUBBOTS_SLOW=1` opt-in test; one live R2 roundtrip requiring owner writer credentials; and four tests requiring canonical game checkout/Godot capabilities not supplied by their specific gates. Both transient/environment failures from the earlier run passed on isolated retry before this final full run.
- R03 focused CPX-004 timestamp/STAGING suite: 13 passed. M14 approval/promotion/activation focused suite: 23 passed. R01 staging/ledger/idempotency regression selection: 35 passed. M11-M14 + CP07 publisher/provider/factory-pack regression selection: 365 passed. Governance/tracker selection: 204 passed. Actual Factory Studio headless runtime suite with Release timestamp assertion: PASS. CPX-002 integration against verified TEMP authority: 1 passed. Route A authentic verifier integration: 1 passed.
- `python -m compileall -q src scripts content_pipeline level_factory/scripts tests`: PASS.
- JSON parse check: 60 files PASS. JSON Schema meta-validation: 9 schemas PASS.
- `git diff --check`: PASS. Tracked diff + builder-log secret-pattern scan: 0 matches. `TASKS.md` and `.hiveai/audits/**` diff: 0.

### Implementation commit and publication preflight

- Final pre-publication `origin/main` fetch confirmed the authorized base remained `4c7312915c400b5d559a856ec0692d67883d5a9e`, local implementation base `0 ahead / 0 behind`, clean relative to the committed base.
- Implementation/test commit: `864301396c771c5cd5a11acb6c3dcd81e19a830a` (`fix(cpx004): canonicalize studio publish timestamp`). It contains only the two Factory Studio GDScript/test files, the CPX-004 service, and the CPX-004/M14 tests listed above. Builder log remains a separate pending evidence commit.
- Final pre-commit checks passed: compileall, 60 JSON parses, 9 schema meta-validations, `git diff --check`, 0 secret-pattern matches, and no `TASKS.md`/audit diff.

### 2026-10-07 — Builder-log whitespace correction

- The first staged builder-log `git diff --cached --check` reported one extra blank line at end of file. The shell sequence continued and created the separate log commit before that nonzero check was acted on. Removed the extra EOF blank line and recorded the correction; no product or test code changed.
