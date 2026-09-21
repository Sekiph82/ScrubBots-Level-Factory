# SB-LF03-001-C001 — Pure / Headless Puzzle Simulation Boundary

Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`
Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Mission

Work only on:

`SB-LF03-001 — Create pure/headless puzzle simulation boundary.`

Create the matching builder log **before product/test edits**:

`.hiveai/codex-logs/SB-LF03-001-C001_HEADLESS_PUZZLE_SIMULATION_BOUNDARY_CODEX_LOG.md`

Do not modify root `TASKS.md`.

Read completely:
- root `TASKS.md`;
- `.hiveai/audit-criteria/SB-LF03-001-C001_HEADLESS_PUZZLE_SIMULATION_BOUNDARY_AUDIT_CRITERIA.md`;
- accepted M00/M01/M02 contracts relevant to LevelData and immutable candidate/source identity;
- accepted SB-LF06/SB-LFX integration boundaries;
- current `Sekiph82/Scrubbots` canonical gameplay specifications and proof/solver source.

## 1. Mandatory cross-repository authority discovery

Inspect current `Sekiph82/Scrubbots` `main` and record the exact inspected SHA in the builder log and durable boundary evidence.

At preparation time ChatGPT observed:
`1144704e6c3647ed1cf76c610be5bd675585734a`.

Do **not** hard-code that as eternal truth. Resolve current authority when the task runs.

Inspect at minimum:
- `docs/01_GAMEPLAY_SPEC.md`;
- `docs/03_LEVEL_DATA_SPEC.md`;
- `scripts/gameplay/board/board_state.gd`;
- `scripts/gameplay/solver/proof_state.gd`;
- `scripts/gameplay/solver/proof_kernel.gd`;
- `scripts/gameplay/solver/solvability_solver.gd`.

Explicitly prove that:
- the Level Factory's WFC solver is generation machinery, not gameplay puzzle-solver authority;
- gameplay simulation semantics remain owned by the main-game repository.

## 2. Build the boundary, not the mechanics

Create a small dedicated Level Factory package/module for the M03 simulation port.

Prefer a shape such as:
- authority descriptor / capability object;
- versioned simulation-boundary request/result envelope;
- canonical bridge adapter;
- deterministic bounded error handling.

Exact filenames are implementation-owned, but do not bury this inside WFC/generator code.

The boundary must be usable without:
- Factory Studio UI;
- Godot editor UI;
- rendering/animation;
- provider/network/API calls.

## 3. Scope guard against SB-LF03-002/003

Do not prematurely implement:
- the final compact solver-state contract;
- the canonical legal-move-provider interface;
- new gameplay mechanics.

Those belong to:
- SB-LF03-002;
- SB-LF03-003.

For C001, establish the port and authority/capability contract only.

## 4. Canonical bridge

If a stable headless invocation path to the canonical main-game proof kernel can be established without copying gameplay logic:
- use it;
- bind every result to exact authority repository/SHA and bridge version;
- run it headlessly;
- capture bounded stdout/stderr/error evidence;
- prove identical request + authority produces deterministic identical result.

Do not hard-code the user's machine path. Use an explicit configured path/environment/capability discovery mechanism.

If a safe canonical bridge cannot be made real in this task:
- return `UNAVAILABLE` from the boundary;
- explain the missing bridge/dependency;
- do not create a fake Python simulator.

A truthful unavailable canonical adapter is acceptable for C001 if the boundary itself is complete and safe.

## 5. Input/source immutability

The boundary must never mutate:
- canonical LevelData input;
- Factory source/candidate bundles;
- owner-review evidence;
- main-game repository files.

Snapshot and compare bytes where applicable.

No second persistent gameplay truth store.

## 6. Result truth

Use explicit dispositions such as:
- `AVAILABLE`;
- `UNAVAILABLE`;
- `ERROR`.

If an actual canonical simulation operation is supported, its result must distinguish canonical solver dispositions without reinterpretation.

Do not collapse main-game `UNKNOWN_BOUND`/inconclusive semantics into UNSOLVABLE.

Do not infer measured difficulty here.

## 7. Required tests

Add narrow unit/static tests proving:
- authority metadata is version/SHA bound;
- WFC/generator solver is not selected as gameplay authority;
- boundary imports/runs headlessly;
- no UI/render/provider/network dependency;
- missing canonical game checkout/bridge returns UNAVAILABLE;
- malformed authority/config fails closed;
- deterministic repeated capability/result;
- no input/source bytes mutate.

If a real main-game bridge is available in the test environment, add a real cross-repository/headless integration proving the bridge invokes canonical proof/solver code and does not modify either repository.

Do not make CI depend on a private absolute path. Cross-repo integration may be capability-gated, but the unavailable branch must itself be tested.

## 8. Regression gates

Run:
- focused SB-LF03-001 tests;
- relevant M01/M02 LevelData/candidate tests;
- retained Studio/core boundary tests affected by imports;
- full `python -m pytest -q`;
- `python -m compileall -q src tests`;
- Godot headless editor boot for Level Factory;
- `git diff --check`;
- `git diff --exit-code -- TASKS.md`.

Record failures/corrections truthfully.

## Acceptance

PASS eligibility requires:
- pure/headless boundary exists;
- main-game gameplay code remains sole mechanics authority;
- no WFC/gameplay-solver conflation;
- no SB-LF03-002/003 scope theft;
- canonical bridge is real or truthfully UNAVAILABLE;
- exact authority identity is recorded;
- no source mutation;
- no network/provider dependency;
- full regression suite green;
- TASKS untouched by builder.

## Publication

Push implementation/tests and finalized builder log to `main`.

At completion return only:
1. finalized builder-log URL;
2. final implementation commit SHA;
3. terminal log-only commit SHA.

Then stop for independent ChatGPT strict audit.
