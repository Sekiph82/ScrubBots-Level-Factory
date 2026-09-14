# SB-LF00-002-C001 — Factory Project Boundaries & Local Documentation
Document role: CODEX BUILDER LOG

## 1. Start and authority

- Exact starting timestamp: `2026-09-14T22:55:24.2667070+03:00` (Europe/Istanbul).
- Canonical repository: `Sekiph82/ScrubBots-Level-Factory`.
- Canonical GitHub URL: `https://github.com/Sekiph82/ScrubBots-Level-Factory`.
- Canonical local mirror used exclusively: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Branch: `main`.
- Remote: `origin https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- Synchronization: fetched `origin/main` and fast-forwarded the clean canonical mirror from `de946e5f3e4eb571eead29c8575f142affc2dcfe` to `274330a11b523587cdf805a48bdefa38d6ca2b2e` with `git merge --ff-only origin/main`. No reset, rebase, force-push, discard, or sibling-repository discovery was used.
- Starting HEAD: `274330a11b523587cdf805a48bdefa38d6ca2b2e`.
- Starting `origin/main`: `274330a11b523587cdf805a48bdefa38d6ca2b2e`.
- Starting divergence: local `main` equals `origin/main`; no ahead/behind divergence.
- Starting worktree: clean before this required builder-log creation.
- Existing stash/worktree state was inspected; only the canonical mirror worktree is being used.

## 2. Required reads before implementation

Read completely before any product or test edit:

- Full authoritative GitHub prompt: `.hiveai/prompts/SB-LF00-002-C001_FACTORY_PROJECT_BOUNDARIES_AND_LOCAL_DOCUMENTATION_PROMPT.md`.
- Current root `TASKS.md`, whose active task is `SB-LF00-002`; root `TASKS.md` is owner-controlled and will not be edited.
- Previous strict PASS audit: `.hiveai/audits/SB-LF00-001-C001_INDEPENDENT_LEVEL_FACTORY_GODOT_PROJECT_BOOTSTRAP_STRICT_AUDIT.md`.
- `docs/migration/LF_CP_UNIFICATION_POST_CUTOVER_AUDIT_V01.md`.
- `docs/migration/LEVEL_FACTORY_CONTENT_PLATFORM_UNIFICATION_V01.md`.
- `docs/migration/LF_CP_REQUIREMENT_MAPPING_V01.md`.
- Current `level_factory/project.godot` and `level_factory/bootstrap.tscn`.
- Root `README.md`, `GOVERNANCE.md`, `AGENTS.md`, `.gitignore`, and current repository structure.

The legacy v3 paths `.hiveai/RULES.md`, `.hiveai/PROJECT.json`, `.hiveai/TASKS.md`, and `.hiveai/EVENTS.jsonl` are absent from the synchronized GitHub `main` branch. They were not recreated or used as current-state authority. The root `TASKS.md`, current cycle prompt, and previous strict audit are the active authorities for this cycle.

## 3. Scope and pre-implementation chronology

This builder log was created and verified before any `level_factory/` documentation, directory, scene, or test edit. Verification confirmed the exact H1 and document-role lines, a clean log diff, and that the log was the only worktree change at that point. The scope is limited to SB-LF00-002 project-local README/governance/directory boundaries, the contained bootstrap-scene move, focused structural tests, and required verification. SB-LF00-006/007/008, M01+, gameplay, Factory Studio, Content Platform, provider execution, and main-game work are out of scope.

No provider, cloud service, Magnific, PixelLab, API key, credential, network/runtime HTTP behavior, or main-game repository access is authorized or introduced.

## 4. Implementation chronology and decisions

- Updated `level_factory/project.godot` from `res://bootstrap.tscn` to the contained `res://scenes/bootstrap.tscn` main-scene reference.
- Moved the accepted minimal bootstrap scene from `level_factory/bootstrap.tscn` to `level_factory/scenes/bootstrap.tscn` without changing its three-line Godot 4 root `Node` content.
- Created `level_factory/README.md` with concise ownership, independent-openability, canonical-Python-Core, directory-role, root-tracker, main-game-boundary, provider-boundary, and deferred-policy statements. It does not duplicate the canonical roadmap.
- Created `level_factory/GOVERNANCE.md` with narrow ownership governance that explicitly defers task status, milestone/sprint/cycle acceptance, audit authority, and builder/auditor separation to root governance and root `TASKS.md`. It creates no competing control plane or tracker.
- Created `level_factory/docs/DIRECTORY_BOUNDARIES.md` defining `docs/`, `scenes/`, `scripts/`, `tests/`, and `output/`, and explicitly retaining the broader generated/candidate/cache/secret policy under `SB-LF00-006`.
- Created empty future-use boundary markers: `level_factory/scripts/.gitkeep`, `level_factory/tests/.gitkeep`, and `level_factory/output/.gitkeep`. No placeholder implementation code was added.
- Added `tests/unit/test_sb_lf00_002_project_boundaries.py` with nine focused structural/offline tests covering required paths, README/GOVERNANCE authority, directory roles, scene move/main-scene path, resource containment, dependency markers, implementation duplication/reparse points, and competing tracker claims.
- Narrowly updated `tests/unit/test_sb_lf00_001_project_contract.py` so the accepted LF00-001 structural tests continue to reject actual absolute/dependency markers while permitting the project-local documentation prose that SB-LF00-002 explicitly requires (for example, the mandated textual main-game ownership statement and provider-backed-feature prohibition).

## 5. Focused test failure and correction

- Initial combined focused command: `python -m pytest -q tests/unit/test_sb_lf00_001_project_contract.py tests/unit/test_sb_lf00_002_project_boundaries.py` → `14 passed, 2 failed`.
- Both failures were in new assertion wording: exact phrase checks did not account for Markdown line wrapping, and the README assertion expected `not duplicated` while the document correctly used `not moved, copied, or reimplemented in GDScript`.
- Correction: normalized whitespace in the documentation assertions and aligned the expected phrase with the documented boundary contract. No product behavior or scope changed.
- Corrected combined focused rerun → `16 passed` with the same pre-existing pytest cache-permission warning.
- Separate focused evidence: `python -m pytest -q tests/unit/test_sb_lf00_002_project_boundaries.py` → `9 passed`; prior `python -m pytest -q tests/unit/test_sb_lf00_001_project_contract.py` → `7 passed`.

## 6. Verification evidence

- Full regression: `python -m pytest -q` → `582 passed, 1 warning in 241.85s (0:04:01)`. The warning is the pre-existing `.pytest_cache` permission warning from the local environment.
- Compile check: `python -m compileall -q src tests` → success.
- Package import smoke: `python -c "import scrubbots_pixel_factory; print(scrubbots_pixel_factory.__name__)"` → `scrubbots_pixel_factory`.
- Module CLI help smoke: `python -m scrubbots_pixel_factory.cli --help` → success.
- Installed CLI help smoke: `scrubbots-pixel --help` → success.
- Godot smoke: `godot --headless --path level_factory --editor --quit` → success with existing `Godot Engine v4.7.2.stable.official.ed1daf0bf`.
- Scoped source/document scan excluding `.godot/`: no absolute owner-local paths, `res://../`, URLs/runtime HTTP markers, `HTTPRequest`, `WebSocket`, API-key/credential markers, plugin/addon declarations, preload/load calls, or competing task-checklist/current-state claims.
- The only `Sekiph82/Scrubbots` match is the required README textual ownership boundary; no `res://`, preload, load, or runtime dependency references it.
- Reparse-point scan: no symlinks or junction/reparse points under `level_factory/`.
- `git diff --check` → no whitespace errors; Git emitted only non-failing LF-to-CRLF working-copy warnings for existing modified text files.
- `git diff -- TASKS.md` → empty.

## 7. Files changed and boundary statements

Created:

- `.hiveai/codex-logs/SB-LF00-002-C001_FACTORY_PROJECT_BOUNDARIES_AND_LOCAL_DOCUMENTATION_CODEX_LOG.md`.
- `level_factory/README.md`.
- `level_factory/GOVERNANCE.md`.
- `level_factory/docs/DIRECTORY_BOUNDARIES.md`.
- `level_factory/scenes/bootstrap.tscn`.
- `level_factory/scripts/.gitkeep`.
- `level_factory/tests/.gitkeep`.
- `level_factory/output/.gitkeep`.
- `tests/unit/test_sb_lf00_002_project_boundaries.py`.

Changed:

- `level_factory/project.godot` — contained main-scene path update.
- `tests/unit/test_sb_lf00_001_project_contract.py` — compatibility of prior structural tests with required project-local boundary prose.

Moved/deleted:

- `level_factory/bootstrap.tscn` was moved to `level_factory/scenes/bootstrap.tscn`; the old path is absent.

The root Python package/source layout, semantic provider code, compiler, quality gates, and CLI remain in place and were not copied into `level_factory/`. No GDScript or Python implementation file was added. No dependency or license change was made. No root `TASKS.md` edit exists. No file in `C:\Users\sekip\Desktop\ScrubBots` was accessed or modified. No provider call, credit spend, network service, runtime HTTP path, API key, or credential was used.

## 8. Pre-commit state

At `2026-09-14T23:02:59.1503940+03:00`, local `main` remained at `274330a11b523587cdf805a48bdefa38d6ca2b2e`, equal to `origin/main`, with only the listed SB-LF00-002 implementation, test, moved-scene, and builder-log changes. This log is fully populated through pre-commit verification. Commit and push results will be appended chronologically after the implementation commit.

## 9. Commit and publication

- Implementation commit: `a442739810e642e0a3aa9936981e431ebe244953` (`Define SB-LF00-002 project boundaries`). It contains the project-local documentation/boundaries, contained bootstrap-scene move, focused tests, and this builder log through pre-commit verification.
- `git push origin main` for the implementation commit succeeded without force-push: `274330a..a442739 main -> main`.
- Immediately after that push, `git rev-parse HEAD` and `git rev-parse origin/main` both returned `a442739810e642e0a3aa9936981e431ebe244953`; local `main` and `origin/main` were equal and the worktree was clean.
- This final log update is evidence-only and introduces no product or test change. It is committed and pushed afterward with the same non-force procedure; final verification confirms local `HEAD == origin/main` and a clean worktree after the finalized log publication.
- No audit verdict is asserted here. Stop after final push for independent ChatGPT strict audit.
