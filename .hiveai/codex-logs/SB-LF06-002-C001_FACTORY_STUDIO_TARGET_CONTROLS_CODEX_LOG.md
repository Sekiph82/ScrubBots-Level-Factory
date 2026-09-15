# SB-LF06-002-C001 — Factory Studio Target Controls

Document role: CODEX BUILDER LOG

## Start

- Timestamp: 2026-09-15T15:47:49+03:00.
- Canonical repository verified as `Sekiph82/ScrubBots-Level-Factory` with origin `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- Branch: `main`.
- Starting local HEAD: `ad7805a88ca6bcd860a0e9fb06101515c9d7f43a`.
- Starting `origin/main`: `ad7805a88ca6bcd860a0e9fb06101515c9d7f43a`; ahead/behind: `0/0`.
- Initial tracked status was clean. Four pre-existing untracked owner-local Godot UID files were preserved and were not read, edited, staged, or deleted.
- Synchronization used a non-destructive fast-forward fetch/merge of `origin/main` only. No sibling repository was accessed.

## Authority and scope read

- Read the current root `TASKS.md`; it remains unmodified and is the sole current project-status tracker.
- Read the closing strict audit for `SB-LF01-005-C001-R01` from the supplied GitHub URL.
- Read the complete authoritative `SB-LF06-002-C001` prompt from the supplied GitHub URL.
- Read the repository `AGENTS.md` and `GOVERNANCE.md` instructions.
- Read the current Factory Studio scene, shell, navigation, workspace, gateway, existing LF06-001 runtime contract, focused LF06-001 Python tests, canonical Python difficulty/mode/request contracts, and the existing Studio workspace documentation.

## Boundary correction before formal implementation

An initial uncommitted Studio target-controls edit was attempted before this matching log was created. That sequencing was incorrect. The attempt was reverted with `apply_patch` before any test, documentation, tracker, prior audit, owner-local file, or sibling repository change. The formal implementation sequence begins after this log entry; the premature attempt is recorded here rather than hidden.

The active scope is limited to the Factory Studio Generate target-controls and presentation draft state. Python Factory Core remains authoritative. No GDScript compiler, difficulty/dimension policy, Generate/Solve/Validate action, provider, network, Dashboard operation, Import, Library, Content Platform, solver, or main-game work is in scope.

## Planned implementation

- Add a real Generate presentation form with canonical difficulty and mode choices, independent width/height controls bounded to the canonical 20..59 envelope, seed text, bounded candidate-presentation text, and an explicit draft/unavailable state.
- Keep edits local to the presentation draft and expose a deterministic draft snapshot that is not a canonical `GenerationRequest`.
- Preserve truthful inert states for all non-Generate surfaces and the existing Core gateway `UNAVAILABLE` boundary.
- Add executable Godot scene-instantiation/interactions and Python cross-language contract regression evidence.

## Required verification

The implementation will be checked with focused LF06-002 tests, LF06-001 regressions, executable Godot runtime checks, canonical LF01 dimension/request tests, the full Python suite, compile checks, headless Godot smoke, diff whitespace checks, and a final scope/status review. No credentials or provider/network services will be used.

## Implementation and verification chronology

- Added `level_factory/scripts/factory_studio_target_controls.gd` as presentation-only state: canonical difficulty/mode choices, independent 20..59 width and height controls, seed text, bounded candidate-presentation label, deterministic draft snapshot, and truthful DRAFT/UNAVAILABLE/no-operation readout.
- Added the Generate target-controls node to the existing Studio scene and made the workspace show it only for Generate while preserving inert truthful placeholders for other surfaces and the Core gateway boundary.
- Added `tests/support/factory_studio_target_controls_contract.gd` for executable scene instantiation, Generate navigation, control-path checks, canonical choices/bounds, rectangular edits, deterministic draft state, unavailable status, no operational action button, and navigation round-trip stability.
- Updated the existing LF06-001 executable runtime contract for the now-authorized Generate draft surface, and added Python cross-language tests binding the GDScript constants to canonical Python `Difficulty`, `GeneratorMode`, and `PRODUCTION_DIMENSION_ENVELOPE`.
- Updated the existing project-boundary regression allowlist only for the newly authorized target-controls script; no external reference, provider, or duplicate Core boundary was introduced.
- First focused Python run: `python -m pytest -q tests/unit/test_sb_lf06_001_factory_studio_workspace.py tests/unit/test_sb_lf06_002_factory_studio_target_controls.py` — 11 passed, one pre-existing pytest cache-permission warning.
- First Godot executable attempt exposed a compile-order defect from a typed `FactoryStudioTargetControls` reference in the workspace/runtime test. Removed that global-class type dependency in favor of the committed scene-node contract. The corrected LF06-001 and LF06-002 runtime contracts then passed with exit code 0.
- A disposable project-local Godot runner was used only to execute the committed root support contracts because this local Godot build did not reliably attach `res://../tests` scripts when passed directly. The disposable runner scenes/scripts and temporary main-scene substitutions were removed/restored immediately after verification; none are part of the final diff. Final outputs: `SB-LF06-002-C001 target controls runtime contract PASS`, exit 0; `SB-LF06-001-C001-R01 runtime contract PASS`, exit 0.
- Canonical regression run: `python -m pytest -q tests/unit/test_sb_lf01_005_dimension_envelope.py tests/unit/test_m02_request.py` — 64 passed, one pre-existing pytest cache-permission warning.
- `python -m compileall -q src tests` passed.
- `git diff --check` passed.
- Initial full-suite run reached 683 passed but failed five existing boundary assertions because the disposable runner was still present and the newly added target script had not yet been staged. Removed the disposable files, updated the authorized script allowlist, staged the intended tracked files, and reran the affected boundary subset: 34 passed.
- Final full regression: `python -m pytest -q` — 688 passed, one pre-existing pytest cache-permission warning, exit code 0.
- Final headless Studio smoke: `godot --headless --path level_factory --quit` — exit code 0. A `--quit-after=1` invocation did not terminate in this local Godot process wrapper and was terminated; the explicit `--quit` smoke completed successfully. No parse, missing-resource, provider, network, or sibling-repository error was observed.

## Boundary and safety review

- No provider/network service, Magnific, PixelLab, Perchance, credential, token, API key, or secret was read or used.
- No `Sekiph82/Scrubbots` repository was accessed.
- No Python Factory Core was copied or reimplemented in GDScript; no request validator, compiler, difficulty formula, dimension policy, provider, solver, or operational action was added.
- No `TASKS.md`, prior prompt, prior audit, governance tracker, generated owner-local UID, or sibling repository file was changed. The four pre-existing untracked owner-local UID files remain untracked and preserved.
- No dependency or license change.

## Final pre-commit state

- Intended staged files are limited to the matching builder log, Factory Studio scene/workspace/target-controls implementation, executable Studio runtime contracts, the narrow project-boundary allowlist update, and focused LF06-002/LF06-001 regression tests.
- Final tracked diff summary before commit: 9 files, 450 insertions, 13 deletions.
- Final local tracked worktree status before commit: only the intended staged files above; the four pre-existing untracked UID files remain untouched.
- Commit and push/equality results will be appended chronologically after the implementation commit and final publication checkpoint are observed. No final SHA is claimed in this pre-commit entry.

## Implementation publication checkpoint

- Implementation commit created: `d8623ab4ccc4c62c408fb8841ebfca6b7ac29b42` (`Implement Factory Studio target controls`).
- Implementation commit contains the nine intended files listed above; root `TASKS.md` is not changed.
- Push command: `git push origin main` — succeeded; remote advanced from `ad7805a88ca6bcd860a0e9fb06101515c9d7f43a` to `d8623ab4ccc4c62c408fb8841ebfca6b7ac29b42`.
- Immediately after the implementation push, local HEAD and `origin/main` both resolved to `d8623ab4ccc4c62c408fb8841ebfca6b7ac29b42`.
- The pre-existing four untracked owner-local UID files remained untracked and were not included.

## Final publication checkpoint

- This log update is the final publication content. The final publication commit is created from this exact staged log and pushed to `main`; its resulting SHA is handed off externally rather than self-referenced inside the commit content.
