# SB-LF01-005-C001-R01 — Manifest Version Gate & Workload Guidance Remediation
Document role: CODEX BUILDER LOG

## 1. Start and pre-edit repository baseline

- Start timestamp: 2026-09-15T14:29:37+03:00.
- Canonical repository root: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Canonical repository: `Sekiph82/ScrubBots-Level-Factory`.
- Branch: `main`.
- Origin: `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- Synchronization: `git fetch origin main`, then non-destructive `git merge --ff-only origin/main`.
- Synchronized starting HEAD and `origin/main`: `aa957110269ab1449e0922829b1b4bf35c36b434`.
- Initial tracked status: clean and equal to `origin/main`.
- Preserved pre-existing owner-local untracked files without reading or deleting their contents:
  - `level_factory/scripts/factory_core_gateway.gd.uid`
  - `level_factory/scripts/factory_studio_navigation.gd.uid`
  - `level_factory/scripts/factory_studio_shell.gd.uid`
  - `level_factory/scripts/factory_studio_workspace_page.gd.uid`
- Existing stashes and the single canonical worktree were inspected and left unchanged.
- No implementation, test, documentation, tracker, prompt, or audit file was edited before this log was created.

## 2. Required reads and bounded scope

- Read the current root `TASKS.md`; it identifies the SB-LF01-005 workstream and forbids builder tracker edits.
- Read the complete R01 remediation prompt from GitHub:
  `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/SB-LF01-005-C001-R01_MANIFEST_VERSION_GATE_AND_WORKLOAD_GUIDANCE_REMEDIATION_PROMPT.md`.
- Read the complete source strict audit from GitHub:
  `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF01-005-C001_INDEPENDENT_DIMENSION_ENVELOPE_MIGRATION_STRICT_AUDIT.md`.
- Read the original C001 prompt and finalized C001 builder log from GitHub.
- Read `AGENTS.md`, `GOVERNANCE.md`, `src/scrubbots_pixel_factory/cli/main.py`, the canonical dimension contracts, relevant request/difficulty/CLI tests, `README.md`, and `pyproject.toml`.
- The R01 boundary is limited to exact batch-manifest version typing/corruption handling, non-binding workload guidance plus its narrow regression assertion, and this R01 builder log. The accepted C001 independent 20..59 architecture and historical schema-v1 replay remain unchanged.
- No `TASKS.md`, Studio product, provider, solver, Content Platform, main-game, or sibling-repository work is authorized.

## 3. Audit findings and implementation plan

- F-SB-LF01-005-MAJOR-001: `_validate_manifest()` currently uses membership against `{1, 2}` without an exact integer type check, allowing JSON booleans to select a compatibility branch because `True == 1`. Repair this with `type(version) is int` plus the existing supported-version check, and add fail-closed cases for booleans, float, string, null, and unsupported integer values while retaining valid v1/v2 replay.
- F-SB-LF01-005-MINOR-002: add concise user-facing guidance to the existing README or CLI help surface. It must state independent width/height legality in 20..59, rectangle legality regardless of difficulty, larger area may require more processing/resources, and that this is advisory only, never changes legality, and is not difficulty. No unmeasured thresholds or size bands will be invented.
- F-SB-LF01-005-MINOR-003: keep R01 publication chronology truthful. The implementation commit, pushed equality checkpoint, and final log-only publication commit will be distinguished. The log will not claim a terminal SHA before later log publication and will hand off the actual final publication SHA externally.

## 4. Implementation record

Implementation and test commands will be appended chronologically below. Failed commands and corrections will be retained truthfully. No secrets or credentials will be recorded.

## 5. Implementation and focused verification

### 2026-09-15T14:35:00+03:00 — first implementation pass and focused corrections

- Updated `src/scrubbots_pixel_factory/cli/main.py` so `_validate_manifest()` requires `type(manifest_version) is int` before accepting only manifest versions `1` and `2`; valid v1 and v2 parsing branches are otherwise unchanged.
- Added explicit valid-v2 batch create/resume evidence and parameterized invalid manifest-version resume coverage for `true`, `false`, `1.0`, `"1"`, `null`, `3`, and `99` in `tests/integration/test_m09_cli_integration.py`. Existing valid-v1 replay evidence remains intact.
- Added the required non-binding workload guidance to the existing `README.md`. It references the canonical `20..59` envelope, states rectangle legality independent of difficulty, warns only that larger area may require more processing/resources, and states that guidance is advisory, never changes legality, and is not difficulty.
- Added `test_workload_guidance_is_advisory_and_uses_canonical_envelope()` to the existing C001 dimension test file. It reads the README guidance and derives the numeric range from `PRODUCTION_DIMENSION_ENVELOPE` rather than defining a second numeric policy.
- First focused command:
  `python -m pytest -q tests/integration/test_m09_cli_integration.py::test_current_v2_batch_manifest_is_explicit_and_replayable tests/integration/test_m09_cli_integration.py::test_resume_rejects_non_strict_or_unsupported_manifest_versions tests/integration/test_m09_cli_integration.py::test_version1_batch_manifest_replays_legacy_omitted_dimension_semantics tests/integration/test_m09_cli_integration.py::test_historical_v1_omitted_request_reproduces_without_current_dimension_re_resolution tests/unit/test_sb_lf01_005_dimension_envelope.py`
- First result: collection failed because the new test imported `PRODUCTION_DIMENSION_ENVELOPE` from the package root instead of `scrubbots_pixel_factory.contracts`. Corrected only that test import.
- Immediate rerun result: `1 failed, 55 passed, 2 warnings`; the remaining failure was the test slicing README at `Stable domain exit codes:` while the README wording is `Stable domain exit codes are:`. Corrected the test's section delimiter; no product behavior was implicated.
- The next rerun still reported one guidance assertion failure because Markdown line wrapping split the expected sentence across a newline. Corrected the assertion to normalize whitespace before checking the exact guidance statements; this remains a documentation assertion only.
- Final focused R01/C001 compatibility command result: `56 passed, 1 warning in 4.96s`. This covers strict manifest versions, valid v1 bundle/batch replay, valid v2 batch create/resume, the C001 dimension-envelope suite, and the guidance assertion.

### 2026-09-15T14:48:00+03:00 — affected regression result

- Ran:
  `python -m pytest -q tests/unit/test_difficulty_contract.py tests/unit/test_m02_request.py tests/unit/test_m05_wfc_contracts.py tests/unit/test_m07_quality.py tests/integration/test_m01_contract_acceptance.py tests/integration/test_m03_generator.py tests/integration/test_m05_wfc_generator.py tests/integration/test_m06_router.py tests/integration/test_m09_cli_integration.py`
- Result: `175 passed, 1 warning in 56.39s`.

### 2026-09-15T14:56:00+03:00 — full regression result

- Ran `python -m pytest -q`.
- Result: `685 passed, 1 warning in 270.23s (0:04:30)`. The only warning is the pre-existing Windows pytest cache permission warning; no test failed.

### 2026-09-15T15:02:00+03:00 — toolchain and offline smoke results

- `python -m compileall -q src tests` passed.
- Package import/router smoke passed: canonical envelope printed `20 59`, and an offline `23x47` request generated a successful `23x47` result.
- Both `python -m scrubbots_pixel_factory.cli --help` and installed `scrubbots-pixel --help` passed with the same offline CLI command surface.
- `git diff --check` passed; Git emitted only normal line-ending normalization warnings.
- Offline CLI smoke passed for explicit `23x47` MASK generation and reproduce (`MATCH`). Two omitted-axis EASY runs with the same seed both resolved to `37x33`, proving deterministic current resolution. Disposable outputs were written outside the repository under the system temporary directory; no provider or network service was called.

## 6. Final scope review before commit

- Product/test/documentation changes are limited to `src/scrubbots_pixel_factory/cli/main.py`, `README.md`, `tests/integration/test_m09_cli_integration.py`, and `tests/unit/test_sb_lf01_005_dimension_envelope.py`, plus this matching R01 log.
- `git diff -- TASKS.md` is empty. No C001 dimension contract, Factory Studio feature, provider, solver, Content Platform, main-game, or sibling-repository file is changed.
- The four pre-existing owner-local Godot UID files remain untracked, unstaged, and preserved.
- Dependency and license files are unchanged. No credentials, API keys, tokens, or network/provider calls were used.

## 7. Implementation publication checkpoint

- Implementation commit: `c84f182ac07813dda6095ff6db5ad58dd210627d` (`Remediate manifest version gate and workload guidance`).
- The implementation commit contains only the four reviewed product/test/documentation files listed above; this R01 log remains intentionally uncommitted until the final log-only publication.
- `git push origin main` succeeded: `aa95711..c84f182`.
- After `git fetch origin main`, observed local `HEAD == origin/main == c84f182ac07813dda6095ff6db5ad58dd210627d` with no tracked divergence.
- This is the pushed implementation equality checkpoint, not the final publication commit. A final log-only commit remains planned; this log does not claim the current checkpoint is terminal.

## 8. Final log publication discipline

- The next commit is intentionally log-only and will publish this finalized R01 builder log.
- The final log cannot truthfully embed its own commit SHA. It therefore records the observed pre-final equality checkpoint above and leaves the actual final publication SHA to the post-push handoff.
- After that log-only commit is created, it will be pushed to `main` and local/remote equality will be checked. No further builder commit will be made after the final publication commit.
