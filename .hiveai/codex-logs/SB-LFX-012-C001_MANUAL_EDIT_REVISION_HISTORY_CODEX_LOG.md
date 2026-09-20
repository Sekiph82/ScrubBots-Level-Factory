# SB-LFX-012-C001 — Factory Studio Manual-Edit Revision History

Document role: CODEX BUILDER LOG

Starting timestamp: 2026-09-20T18:25:00+03:00
Canonical repository: `Sekiph82/ScrubBots-Level-Factory`
Branch: `main`
Starting HEAD: `0da0d10bef76909ddd3cf0b0f544d7aae29e7b9d`
Origin state: local `main` equaled `origin/main` before task edits.
Initial status: preserved ten pre-existing untracked Godot `.uid` files only.

## Scope and required reads

Implement only SB-LFX-012 C001. Root `TASKS.md` is read-only. Read product contract, SB-LFX-012 prompt/criteria, accepted manual editor/revalidation contracts, and prior logs.

## Chronology

- Created this log before product or test edits.
- Implementation and verification follow.

## Implementation

- Added durable versioned immutable revision records bound to candidate/artwork identity, exact logical grid hash, parent lineage, sequence, and stale validation state. Added listing/loading and changed-cell comparison; branching after undo preserves later revisions.
- Added the real Revisions Studio surface and navigation entry with explicit immutable-lineage wording.
- Focused coverage proves baseline/branch lineage, comparison, reloadable revision records, and source-bundle preservation.

## Verification

- Focused Python: `PYTHONPATH=src python -m pytest -q tests/unit/test_sb_lfx_012_revisions.py tests/unit/test_sb_lfx_011_reproduce.py` — **2 passed, 1 warning**.
- Godot headless Studio boot — **PASS**.
- `git diff --check` — **PASS**; `git diff -- TASKS.md` — **empty**.

## Changed files

`src/scrubbots_pixel_factory/studio_extensions.py`, `src/scrubbots_pixel_factory/__init__.py`, `level_factory/scripts/factory_studio_revisions.gd`, `level_factory/scripts/factory_studio_workspace_page.gd`, `level_factory/scripts/factory_studio_navigation.gd`, `tests/unit/test_sb_lfx_012_revisions.py`, and this builder log.

## Publication

- Final implementation SHA: `de71e73a7b65991f66731e7b3f734ff0d8905ff8`.
- Push/equality checkpoint and final log-only SHA are pending.

## Verification and publication

Pending.
