# MAINT-PALETTE-V3-C001 — Independent Strict Audit
Document role: INDEPENDENT CHATGPT CROSS-REPOSITORY MAINTENANCE AUDIT

## Result
PASS / CLOSED

`MAINT-PALETTE-V3-001` is accepted across:
- `Sekiph82/ScrubBots-Level-Factory@c99142468987378ee8d03a4807a87275cdcb604e`
- `Sekiph82/Scrubbots@edf672f61989d28fd1931917ab49b2d64cc416d6`

## Authority and mirror
Canonical authority:
`Sekiph82/Scrubbots/data/palettes/scrubbots_palette_v3.json`

Level Factory mirror:
`data/palette/scrubbots_palette_v3.json`

Both current files have identical Git blob SHA:
`51ff3cc14441731b39baff283c4289910dc4f256`.

The authority/mirror preserves exact C01..C16 IDs, the Alpix-aligned V3 HEX/RGB mapping, BG01 `#202533`, global used-color envelope 3..12, and `difficultyClassDerivedFromColorCount=false`.

## Live contract checks
- Level Factory `contracts/palette.py` loads only `scrubbots_palette_v3.json`, requires schema `scrubbots-global-palette/v3`, version 3, owner lock, exact 3..12 envelope, and difficulty-independent color legality.
- Scrubbots `scripts/tools/production_art_level_builder.gd` uses `res://data/palettes/scrubbots_palette_v3.json`, validates V3 schema/version/owner lock, exact C01..C16 structure and HEX/RGB consistency, BG01, 3..12 envelope, and rejects deriving difficulty class from color count.
- Dedicated Scrubbots `tests/palette_v3_leveldata_contract.gd` proves Palette V3 remains separate from Level Data format version 1 and preserves V2 only as historical provenance.
- No active repository search result remained for the old V2 palette path/schema, old C01 `#E94B4B`, or `difficultyColorCountBands`. Explicit historical/provenance references are allowed by the maintenance contract.

## Builder verification accepted as supporting evidence
Level Factory:
- focused pytest: `146 passed`
- full pytest: `985 passed, 2 skipped`
- compileall: PASS
- all 23 Level Factory Godot suites: PASS

Scrubbots:
- dedicated Palette V3 contract: PASS
- aggregate Godot suite: `5322 checks, 0 failures`
- relevant M35-M38/M27-M28 headless scripts: PASS

The two Level Factory skips are retained pre-existing canonical-checkout capability skips and were not introduced to hide Palette V3 failures.

## Publication / preservation
- Level Factory implementation commit: `e1cd2ad7eed0c06eaa0fb8aa89d3d607317eaf21`
- Level Factory final publication SHA: `c99142468987378ee8d03a4807a87275cdcb604e`
- Scrubbots implementation commit: `89eb552de3ca2db2ab64e9465e32f3bb5b2cd357`
- Scrubbots final publication SHA: `edf672f61989d28fd1931917ab49b2d64cc416d6`

Builder logs document that protected tracker/audit/history, owner work, and pre-existing untracked files were preserved. Scrubbots incorporated concurrent owner/audit/tracker changes by non-destructive merge rather than reset/rebase/force-push.

## Final disposition
The canonical Palette V3 cross-repository migration is complete and verified. No remediation round is required.
