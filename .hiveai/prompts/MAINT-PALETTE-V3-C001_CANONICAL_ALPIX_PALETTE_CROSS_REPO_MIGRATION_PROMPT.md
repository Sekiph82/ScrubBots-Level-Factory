# MAINT-PALETTE-V3-C001 — Canonical Alpix Palette Cross-Repository Migration

Repository scope:
- https://github.com/Sekiph82/ScrubBots-Level-Factory
- https://github.com/Sekiph82/Scrubbots

Authority:
`Sekiph82/Scrubbots/data/palettes/scrubbots_palette_v3.json`.

Update every LIVE palette-dependent code/data/config/test/doc/UI/fixture/reference in both repos to canonical Palette V3. Preserve C01..C16 IDs and BG01; use the exact V3 Alpix HEX/RGB mapping. Level Factory must stop loading/enforcing Palette V2 and its retired per-difficulty color-count bands; adopt V3 schema/version, `usedColorEnvelopeV1=3..12`, and `difficultyClassDerivedFromColorCount=false`.

Do an exhaustive repository search for stale V2 paths/schema/version, old HEX/RGB values, hard-coded palettes, old difficultyColorCountBands, expected fixtures and generated/UI palette tables. Update all live occurrences consistently. Keep intentionally historical audit/log/legacy snapshot evidence and the superseded V2 palette file only when clearly marked historical; do not rewrite history.

Run all focused palette/semantic/M05/M06 tests plus full pytest, compileall, Godot headless checks, and relevant main-game tests. Prove no live code path still depends on V2 or old colors. Commit/push both repos and report exact SHAs plus changed-file lists.
