# SCRUBBOTS Factory Studio Integration Plan V01

Status: CANONICAL MIGRATION PLAN
Date: 2026-09-14
Source candidate: owner-supplied `ScrubBots Level Factory v1.3.6`

## Goal

The existing Windows application becomes the operator-facing **Factory Studio** for the canonical Content Production Platform.

It must not remain an independent second compiler/validator whose rules can drift from Factory Core.

Target:

```text
Studio UI / provider orchestration / batch controls
                    |
                    v
          canonical Factory Core APIs
                    |
                    v
       one compiler / one validator / one exporter
```

## Source archive inventory

The owner-supplied ZIP contains approximately 9,498 entries, the overwhelming majority belonging to build/virtual-environment output.

After excluding `.buildvenv`, `app_build`, `setup_build`, `app_dist`, `setup_dist` and `__pycache__`, the useful source/operator surface is small and includes:

- `app.py`;
- `requirements.txt`;
- `setup_installer.py`;
- `build_windows_setup.ps1`;
- `BUILD_AND_INSTALL.bat`;
- `RUN_SOURCE_DIAGNOSTIC.bat`;
- application/setup spec files;
- palette/template CSV/JSON assets;
- source diagnostics/static-check evidence;
- changelogs and Turkish README;
- icon/logo source assets.

Generated setup EXEs are release artifacts, not source authority.

## Capabilities to preserve

The Studio candidate contains useful operator capabilities that should be retained where they do not violate newer contracts:

- Magnific workflow/OAuth orchestration;
- PixelLab provider operation;
- Windows credential handling;
- CSV batch execution;
- interrupted-generation resume;
- progress state persistence;
- ORIGINAL vs FINAL result separation;
- provider credit/usage presentation;
- local validation feedback;
- Windows packaging/install ergonomics.

## Capabilities to replace with Factory Core

The Studio must not retain independent truth for:

- LevelData compilation;
- logical-cell reduction;
- palette legality;
- difficulty semantics;
- used-color legality;
- solver/solvability;
- QA acceptance;
- campaign sequencing;
- `.scrubpack` serialization;
- remote manifest truth.

Studio code calls canonical APIs instead.

## Known legacy conflicts to remove

1. Square-board-only assumptions.
2. Old class=dimension mapping.
3. Old class-specific used-color bands.
4. Area-average/block averaging where canonical LEVEL_ART requires CELL_MAJORITY.
5. Any behavior that invents/remaps cells simply to manufacture a minimum class color count.
6. Any local palette/config copy that can silently diverge from canonical platform contracts.

## Target source layout

```text
studio/
  README.md
  src/
    app.py or modular successor
    adapters/
    views/
    controllers/
  assets/
  packaging/
  tests/
```

The first source-import cycle should preserve the original v1.3.6 code under a clearly marked migration namespace or Git tag/commit, then refactor incrementally. Do not erase behavior before replacement tests exist.

## Dependency direction

Allowed:

```text
studio -> scrubbots_factory core
```

Forbidden:

```text
scrubbots_factory core -> studio GUI
```

Core remains headless-testable and usable from CLI/automation without opening the Studio.

## Security

- Never commit provider secrets, OAuth refresh tokens, API keys or DPAPI-protected user blobs.
- Credential storage remains user-local.
- Publishing credentials are separate from art-provider credentials.
- Studio logs must redact credentials and transient signed URLs where appropriate.

## Migration phases

### STUDIO-MIG-01 Source extraction

- import only real source/operator assets;
- exclude build/runtime bulk;
- capture source-file hashes and provenance;
- add smoke/static tests.

### STUDIO-MIG-02 Core adapter

- define application-service API over Factory Core;
- move palette/dimension/normalization/export truth out of UI code;
- retain old implementation only behind temporary migration tests.

### STUDIO-MIG-03 Difficulty V1

- remove class=dimension and class=color legality from Studio;
- expose Challenge/Load/Risk results from canonical evaluator.

### STUDIO-MIG-04 Solver/QA

- add Solve / Analyze / Validate / Reproduce commands to Studio using canonical core.

### STUDIO-MIG-05 Campaign and publishing

- owner-review queue;
- CampaignBuilder views;
- pack/manifest preview;
- staging publish controls;
- production promotion confirmation;
- rollback/disable/scheduling controls.

## Completion rule

LF06 is not complete merely because a GUI exists. It closes only when the Studio is a thin, tested operator layer over canonical core truth and can reproduce/validate the same candidate bytes and metadata as headless tooling.
