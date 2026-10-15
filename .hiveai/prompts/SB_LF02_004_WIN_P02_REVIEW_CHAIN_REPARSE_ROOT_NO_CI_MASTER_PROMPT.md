# SB-LF02-004-WIN-P02 | Close ART_FIRST owner-review reparse trust boundary | No CI

Document role: CODEX BUILDER MASTER PROMPT
Date: 2026-10-16 Europe/Istanbul
Repository: Sekiph82/ScrubBots-Level-Factory, main
Canonical Windows checkout: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Mandatory current truth
Read root `TASKS.md` FIRST (only tracker), `AGENTS.md`, `GOVERNANCE.md`, `docs/process/CODEX_SYNC_PUBLISH_STANDARD_V01.md`, current master prompt, `.hiveai/audits/SB_LF02_004_WIN_P01_REPARSE_INDEPENDENT_AUDIT_PARTIAL_V01.md`, P01 builder log, `src/scrubbots_pixel_factory/generators/router/art_first.py`, `owner_upload.py`, `studio_extensions.py` and focused test file.

**ZERO GitHub Actions, CI, workflow edits, hosted runner/provider usage, paid calls, OS TEMP and new scratch.** Never modify Windows Developer Mode, privilege/registry or use admin. No cleanup attempts, no worktree/clone, reset, rebase, stash, force/clean. Preserve all 3,220 builder-reported owner+task untracked entries, including 16 previously deletion-denied files; no more scratch.

## Independent F01 precisely
P01 hardening of canonical `owner-uploads` and `studio-derived-candidates` roots is source-positive, and 5 focused synthetic tests + 3 read-only Windows symlink/junction *classification* checks were builder-reported PASS. But `_candidate_and_review` currently uses:
```python
review_root = extensions_root() / "owner-review"
if review_root.is_symlink() or not review_root.is_dir(): ...
```
`studio_extensions.extensions_root()` itself calls `.resolve()` and may erase trust-boundary reparse status before this check. Directory junctions may satisfy `not is_symlink()`; `_safe_file` only proves containment under the *already redirected* `review_root`. This review folder contains current ACCEPT evidence so physical root authority matters. GPT audit: `.hiveai/audits/SB_LF02_004_WIN_P01_REPARSE_INDEPENDENT_AUDIT_PARTIAL_V01.md`.

## One narrow fix
1. Within ART_FIRST ONLY, derive the raw canonical `studio-extensions` expected path from `owner_upload_root().parent / "studio-extensions"` **before following symlinks or junctions**. Refuse reparse or unexpected / unresolved root via existing `_path_is_reparse_point`, and require strict resolved physical parent equals verified `owner_upload_root().parent`. Do not alter global Studio `extensions_root()` or unrelated owner batch/recovery behavior. Compatible test-local canonical source-root overrides may be used only when anchored under the same test-local `owner_upload_root().parent`.
2. Likewise reject reparse-point `owner-review` dir before enumeration, require its `resolve(strict=True).parent` equals the canonical validated extensions dir. Store only checked nonredirected root for `iterdir` and subsequent bounded `_safe_file` reads. Retain canonical review-chain validation, immutable JSON/bytes/grid hashes/current ACCEPT, `UNAVAILABLE/NEEDS_OWNER_ACCEPT` fail-closed status, ART_FIRST TEST/PREVIEW only.
3. If code currently refers to injected `extensions_root` for tests, decide whether it should be retained only as a consistency assertion against checked canonical `studio-extensions`; do not allow it to name an arbitrary alternate review directory. Test old synthetic ART_FIRST fixtures and production code path for compatibility.
4. Do not touch `owner_upload.py`, `output/bundle.py`, Pool, CLI, Godot Studio, installer, game, provider/AI creator authority, unless a precisely demonstrated conflict requires smallest isolated change. Do not make global review-storage migration.

## Focused safe proof
- Add **new targeted in-memory** tests with synthetic reparse helper marker: `studio-extensions` redirected/junction and `owner-review` redirected/junction each must fail before `iterdir` / `_safe_file`; also test an injected `extensions_root` outside canonical verified output root if the function remains injectable. Use explicit monkeypatch undo, not new filesystem fixtures, no pytest session, no TEMP.
- Ensure valid canonical review path still works using existing source-backed synthetic ART_FIRST test logic without adding scratch or owner file reads; if cannot run safely, mark old fixture full test NOT RUN and make bounded pure/path checks. Retain P01 tests as historical; avoid claiming 11-suite/full-suite pass on new source unless rerun.
- Source/static validation `python -B`, `PYTHONDONTWRITEBYTECODE=1`, `ast.parse`, `git diff --check`, count exact PASS/FAIL/SKIP/NOT RUN and log source SHA. No native app-path symlink creation due current privilege/owner policy; log **real NTFS guard proof NOT RUN**, **TOCTOU race-free handle proof NOT RUN**; do not infer passing them from mocked guards.

## Desktop/GitHub controls
1. Verify exact repository origin and current `main`; `git fetch --prune origin`, zero owner untracked collisions; if safe tracked clean/behind, `git merge --ff-only origin/main`; otherwise stop with exact SHA/conflict, no worktree/TEMP escape.
2. Implement narrowly in `src/scrubbots_pixel_factory/generators/router/art_first.py` and `tests/unit/test_sb_lf02_004_art_first.py`. Append results chronologically to existing `.hiveai/codex-logs/SB-LFX-018-C001-R02-R05_PRODUCTION_HISTORY_FULL_REGRESSION_EVIDENCE_CODEX_LOG.md`. Do not edit root TASKS, prompts/audits/criteria, HANDOFF, workflows, owner PNGs/accepted 002/9 READY, Release/shortcut or other projects.
3. Commit source/tests, log separately where possible. Before normal main push confirm actual origin/main ancestor, no `.github/workflows` diff and manual-only workflow trigger. `git push origin HEAD:main` normal only, then fetch, HEAD==origin/main, 0/0, tracked clean and 3,220 owner+task untracked unchanged. Return exact source/HEAD SHAs and full GitHub log link.

GPT will independently audit P02, and record SOURCE PASS or further PARTIAL. Neither source-pass nor native classification read-only probe establishes real NTFS app-path protection or race-free native handles. True AI creator/approver authority and R05 genuine gameplay/Factory Studio production are separate OPEN work.
