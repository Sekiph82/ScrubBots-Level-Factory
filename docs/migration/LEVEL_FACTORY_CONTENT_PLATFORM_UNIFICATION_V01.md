# Level Factory + Content Platform Unification V01

## Decision

`Sekiph82/ScrubBots-Level-Factory` is the canonical task/governance repository for the SCRUBBOTS Level Factory + Content Platform program.

`Sekiph82/Scrubbots` remains the canonical mobile game/runtime repository.

This is a tracker/ownership consolidation, not a claim that unfinished LF/CP capabilities are complete.

## Canonical requirement model

- 112 Level Factory source requirements retain IDs `SB-LF00-001..SB-LF10-008`.
- 112 Content Pipeline source requirements retain IDs `SB-CP00-001..SB-CP09-010`.
- Total canonical LF/CP source requirements: 224.
- Accepted PAG/SP implementation becomes evidence attached to these requirements and is not counted as a second live task family.
- `PAG-SP11`, `PAG-SP12`, `PAG-SP13` remain three live extension tasks because their complete capabilities are not represented by the 224 LF/CP source requirements.
- `PAG-SP14` remains an integration/closure alias, not an additional denominator task.

## Repository boundary

### Factory repository owns

- deterministic Factory Core;
- semantic provider adapters and qualification;
- trusted LEVEL_ART compilation;
- semantic/readability QA;
- puzzle simulation/solver tooling;
- Difficulty Intelligence;
- mutation/evolution tooling;
- Factory Studio;
- batch production;
- Campaign Intelligence;
- `.scrubpack` tooling;
- remote manifest tooling;
- staging/production publisher control plane;
- storage/CDN adapters;
- content operations/security/release tooling.

### Game repository owns

- Godot runtime `RemoteContentManager`;
- HTTPS manifest/runtime download behavior;
- `user://` content storage and cache;
- app-side integrity and compatibility validation;
- last-known-good and offline boot;
- runtime activation, disable and rollback behavior;
- runtime LevelCatalog/loader integration.

The runtime subset remains visible in the Factory tracker as `[GAME_RUNTIME]` requirements, but implementation and independent runtime evidence live in `Sekiph82/Scrubbots`.

## Runtime subset

- `SB-CP04-001..014`
- `SB-CP05-001..012`
- `SB-CP06-004`
- `SB-CP06-010`

Total: 28 requirements.

## Windows Factory Studio v1.3.6

The existing Windows application is migration source material for unified M06 Factory Studio.

Reuse/refactor:

- operator GUI/workflow;
- CSV batch orchestration;
- Magnific/PixelLab orchestration;
- OAuth/session handling;
- Windows DPAPI credential storage;
- SQLite durable job state;
- interrupted-job resume and creation-ID recovery;
- duplicate paid-generation prevention;
- ORIGINAL artifact preservation;
- prompt-change invalidation;
- provider credit accounting.

Replace rather than preserve as canonical truth:

- block-average logical reduction;
- class-specific used-color legality;
- difficulty derived from used-color count;
- forced foreground color injection;
- square-only production assumptions;
- arbitrary 1..256 production-size semantics.

Factory Studio must call canonical Factory Core. There is one compiler truth.

## Locked production truth preserved

- width 20..59;
- height 20..59 independently;
- rectangles legal;
- one logical artwork pixel = one gameplay cell;
- C01..C16 logical palette;
- BG01 presentation only;
- 3..12 used colors independent of difficulty lane;
- Difficulty V1 is not board size or color count;
- `CELL_MAJORITY_V1`;
- `PALETTE_SNAP_V1`;
- no random/forced color injection solely to force legality;
- exact deterministic provenance;
- SP06 structural diagnostics never mint recognizability acceptance;
- only explicit semantic-review ACCEPT passes the accepted gate.

## Cutover evidence

- Immediate pre-cutover Factory HEAD: `3e2ce159df77c796b723a4387d5ce40e00b3ff50`
- Immediate pre-cutover Factory `TASKS.md` blob: `97f704c140fc61d866250fc8116d2964849a20dc`
- Unified Factory tracker cutover commit: `edfe40b67a2496c206b1c30394aa2b0b9c8e1566`
- Unified Factory tracker blob: `d8cfdadc07aa3ad14596c4e6d139b17b88472cca`

SP07-C001 had already reached strict audit before cutover. The unified tracker therefore preserves `CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED` and keeps `PAG-SP07-C001-R01` as the active remediation cycle under `SB-LF09-003`.

## Main-game tracker consequence

After this Factory tracker is verified, the duplicate 224 LF/CP checklist rows in `Sekiph82/Scrubbots/TASKS.md` are migrated to a non-checklist reference section and removed from that repository's live task denominator. This does not represent new game implementation progress. It separates game completion from Factory/Content Platform completion.
