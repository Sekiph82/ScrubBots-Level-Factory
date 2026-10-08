# SB-LFX-019-C001-R01 — VOID Closure Audit Criteria

## Retained implementation

Do not redesign accepted C001 architecture.

Retain:

- exact-current game capability gate;
- binary alpha contract;
- VOID = -1 / LevelData V2;
- V1 opaque compatibility;
- current-game loader/validator/supply authority;
- official solver/replay;
- Difficulty V1;
- VOID-aware identity/publisher;
- D1 preview.

## A. Complete current-game fixture matrix

Permanent tests must include each of:

1. VOID ring around artwork;
2. enclosed VOID hole;
3. border-touching VOID;
4. VOID-only row/column;
5. legal VOID corridor/reachability case.

For every fixture that is production-legal:

- emit canonical V2 LevelData with `-1`;
- export a conserving supply plan;
- current exact game `LevelLoader` PASS;
- current exact game `ProductionLevelValidator` PASS;
- current exact game `SupplyPlanLoader` PASS;
- official game solver SOLVED;
- replay WIN;
- official Difficulty V1 result present/finite;
- VOID count and artwork count correct;
- no transparent->color fill.

Tests may be parameterized. Do not substitute screening-only checks for this end-to-end proof.

## B. Owner-authentic 32x32 live evidence

Use a real owner/Claude-created 32x32 transparent PNG from the authorized owner-local workspace if one exists.

Requirements:

- read-only source;
- binary alpha;
- approximately 550 transparent pixels is acceptable; report exact count;
- source SHA-256 recorded;
- source bytes unchanged before/after;
- owner upload -> validation -> pipeline;
- 3, 4 and 5 columns each READY;
- SOLVED;
- replay WIN;
- Difficulty V1;
- LevelLoader / ProductionLevelValidator / SupplyPlanLoader PASS.

The deterministic synthetic 32x32 regression remains required but does not satisfy this owner evidence gate.

If no qualifying owner-authentic file exists, stop truthfully with `OWNER_TRANSPARENT_32X32_FIXTURE_REQUIRED`.

## C. Minimum/color/alpha boundaries

Permanent LF tests must prove:

- semi-alpha rejects;
- D2 199/200 boundary on a 20x20 production board or equivalent exact inherited boundary;
- 25% fraction boundary on a larger board;
- 3..12 used colors count non-VOID only;
- all-VOID rejects;
- gate closed -> UNAVAILABLE and zero partial output.

## D. Opaque V1 compatibility

Require explicit regression that opaque full-canvas content preserves legacy behavior and identity:

- V1 level encoding;
- no VOID metadata fields;
- legacy solver-state identity shape;
- existing opaque pack/identity regressions remain green.

## E. Publisher/pack identity

Require focused proof that:

- V2 VOID metadata carries exact `artworkCellCount` / `voidCellCount`;
- VOID layout changes alter bound identity;
- wrong counts reject;
- TRANSPARENT publish is capability-gated;
- void-free V1 identity remains unchanged.

## F. Studio action-integration classification

Run the exact previously hanging Factory Studio action integration case separately.

PASS if:

- it passes on current R01 HEAD; or
- a C001-caused regression is fixed and it then passes.

If it is proven pre-existing by exact base-vs-head parity under the same environment, record that evidence and do not weaken/skip the test silently.

## G. Full regression

After all R01 changes:

- Godot editor parse/import scan PASS;
- focused VOID unit/integration PASS;
- current-game VOID suite PASS;
- opaque/offline/identity regressions PASS;
- all collected LF pytest tests are accounted for;
- safe full repository pytest completes with zero unresolved failures, except truthful existing capability skips;
- if monolithic execution is operationally impossible, deterministic shards are allowed only if the union exactly covers the collected node IDs and every shard has a final PASS/skip summary;
- compileall PASS;
- JSON/schema checks as applicable PASS;
- `git diff --check` PASS;
- secret scan PASS;
- builder does not edit root `TASKS.md`;
- builder does not write `.hiveai/audits/**`.

## Outcome

PASS only when all A-G close.

Then:

`PASS / CLOSED`

and Simple Owner UI may become current.
