# SB-LFX-009-C001 — Factory Studio Search / Filter / Smart Collections

Document role: CODEX BUILDER LOG

Starting timestamp: 2026-09-20T17:25:00+03:00
Canonical repository: `Sekiph82/ScrubBots-Level-Factory`
Branch: `main`
Starting HEAD: `71705420e697cb9f9a08fe6275a37860071cc0a2`
Origin state: local `main` equaled `origin/main` before task edits.
Initial status: preserved ten pre-existing untracked Godot `.uid` files only.

## Scope and required reads

Implement only SB-LFX-009 C001. Read root `TASKS.md`, product contract, SB-LFX-009 prompt/criteria, Library/Candidate/Review readers, and prior implementation logs. Root `TASKS.md` is read-only.

## Chronology

- Created this log before product or test edits.
- Implementation and verification follow.

## Implementation

- Added `discover_records` as a fresh deterministic derived query over verified Library sources, canonical candidates, and append-only review evidence. Grounded collections include Needs Review, Owner Accepted/Rejected, and Imported Sources; unsupported readiness/campaign collections return NOT AVAILABLE.
- Added the real Search surface with text query and bounded smart-collection selector. No membership list or duplicate truth store is persisted.
- Corrected an initial Godot one-line loop scoping error in the OptionButton construction; headless boot is now clean.

## Verification

- Focused Python: `PYTHONPATH=src python -m pytest -q tests/unit/test_sb_lfx_009_discovery.py tests/unit/test_sb_lfx_008_presets.py` — **3 passed, 1 warning**.
- Godot headless Studio boot — **PASS** after the focused UI correction.
- `git diff --check` — **PASS**; `git diff -- TASKS.md` — **empty**.

## Changed files

`src/scrubbots_pixel_factory/studio_extensions.py`, `src/scrubbots_pixel_factory/__init__.py`, `level_factory/scripts/factory_core_launcher.py`, `level_factory/scripts/factory_studio_search.gd`, `level_factory/scripts/factory_studio_workspace_page.gd`, `level_factory/scripts/factory_studio_navigation.gd`, `tests/unit/test_sb_lfx_009_discovery.py`, and this builder log.

## Publication

- Final implementation SHA: pending commit.
- Push/equality checkpoint and final log-only SHA are pending.

## Verification and publication

Pending.
