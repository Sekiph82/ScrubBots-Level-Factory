# SB-LF03-001-C001 — Pure / Headless Puzzle Simulation Boundary — Strict Audit Criteria

Target:
`SB-LF03-001 — Create pure/headless puzzle simulation boundary.`

## Canonical authority

Gameplay mechanics are not authored by the Level Factory.

The current canonical gameplay authority lives in:
`Sekiph82/Scrubbots`

Relevant canonical main-game surfaces include:
- `scripts/gameplay/solver/proof_state.gd`
- `scripts/gameplay/solver/proof_kernel.gd`
- `scripts/gameplay/solver/solvability_solver.gd`
- `scripts/gameplay/board/board_state.gd`
- locked gameplay/LevelData specifications.

At audit preparation, observed main-game `main` SHA:
`1144704e6c3647ed1cf76c610be5bd675585734a`.

The implementation must record the exact source SHA it actually inspected. Do not assume this preparation SHA is still current when Codex runs.

## Principle

SB-LF03-001 creates the **boundary**, not a second gameplay implementation.

The Level Factory may:
- define a stable, versioned headless simulation port/capability contract;
- discover/identify the canonical main-game authority;
- invoke a canonical bridge when that bridge is demonstrably available;
- report UNAVAILABLE when the canonical bridge cannot be used safely.

It may not:
- copy/rewrite gameplay mechanics into Python merely to make the boundary executable;
- treat the Factory WFC solver as the gameplay puzzle solver;
- invent unresolved win/lose, slot, supply, routing, targeting or move semantics;
- implement SB-LF03-002 compact solver state or SB-LF03-003 legal-move-provider semantics early.

## BLOCKERS

FAIL if:
- a second gameplay truth implementation is created in Level Factory;
- UI/scene rendering is required for simulation;
- provider/network/API access is required;
- WFC/generation search is presented as gameplay simulation;
- main-game source authority is not identity/version bound;
- unavailable canonical runtime is silently replaced with guessed behavior;
- simulation mutates canonical LevelData/source inputs;
- TASKS is edited by the builder.

## Boundary contract

The Level Factory boundary must be:
- pure/headless;
- deterministic for identical canonical inputs and authority version;
- versioned;
- explicit about authority repository/SHA;
- explicit about AVAILABLE vs UNAVAILABLE / ERROR;
- free of UI, rendering, animation and wall-clock gameplay timing;
- free of provider/network dependencies.

The boundary should expose only what SB-LF03-001 needs, such as:
- capability/authority discovery;
- request envelope identity;
- result/disposition envelope;
- bounded stderr/error evidence;
- canonical authority metadata.

Do not prematurely define the compact solver state or legal-move contract assigned to SB-LF03-002/003.

## Canonical bridge behavior

If a stable real bridge to the main-game proof kernel already exists or can be added without duplicating mechanics:
- invoke the canonical main-game headless path;
- bind evidence to exact main-game commit/source identities;
- prove no scene/UI dependency;
- prove deterministic repeated result.

If no safe bridge exists yet:
- boundary still exists;
- capability must return `UNAVAILABLE` with the exact dependency reason;
- no fake simulator/result may be synthesized.

## Immutability

Tests must prove:
- LevelData/input bytes are unchanged;
- no Factory candidate/source/review state is mutated;
- no main-game repository file is mutated;
- repeated capability/simulation calls create no hidden truth store.

## Required evidence

At minimum:
1. exact authority repository + inspected SHA recorded;
2. WFC/generator solver explicitly excluded from gameplay-simulator authority;
3. headless boundary loads without Studio UI;
4. no network/provider call path;
5. AVAILABLE path, if present, routes to canonical main-game authority;
6. unavailable path fails closed and explains why;
7. repeated calls are deterministic;
8. source/input immutability proven;
9. full existing suite remains green;
10. root TASKS remains unchanged by builder.

## PASS rule

PASS when Level Factory has a truthful pure/headless simulation boundary that preserves the main-game gameplay implementation as the sole mechanic authority and never fabricates simulation when the canonical bridge is unavailable.
