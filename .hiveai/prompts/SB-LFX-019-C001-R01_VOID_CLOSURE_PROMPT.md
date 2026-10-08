# SB-LFX-019-C001-R01 — VOID Fixture + Owner Evidence + Regression Closure

Document role: CODEX REMEDIATION PROMPT

Repository:
`https://github.com/Sekiph82/ScrubBots-Level-Factory`

Strict audit:
`.hiveai/audits/SB-LFX-019-C001_STRICT_AUDIT_V01.md`

Audit criteria:
`.hiveai/audit-criteria/SB-LFX-019-C001-R01_VOID_CLOSURE_AUDIT_CRITERIA.md`

Standing sync/publish:
`docs/process/CODEX_SYNC_PUBLISH_STANDARD_V01.md`

## FIRST OPERATION

Follow the standing safe-sync rule.

Use exact current LF `origin/main`.

Preserve the persistent owner checkout byte-for-byte. If it is dirty/stale, use:

`%TEMP%\ScrubBots-Level-Factory\SB-LFX-019-C001-R01`

Never edit root `TASKS.md`.

Never write `.hiveai/audits/**`.

Builder log:

`.hiveai/codex-logs/SB-LFX-019-C001-R01_VOID_CLOSURE_CODEX_LOG.md`

## Retain accepted C001 implementation

Do not redesign:

- `void_capability.py`;
- binary-alpha import contract;
- VOID V2/-1 representation;
- V1 opaque path;
- current-game loader/validator/supply bridge;
- official solver/replay;
- Difficulty V1;
- VOID-aware exporter/identity/publisher;
- BG01 preview behavior.

Fix only defects exposed by the required closure work.

## R01-1 — complete permanent fixture matrix

Add production-legal permanent fixtures for:

- ring;
- enclosed hole;
- border-touching VOID;
- VOID-only row/column;
- legal corridor.

Every fixture must go through the real end-to-end authority, not only the Python screening simulator.

For every fixture prove:

1. canonical LevelData V2 with `-1`;
2. exact non-VOID artwork count and VOID count;
3. conserving 3/4/5-compatible supply plan as applicable;
4. current exact game LevelLoader PASS;
5. current exact game ProductionLevelValidator PASS;
6. current exact game SupplyPlanLoader PASS;
7. official solver SOLVED;
8. replay WIN;
9. official Difficulty V1;
10. exported bytes/metadata remain identity-bound.

Preserve the existing step-exact screening/corridor differential tests.

## R01-2 — real owner 32x32 transparent artwork evidence

The C001 generated rectangle remains a deterministic regression but does not satisfy owner evidence.

Inspect the owner-local workspace read-only:

`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

and its existing owner art/output subtrees for a real owner/Claude-created **32x32 transparent PNG**.

Prefer the owner's actual level-art set, including an orange-fox style sprite if present.

Do not:

- modify the owner file;
- normalize it in place;
- overwrite it;
- move it;
- add it to Git;
- relabel a generated test image as owner-real.

For a qualifying file:

- require binary alpha;
- record exact path, SHA-256, dimensions, transparent count, artwork count and used colors;
- import exact bytes through owner upload;
- verify stored upload bytes equal the original;
- run columns 3, 4 and 5;
- require READY, SOLVED, replay WIN, official Difficulty V1;
- require LevelLoader, ProductionLevelValidator and SupplyPlanLoader PASS;
- verify original source SHA/bytes remain unchanged afterward.

If no owner-authentic qualifying file exists, stop:

`OWNER_TRANSPARENT_32X32_FIXTURE_REQUIRED`

Do not fabricate this gate.

## R01-3 — explicit LF D2/color/alpha boundary tests

Add permanent LF tests for:

- semi-alpha rejection;
- 20x20: 199 non-VOID rejects, 200 accepts when other production rules are valid;
- larger-board 25% boundary;
- used-color count ignores VOID;
- all-VOID rejects;
- capability gate closed gives UNAVAILABLE and zero partial artifacts.

## R01-4 — opaque V1 compatibility and publisher identity

Add or strengthen focused regressions proving:

- opaque full-canvas stays V1;
- opaque legacy encoding/hash/metadata shape remains unchanged;
- no `artworkCellCount` / `voidCellCount` in legacy V1 identity where the old schema omitted them;
- V2 carries exact counts;
- changing VOID layout changes bound identity;
- wrong V2 counts reject;
- TRANSPARENT publish remains capability-gated.

Do not alter legacy V1 bytes merely to simplify V2 code.

## R01-5 — classify the Factory Studio action integration hang

Run the exact previously hanging action-integration test/suite by itself under the correct Godot/Python environment.

If current C001 caused the hang, fix it and retain assertions.

If uncertain, compare the exact same test at:

- pre-C001 base `6e011d1f273d173ff41bb2f563a87c868213d28c`;
- current R01 HEAD;

using equivalent clean worktrees and environment.

Do not:

- mark it xfail;
- skip it permanently;
- weaken assertions;
- delete it;
- add arbitrary sleeps as proof.

Record elapsed time and final result.

## R01-6 — complete the full regression

The prior broad run is invalid for closure because it was interrupted after unresolved `F` markers and before final tracebacks.

After all fixes:

1. run Godot editor parse/import scan;
2. run focused VOID suites;
3. run current-game `tests/void_cells_c001.gd`;
4. run opaque/offline/pack identity regressions;
5. run a complete repository pytest.

If one monolithic pytest is operationally impossible because of process orchestration, deterministic shards are permitted only if:

- collect node IDs first;
- record the complete collected set;
- every collected node ID belongs to exactly one executed shard;
- every shard finishes with a final summary;
- union coverage equals the collected set;
- no unresolved failure remains.

Do not hide the action-integration case from coverage.

Run compileall, diff check and secret scan.

## Publication

Implementation/test commit separate from builder-log/evidence commit.

Fetch/prune before push.

Normal fast-forward push only.

Final HEAD == origin/main, 0 ahead / 0 behind, clean task worktree.

## Final state

If everything passes:

`AWAITING_GPT_SB_LFX_019_C001_R01_STRICT_REAUDIT`

Final response:
return only the GitHub builder log URL.
