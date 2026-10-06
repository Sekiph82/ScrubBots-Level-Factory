# SB-CP03-008-C001 - Explicit STAGING to PRODUCTION Promotion

Document role: CODEX BUILDER LOG

## Start and synchronization preflight

- Starting timestamp: `2026-10-06T23:42:10+03:00`.
- Canonical persistent root verified as `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`; origin `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`; branch `main`; persistent HEAD `7c6051589d0a95fc785d7f182ccd0d7f8d7013ce`.
- Ran `git fetch --prune origin` on the canonical persistent checkout. `origin/main` is `e200b95dfff241cc3cd62b7cb8ae39022ceee5a2`; divergence is 0 ahead / 377 behind. Persistent status has 889 entries (123 tracked modified, 766 untracked), 18 stashes, and 22 worktree entries. Its owner-local data remains untouched. The checkout is not synchronized because it contains extensive local work and is far behind; no merge/stash/reset/clean was attempted.
- Reused the single authorized TEMP M14 worktree `C:\Users\sekip\AppData\Local\Temp\ScrubBots-Level-Factory\M14-CP03-001-012-CPX002-MASTER`. It is clean, with `HEAD == origin/main == e200b95dfff241cc3cd62b7cb8ae39022ceee5a2`, 0/0.
- Read current `origin/main:TASKS.md`; M14 is ACTIVE / MASTER_BATCH_AUTHORIZED and orders CP03-008 immediately after CPX-002. Read root `AGENTS.md`, `GOVERNANCE.md`, the M14 interim audit and master prompt, and the live CP03-008 prompt and audit criteria from GitHub. The active master authorization allows continuing this child without inter-child handoff.
- Created this matching log before CP03-008 product changes or tests.

## Contracts and implementation

- Read the live CP03-008 prompt and audit criteria plus `provider.py`, `staging_download_verify.py`, `staging_manifest_publish.py`, `current_main_replay.py`, `release_state.py`, `manifest_v1.py`, and the CP03-006/007 unit fixtures.
- Added a narrow `ProductionPromotionProvider` protocol with exact object copy/read, append-only release event persistence, and conditional production-manifest write operations. It adds no vendor adapter or network behavior.
- Added the provider-neutral production transaction and immutable approval/precondition/report evidence. It requires a verified CP03-007 receipt bound to the canonical STAGING target, exact manifest and pack bytes, accepted CPX-002 current-main receipt with per-pack solved replay rows, exact owner approval, PRODUCTION target and negotiated capabilities, and a replayable staging event chain bound to the receipt's event digests.
- The transaction copies every verified source pack to the same logical key in PRODUCTION before beginning readback. It independently reads and compares exact bytes, lengths, hashes, provider identity, environment, and key for every copied object. No manifest call can occur unless all objects pass.
- Before manifest activation, it durably appends the hash-chained M11 `PROMOTION_PENDING` event. It rechecks current owner approval and the game repository/branch/commit/source hashes immediately at the manifest boundary, then makes one conditional manifest call with the pending-event digest. It appends `PRODUCTION_PROMOTED` after a successful write, or `FAILED` after a manifest conflict. There is no delete or rollback path; verified immutable pack copies remain in place on a blocked/failed manifest write.
- Added deterministic memory-provider tests for ordering, exact readback, missing CPX/approval, owner approval loss, production identity mismatch, game source drift, capability rejection, direct STAGING target rejection, stale STAGING evidence, non-successor manifest CAS, and manifest conflict/no rollback.
- Test correction history: initial focused run exposed that the CPX receipt's target label is uppercase `STAGING` while the staging-download receipt uses the canonical lowercase enum value; corrected the distinct schema checks. A later direct-target assertion first returned the owner-approval error because target validation followed approval validation; reordered the gate so a non-production target is rejected directly before provider calls. Final focused boundary regressions passed.
- An initial public API import smoke command failed because the source package directory was not on `PYTHONPATH`; repeated with `PYTHONPATH=content_pipeline/src`, and the public API import passed. Hardened provider and freshness callback exceptions so an uncertain manifest response is reported as an attempted write with durable `PROMOTION_PENDING` evidence and no blind retry. Added an explicit ambiguous provider-response test. The post-hardening focused set passed: **32 passed in 0.50s**.

## Verification and publication

- Final focused command `python -m pytest -q tests/unit/test_sb_cp03_008_production_promotion.py tests/unit/test_sb_cp03_007_staging_download_verify.py tests/unit/test_sb_cp03_006_staging_manifest_publish.py` -> **32 passed in 0.50s**.
- Final-code cumulative M14/M13/M12/M11/governance command `python -m pytest -q tests/unit tests/integration/test_sb_cpx_001_solver_identity_pack.py tests/integration/test_sb_cp03_002_factory_candidate_pack.py` -> **1,435 passed, 4 skipped in 170.65s**. The four skips require explicit canonical ScrubBots/Godot capability.
- Corrected public API smoke command with `PYTHONPATH=content_pipeline/src` passed. `python -m compileall -q content_pipeline/src src tests` passed. All **16** Content Pipeline JSON files parsed. `git diff --check` passed; Git printed only its standard LF-to-CRLF working-copy notices for `__init__.py` and `provider.py`.
- Final safe unfiltered command was run after clearing process `SCRUBBOTS_PROJECT`; `python -m pytest -q` -> **1,633 passed, 19 skipped in 695.12s**. Skips require an explicitly supplied ScrubBots checkout or Godot capability and did not inspect the protected Desktop game checkout.
- No dependencies, license inventory, vendor adapter, runtime HTTP access, API key, telemetry, or delete/rollback behavior was introduced. Provider tests use only deterministic in-memory fixtures.
- Final diff contains only `provider.py`, package exports, the new production promotion module, its focused unit test, and this child builder log. Root `TASKS.md`, prompts and audits were not modified.
- Product implementation commit `df021d8072bd670ed210e17c610805c4a03fc02a` was pushed normally after fetch/prune. Post-push fetch confirmed `HEAD == origin/main == df021d8072bd670ed210e17c610805c4a03fc02a`, 0/0; only this child evidence log remains untracked for its separate log commit.
- Child and M14 master evidence logs are being published in a separate evidence-only commit. Continue immediately to CP03-009 under the existing M14 master authorization after post-log parity is confirmed.
