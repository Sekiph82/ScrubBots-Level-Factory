# SB-LF02-008-R01 | Restore TEST negative gate without weakening owner-source verification | No CI

Date: 2026-10-15 Europe/Istanbul
Builder: Codex
Authoritative repo: `Sekiph82/ScrubBots-Level-Factory` / `main`
Canonical Desktop root: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
Independent audit: `.hiveai/audits/SB_LF02_008_M02_02_R00_INDEPENDENT_SOURCE_AUDIT_PARTIAL_V01.md`

## Owner authority
Read **live root `TASKS.md` first**, current `AGENTS.md`, `GOVERNANCE.md`, `docs/process/CODEX_SYNC_PUBLISH_STANDARD_V01.md`, active R01 prompt, source audit and LF02-008 previous master. Owner budget **ABSOLUTE ZERO GitHub Actions, CI or workflows**. No workflow_dispatch, no CI alternative, no staged workflow modifications, no hosted test or license/dependency/provider change. Use safe bounded local checks only.

`SB-LF02-008` remains GPT PARTIAL/OPEN pending F01. Builder source `95da9a26001ece2e1191ee5b7fe362810fecc4c8`, final builder head `05e7b63aea02cb3509f5ba2d944e7608fa74ae87`. GPT inspected source and found one definite negative-path contract mismatch but **did not run it**. Do not claim new test failures before reproducing.

## F01 exact bug and fix
`tests/unit/test_sb_lf01_009_010_candidate_and_semantic_contracts.py::test_generated_candidate_defaults_to_test_and_is_request_bound` expects `ReleaseError` matching `"TEST candidate"` from both `validate_pool_candidate_provenance(_candidate(owner_source=False), None)` and `enter_release_pool(...)`. Current `release_pool.py::validate_pool_candidate_provenance` calls `_verify_candidate_source_grid_binding` on this clearly TEST-class bundle before negative rejection, which reads nonexistent owner-source candidate paths and raises an unrelated ReleaseError.

**Repair this one boundary only:**
1. After strictly extracting `classification = generator_metadata.get("classification")`, reject a record whose candidate class is not `PRODUCTION_CANDIDATE` as a negative-only disposition using established `TEST candidate cannot enter...` messaging (including other nonproduction classes), without filesystem reads or owner source proof needed to reject.
2. **Never permit** a merely claimed positive `PRODUCTION_CANDIDATE` to pass this early gate. For any positive claim, still require `_verify_candidate_source_grid_binding` to read/verify canonical raw bytes, decoded grid and actual artwork, followed by `validate_verified_owner_upload_classification` and exact current owner ACCEPT gate, even if claim is caller-forged.
3. Keep malformed classification fail-closed without confusing it with authority; do not trust origin strings or `approved_by`, do not restore WFC `OWNER_APPROVED`, do not remove verification at bundle build/read or Pool. Preserve ALL current accepted 002, 9 READY, 140 original PNG, LF02-004, R05, Studio/Release/shortcut and game repo.
4. Avoid modifying `candidate_provenance.py`, `output.bundle`, WFC or other modules unless a reproducible bug forces an in-scope correction. Explain any enlargement before editing.

## Focused local tests (no scratch amplification)
- First make read-only baseline to establish clean source, current branch/origin, 3,220 user+task untracked paths and their ownership categories. Owner original count 3,204 and **16 blocked-policy task-created** `.pytest-scratch-sb-lf02-008-20261015/` files; **leave all 3,220 exactly as-is**. Do NOT try again to delete 16, use alternate removal methods, create worktrees/clones, write Windows TEMP, or create more task scratch. Those 16 have known task ownership, but deletion is currently policy-denied. No blanket clean.
- Verify source fix via a **no-filesystem-fixture** negative test or direct Python in-memory repro using the existing `_candidate(owner_source=False)` helper, both Pool negative call paths. Add a local targeted test of forged `candidate_class="PRODUCTION_CANDIDATE"` on metadata-only `_candidate(owner_source=False)` that MUST still raise ReleaseError and cannot construct a real source/ACCEPT. Ensure no source file is opened for a trivially TEST-class candidate (monkeypatch source verifier to throw to prove not reached, or equivalent).
- If safe under owner-no-TEMP constraints, run precisely affected tests, for example the two no-tmp tests with `python -B -m pytest -q -p no:cacheprovider ...::test_generated_candidate_defaults_to_test_and_is_request_bound` and `...::test_owner_upload_metadata_without_source_bytes_cannot_create_production_export`; **only** if they create no new scratch or pytest temp artifacts. `PYTHONDONTWRITEBYTECODE=1`; capture output inline/log. Do not rerun full 24-case suite while cleanup of scratch is denied. If even isolated tests require new scratch, perform static/AST + read-only in-memory direct checks and record TESTS NOT RUN where applicable.
- Preserve prior red history, initial 22 PASS/2 FAIL and later direct checks; do NOT rephrase as clean `24/24`. Record actual new SHA/commands/results, check `git diff --check`, AST and strict unchanged workflow diff. NO GitHub Actions run.

## Git safety/publication
- Only canonical Desktop working directory. Follow `git fetch --prune origin`, ff-only only if tracked clean and no untracked path collision. No reset/rebase/auto-stash/force/clean, no new TEMP/worktree/clone, no changes to user work. If unsafe branch divergence STOP with exact paths/SHA.
- Codex edits only the smallest owner-invariant `release_pool.py` and necessary targeted regression tests; append chronological builder evidence to existing `.hiveai/codex-logs/SB-LFX-018-C001-R02-R05_PRODUCTION_HISTORY_FULL_REGRESSION_EVIDENCE_CODEX_LOG.md`. Do not modify `TASKS.md`, GPT audit/criteria, prompts, HANDOFF, `.github/workflows`, existing 16 scratch or other owner files.
- First source commit, log commit separately. Publish normal main push only after `origin/main` is ancestor of local HEAD, workflow is manual-only, and net workflow diff is zero. Fetch again and verify exact HEAD = origin/main and 0/0, tracked clean and unchanged untracked-path count. Return full GitHub builder-log URL. Independent GPT audit follows and may close or keep LF02-008 OPEN. No owner or R05 production acceptance is implied.
