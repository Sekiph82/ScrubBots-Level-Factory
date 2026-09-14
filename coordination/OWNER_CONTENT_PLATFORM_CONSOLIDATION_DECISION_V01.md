# OWNER CONTENT PLATFORM CONSOLIDATION DECISION V01

Status: **OWNER-LOCKED**
Date: 2026-09-14
Owner: Şekip

## Decision

`Sekiph82/ScrubBots-Level-Factory` is promoted from a standalone pixel-art/semantic generator project into the canonical **SCRUBBOTS Content Production Platform** repository.

The platform owns program tracking, planning and implementation for the 224 sidecar tasks originally defined in `Sekiph82/Scrubbots` as:

- `SB-LF00-*` through `SB-LF10-*`: 112 Level Factory / Campaign Intelligence tasks.
- `SB-CP00-*` through `SB-CP09-*`: 112 Content Packaging / Publishing / Update Platform tasks.

The mobile-game repository remains the canonical gameplay/client-runtime repository.

## Product split

### `Sekiph82/ScrubBots-Level-Factory`
Owns:

- semantic and procedural level-art generation;
- deterministic compilation and provenance;
- puzzle simulation and solver tooling;
- Difficulty V1 metrics and acceptance intelligence;
- QA, review and campaign sequencing;
- Factory Studio/operator UI;
- `.scrubpack` packaging;
- remote manifest generation;
- staging/production publisher control plane;
- storage/CDN adapters;
- rollback, disable and scheduling control plane;
- content operations and release evidence.

### `Sekiph82/Scrubbots`
Owns:

- the shipping Godot game;
- gameplay systems and presentation;
- runtime LevelData/catalog consumption;
- runtime `RemoteContentManager` implementation;
- HTTPS download and integrity verification;
- `user://` content registry/cache;
- last-known-good activation and offline fallback;
- store-facing application permissions and runtime compatibility.

## Tracker authority

The canonical live tracker for the 224 LF/CP tasks is now:

`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/TASKS.md`

The corresponding LF/CP rows retained in the main-game repository are a historical/shadow roadmap only and must not be independently advanced. Cross-repo runtime tasks remain tracked in the Content Platform tracker but declare `implementation_repo: Sekiph82/Scrubbots`.

The main game keeps its own gameplay/UI tracker and progress denominator. Program-level reporting must show three values separately:

1. Game/client progress.
2. Content Platform progress out of 224.
3. Combined SCRUBBOTS program progress.

Moving tracker ownership does not itself count as task completion.

## Contract precedence

For gameplay, LevelData, palette, Difficulty V1, campaign and runtime semantics, current owner-locked contracts in `Sekiph82/Scrubbots` outrank stale legacy rules in this repository.

In particular:

- board dimensions are an engine/content envelope, not difficulty class identity;
- production artwork uses canonical C01..C16 and current Difficulty V1 3..12 used-color envelope unless a newer audited rule narrows a content family;
- old `EASY 20..29 / MEDIUM 30..39 / HARD 40..49 / VERY_HARD 50..59` and old class-specific used-color bands are historical compatibility rules, not current player-facing difficulty truth;
- rectangular boards remain legal;
- Challenge, Session Load and Frustration Risk remain separate axes;
- CampaignBuilder sequences accepted levels but does not mutate accepted logical cell data.

## Existing repository evidence

Existing accepted PAG M00-M10 and PAG-SP evidence is preserved. It is not discarded and is not automatically relabeled as completion of new `SB-LF*` / `SB-CP*` tasks. A migration/evidence audit maps existing proofs onto the new canonical task IDs before new checkboxes close.

## Factory Studio

The owner-supplied `ScrubBots Level Factory v1.3.6` Windows application becomes a **Studio/operator-console source candidate**, not an independent second compiler.

The target rule is:

`Studio UI -> canonical Factory Core -> one canonical output contract`.

Build environments, installer output and generated EXEs are not source authority and are not imported as canonical code.

## Remote-content safety

Remote content is declarative only. No remote scripts, native libraries, executable expressions, plugins or arbitrary code are permitted in content packages.

Publishing is always versioned, integrity-checked, staging-first, reversible and auditable.

## Parallel development

Codex may advance Content Platform work in `ScrubBots-Level-Factory` while Claude advances game work in `Scrubbots`, provided each prompt states its repository and cross-repo write boundary explicitly.

No agent may opportunistically modify the other repository outside a prompt-authorized cross-repo task.
