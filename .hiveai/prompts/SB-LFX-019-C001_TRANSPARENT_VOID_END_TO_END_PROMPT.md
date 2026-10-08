# SB-LFX-019-C001 — Transparent Artwork -> VOID End-to-End

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
`https://github.com/Sekiph82/ScrubBots-Level-Factory`

Owner decision:
`docs/decisions/OWNER_TRANSPARENT_VOID_LF_INTEGRATION_V01.md`

Audit criteria:
`.hiveai/audit-criteria/SB-LFX-019-C001_TRANSPARENT_VOID_END_TO_END_AUDIT_CRITERIA.md`

Standing sync/publish:
`docs/process/CODEX_SYNC_PUBLISH_STANDARD_V01.md`

## HARD EXECUTION GATE

The game dependency is now merged and independently closed:

- game implementation: `Sekiph82/Scrubbots@7d0d148b8609ec04852fdee02f6b8ef37598c616`;
- game audit: `https://github.com/Sekiph82/Scrubbots/blob/main/coordination/sessions/VOID-CELLS-C001/CHATGPT_STRICT_AUDIT_V01.md`.

Run only when root LF `TASKS.md` makes `SB-LFX-019-C001` Current Task.

At task start:

1. resolve exact current `Sekiph82/Scrubbots:main` in a clean configured authority;
2. require audited commit `7d0d148b8609ec04852fdee02f6b8ef37598c616` to be an ancestor of that current game authority;
3. read ADR-030 and current Level Data spec first;
4. positively prove `FORMAT_VERSION_VOID == 2`, `VOID_CELL == -1`, D1 and D2 from the current game code/docs;
5. if the audited contract is absent/incompatible, stop fail-closed.

Do not fill transparency. Do not partially emit production artifacts.

## FIRST OPERATION — standing safe sync

Apply `docs/process/CODEX_SYNC_PUBLISH_STANDARD_V01.md`.

Use exact current LF `origin/main`; preserve owner Desktop work. Use task TEMP authority if needed:

`%TEMP%\ScrubBots-Level-Factory\SB-LFX-019-C001`

Never edit root `TASKS.md` or `.hiveai/audits/**`.

Builder log:

`.hiveai/codex-logs/SB-LFX-019-C001_TRANSPARENT_VOID_END_TO_END_CODEX_LOG.md`

## OWNER DECISION

Transparent pixels are VOID once the game capability exists.

They are not colors, not supply demand, and must never be filled.

Opaque full-canvas artwork must keep today's behavior.

## 1. Import / Artwork QA

Cover owner upload, Import Validation Wizard, batch import and art-producer handoff.

Requirements:

- alpha must be binary 0/255;
- semi-alpha rejected;
- alpha 0 -> VOID;
- alpha 255 -> canonical artwork color;
- used-color count 3..12 counts non-VOID only;
- apply the exact minimum-artwork rule from the game ADR;
- source PNG remains byte-identical;
- capability gate closed -> transparent input UNAVAILABLE with explicit reason and zero partial production output.

## 2. Pixel analyzer / screening

Use existing `-1` internal VOID modeling where present.

- playable/artwork metrics count non-VOID only as required by the game contract;
- VOID initial openness/reachability mirrors current game kernel exactly;
- add step-exact parity fixtures against game behavior;
- no LF-specific shortcut/teleport semantics.

## 3. Godot solver bridge

Remove any transparent->colour-0 plus manual CLEARED workaround.

Build the real game-supported LevelData representation with VOID `-1` according to the merged game V2 contract.

Let game code create the initial solver state.

Run official `LevelDifficultyAnalyzerV1` for VOID levels. Remove full-canvas-only guards only behind the positive capability gate.

## 4. Supply optimizer / primary acceptance

Acceptance remains unchanged in authority:

- game SOLVED;
- replay WIN;
- official Difficulty V1;
- normal QA/readiness gates.

Supply columns remain 3, 4 or 5.

Supply conservation counts non-VOID artwork only.

Do not introduce a special VOID difficulty model.

## 5. Exporter / loader proof

Export official game-supported LevelData with VOID cells and corresponding supply plan.

Require exact current-game:

- LevelLoader PASS;
- SupplyPlanLoader PASS;
- solver/replay WIN.

Metadata must include at least:

- `artworkCellCount`;
- `voidCellCount`.

## 6. Identity / packaging / publishing

Update scrubpack identity, metadata and game publisher so VOID layout is hash-bound.

TRANSPARENT background intent becomes publishable only when capability gate is positively open.

No provider/game payload executable changes.

CampaignBuilder/release logic consumes official Difficulty V1 output normally.

## 7. Factory Studio preview

Render VOID exactly as current game ADR/presentation does.

Do not define a competing LF visual rule.

## 8. Permanent tests

Add:

- opaque full-canvas regression with identical legacy output/hashes where applicable;
- VOID ring;
- enclosed hole;
- border-touching VOID;
- VOID-only row/column where legal;
- game reachability/corridor parity fixture;
- gate-closed transparent rejection;
- semi-alpha rejection;
- game minimum-artwork boundary;
- 3..12 color count ignoring VOID;
- deterministic identity/hash tests;
- export/load/replay/Difficulty V1 proof.

Owner-real case:

a 32x32 sprite with approximately 550 transparent pixels must reach READY with supply columns 3, 4 and 5 when all normal production gates pass.

## 9. Report

Builder log must report:

- exact game commit/ADR;
- changed files;
- gate-open/gate-closed behavior;
- focused/full test results;
- sample exported LevelData + supply plan;
- Difficulty V1 results for transparent fixtures;
- owner-real 32x32 3/4/5 column results.

## 10. Publication

Use `CODEX_SYNC_PUBLISH_STANDARD_V01.md`.

Normal push only. Final local HEAD == origin/main, 0/0, clean.

Final response:
return only the GitHub builder log URL.
