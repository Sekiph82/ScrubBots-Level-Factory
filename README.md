# SCRUBBOTS Content Production Platform

`Sekiph82/ScrubBots-Level-Factory` is the canonical development-time platform that creates, validates, sequences, packages and publishes declarative content for the SCRUBBOTS mobile game.

It now unifies three related development surfaces:

1. **Level Factory / Art Intelligence** — semantic + procedural level artwork, deterministic logical compilation, provenance and batch production.
2. **Puzzle / Campaign Intelligence** — simulation, solver, Difficulty V1 analysis, QA and campaign sequencing.
3. **Content Publishing / Update Platform** — `.scrubpack`, manifests, staging/production promotion, storage adapters, rollback/disable/scheduling and release evidence.

The shipping game remains in `Sekiph82/Scrubbots` and never imports Factory/Publisher implementation code.

## Canonical program tracker

Root `TASKS.md` is the canonical live tracker for the 224 Content Platform tasks:

- 112 `SB-LF00-* .. SB-LF10-*` Level Factory / Campaign tasks.
- 112 `SB-CP00-* .. SB-CP09-*` Content / Update Platform tasks.

Some CP tasks, especially `CP04` and `CP05`, are tracked here but implemented in the main Godot game repository because they are shipping-runtime responsibilities.

ChatGPT owns task acceptance and tracker updates. Codex/Claude implement and test but do not self-close task rows.

## Architecture authority

Read in this order:

- `coordination/OWNER_CONTENT_PLATFORM_CONSOLIDATION_DECISION_V01.md`
- `TASKS.md`
- `docs/CONTENT_PLATFORM_ARCHITECTURE_V01.md`
- `docs/CROSS_REPO_CONTRACT_V01.md`
- `docs/CONTENT_PLATFORM_MIGRATION_MATRIX_V01.md`
- `docs/STUDIO_INTEGRATION_PLAN_V01.md`
- `GOVERNANCE.md`

Current owner-locked game contracts in `Sekiph82/Scrubbots` outrank stale historical Factory assumptions.

## Current core

The existing Python package remains valuable and is retained rather than rewritten. It already contains substantial audited foundations for:

- deterministic generation requests and RNG;
- seed/reproduce/batch workflows;
- MASK / RULES / WFC / HYBRID / AUTO generation;
- quality/diversity analysis;
- deterministic logical export/provenance;
- CLI batch/resume/reproduce;
- semantic generation contracts;
- Magnific and PixelLab provider bridges;
- deterministic semantic normalization;
- qualification/review evidence.

Historical PAG M00-M10 and PAG-SP work remains evidence. It is mapped to the new 224-task program through strict migration audit rather than silently relabeled as completion.

## Difficulty V1 convergence

The main game has superseded the old player-facing assumptions that difficulty class is determined by board dimensions or class-specific color-count bands.

Current platform target:

- board engine/content envelope remains 20..59 per dimension, rectangular supported;
- board size contributes to workload/session load rather than defining difficulty class;
- production logical art uses canonical C01..C16;
- current general production used-color envelope is 3..12;
- Challenge, Session Load and Frustration Risk are separate;
- campaign sequencing follows the owner-locked repeating cadence and retention system.

Legacy validators/contracts are migrated through audited work, not edited silently.

## LEVEL_ART semantic direction

The owner-approved high-resolution LEVEL_ART direction remains:

```text
SEMANTIC IMAGE
  -> CELL_MAJORITY
  -> PALETTE SNAP
  -> ONE LOGICAL PIXEL = ONE GAMEPLAY CELL
  -> C01..C16
  -> CURRENT DIFFICULTY / QA EVALUATION
  -> VALIDATION / EXPORT
```

`AREA_AVERAGE_V1` remains historical evidence only for prior qualification and is not the canonical LEVEL_ART reduction policy.

## Factory Studio

The owner-supplied Windows `ScrubBots Level Factory v1.3.6` application is treated as a Studio/operator-console source candidate.

Target dependency direction:

```text
Studio UI -> canonical Factory Core -> one canonical compiler/validator/exporter
```

The Studio may own provider orchestration, batch/resume, previews, review and operator UX. It must not remain an independent second compiler with duplicated difficulty/palette rules.

See `docs/STUDIO_INTEGRATION_PLAN_V01.md`.

## Content publishing boundary

Factory output ultimately flows through:

```text
Accepted LevelData / Campaign
 -> .scrubpack
 -> versioned remote manifest
 -> STAGING
 -> remote verification
 -> explicit PRODUCTION promotion
 -> storage/CDN
 -> ScrubBots Godot runtime
```

Remote packages are declarative only. No executable scripts, native libraries, plugins or publishing credentials may ship as content.

The game downloads verified content under `user://`, preserves last-known-good content and remains playable offline where cached/builtin content exists.

## Development setup

The current Python core targets Python 3.12 according to `pyproject.toml`.

Typical local setup:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\test.ps1
```

Direct equivalent:

```powershell
python -m pip install -e ".[test]"
python -m pytest
```

Do not commit virtual environments, build trees, generated installer output, caches, provider credentials or publisher credentials.

## Historical PAG CLI

Existing local generator CLI remains available during migration:

```powershell
python -m scrubbots_pixel_factory.cli
```

Its `generate`, `reproduce` and `batch` foundations are retained and progressively adapted to the canonical Content Platform contracts.

## Governance

GitHub `main` is repository truth. Root `TASKS.md` is the current 224-task Content Platform ledger. Historical `.hiveai` prompts/logs/audits remain immutable evidence, not a competing current tracker.

A builder's passing tests are evidence, not independent acceptance. ChatGPT performs final audits and tracker closure.
