# Owner Decision — Transparent Artwork -> VOID Cells in Level Factory V01

Status: OWNER-APPROVED / IMPLEMENTATION BLOCKED BY GAME VOID CAPABILITY  
Date: 2026-10-08  
Repository: `Sekiph82/ScrubBots-Level-Factory`  
Depends on: `Sekiph82/Scrubbots` main-game VOID ADR and LevelData V2 support.

## Owner decision

Transparent artwork pixels are VOID cells once the main game supports VOID.

They are never filled with a colour, never become supply demand, and never silently mutate the artwork.

Full-canvas opaque artwork must behave exactly as before.

## Current gate

As of this decision, `Sekiph82/Scrubbots:main` still reports:

`LevelData.FORMAT_VERSION := 1`

and its current Level Data spec defines only fully coloured source cells.

Therefore LF implementation must remain **BLOCKED_BY_GAME_VOID_MERGE** until current game `main` contains the owner-approved VOID contract.

## Capability gate

The LF implementation must resolve a configured clean current-game authority and positively prove the new VOID capability from current `Sekiph82/Scrubbots` main, including the authoritative ADR/spec.

At minimum, the game authority must define the new LevelData format with `-1` cell semantics or an equivalent exact owner-approved constant/contract.

If the gate is absent:

- transparent artwork remains unavailable for production;
- reason is explicit;
- no fill fallback;
- no partial LevelData/supply output;
- opaque full-canvas behavior remains unchanged.

## Contract inheritance

Level Factory does not independently redefine game VOID gameplay semantics.

When the gate opens, LF must read and follow the game ADR for:

- VOID presentation;
- minimum non-VOID artwork rule;
- board/reachability semantics;
- win semantics;
- Difficulty V1 VOID behavior;
- schema/version details.

This avoids duplicated or drifting D1/D2 decisions.

## LF end-to-end target

Once the game gate opens:

- binary alpha only: 0 or 255;
- semi-alpha rejected;
- alpha 0 becomes VOID;
- non-VOID colors must remain canonical;
- 3..12 used-color count ignores VOID;
- artwork/minimum-cell legality uses the game ADR;
- supply conservation ignores VOID;
- solver bridge constructs real game-supported VOID LevelData rather than colour-0 plus manual cleared state;
- official game solver/replay and Difficulty V1 remain authoritative;
- exporter emits the game-supported LevelData version and `-1` VOID cells;
- metadata records both artwork/non-VOID and VOID counts;
- hashes/identity include VOID layout;
- Factory Studio preview displays VOID exactly as the current game contract specifies;
- release/campaign logic uses official resulting score without a separate VOID difficulty hack.

## Required owner-real fixture

A real 32x32 owner/Claude-drawn sprite with approximately 550 transparent pixels must reach READY with supply columns 3, 4 and 5 when all normal production gates pass.

## Regression invariant

Opaque full-canvas artwork must preserve the pre-VOID output/hashes/behavior where the format remains V1-compatible.

No V2/VOID feature may rewrite legacy opaque content merely because the capability exists.
