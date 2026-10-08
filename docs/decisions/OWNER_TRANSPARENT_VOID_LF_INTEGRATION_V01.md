# Owner Decision — Transparent Artwork -> VOID Cells in Level Factory V01

Status: OWNER-APPROVED / GAME VOID CAPABILITY MERGED + AUDITED / LF IMPLEMENTATION PASS-CLOSED  
Date: 2026-10-08  
Repository: `Sekiph82/ScrubBots-Level-Factory`  
Depends on: `Sekiph82/Scrubbots` main-game VOID ADR and LevelData V2 support.

## Owner decision

Transparent artwork pixels are VOID cells once the main game supports VOID.

They are never filled with a colour, never become supply demand, and never silently mutate the artwork.

Full-canvas opaque artwork must behave exactly as before.

## Current gate

**OPEN as of 2026-10-08.**

Main-game implementation authority:

`Sekiph82/Scrubbots@7d0d148b8609ec04852fdee02f6b8ef37598c616`

Independent game audit:

`coordination/sessions/VOID-CELLS-C001/CHATGPT_STRICT_AUDIT_V01.md`

Game contract now defines:

- legacy opaque levels: `LevelData.FORMAT_VERSION := 1`;
- VOID levels: `LevelData.FORMAT_VERSION_VOID := 2`;
- VOID encoding: `LevelData.VOID_CELL := -1`;
- D1: VOID renders exactly like CLEARED/BG01;
- D2: production >= 200 non-VOID cells and >= 25% W*H.

The LF task must still resolve exact current `Sekiph82/Scrubbots:main` at execution time and prove that the audited VOID authority remains an ancestor/current contract.

## Capability gate

The LF implementation must resolve a configured clean current-game authority and positively prove the new VOID capability from current `Sekiph82/Scrubbots` main, including the authoritative ADR/spec.

At minimum, the game authority must define the new LevelData format with `-1` cell semantics or an equivalent exact owner-approved constant/contract.

If a future current-game authority no longer contains or is incompatible with the audited VOID contract:

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

## Owner-real fixture acceptance

Canonical owner-supplied fixture:

`tests/fixtures/owner_void/017_a_single_brown_owl_centered_simple_clear_32px.png`

Accepted immutable facts:

- 32x32;
- 354 transparent/VOID cells;
- 670 artwork cells;
- 0 semi-alpha cells;
- 7 opaque RGB colors;
- SHA-256 `9f3cff525745cd0623997cb0c2d99084e3c2ddb110457042ebdefe58cdcb7214`.

This exact fixture reached READY with supply columns 3, 4 and 5, with official current-game loader/validator/supply checks, solver SOLVED, replay WIN and Difficulty V1.

The earlier approximately-550-transparent example is superseded by this owner-selected fixture.

## Regression invariant

Opaque full-canvas artwork must preserve the pre-VOID output/hashes/behavior where the format remains V1-compatible.

No V2/VOID feature may rewrite legacy opaque content merely because the capability exists.


## Level Factory closure

SB-LFX-019-C001-R01 is independently PASS/CLOSED by:

`.hiveai/audits/SB-LFX-019-C001-R01_STRICT_REAUDIT_V01.md`

No R02 is required.
