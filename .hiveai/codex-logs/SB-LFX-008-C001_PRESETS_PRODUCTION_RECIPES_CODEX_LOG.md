# SB-LFX-008-C001 — Factory Studio Presets / Production Recipes

Document role: CODEX BUILDER LOG

Starting timestamp: 2026-09-20T17:05:00+03:00
Canonical repository: `Sekiph82/ScrubBots-Level-Factory`
Branch: `main`
Starting HEAD: `5987ec84eaabf2ae7440c25bef6d40f2c048a7f0`
Origin state: local `main` equaled `origin/main` before task edits.
Initial status: preserved ten pre-existing untracked Godot `.uid` files only.

## Scope and required reads

Implement only SB-LFX-008 C001. Read root `TASKS.md`, owner-operations spec, SB-LFX-008 prompt/criteria, current Generate/Import Validation/Pipeline request contracts, and prior implementation logs. Root `TASKS.md` is read-only.

## Chronology

- Created this log before product or test edits.
- Implementation and verification follow.

## Implementation

- Added versioned preset records with bounded names/settings, supported operation kinds, deterministic serialization, and unsupported secret/truth-field rejection.
- Added expanded canonical request resolution so execution data contains resolved controls rather than relying on a preset ID.
- Added the real Presets Studio surface for save/update and expanded-request application.

## Verification

- Focused Python: `PYTHONPATH=src python -m pytest -q tests/unit/test_sb_lfx_008_presets.py tests/unit/test_sb_lfx_007_comparison.py` — **3 passed, 1 warning**.
- Godot headless Studio boot — **PASS**.
- `git diff --check` — **PASS**; `git diff -- TASKS.md` — **empty**.

## Changed files

`src/scrubbots_pixel_factory/studio_extensions.py`, `level_factory/scripts/factory_core_launcher.py`, `level_factory/scripts/factory_studio_presets.gd`, `level_factory/scripts/factory_studio_workspace_page.gd`, `level_factory/scripts/factory_studio_navigation.gd`, `tests/unit/test_sb_lfx_008_presets.py`, and this builder log.

## Publication

- Final implementation SHA: pending commit.
- Push/equality checkpoint and final log-only SHA are pending.

## Verification and publication

Pending.
