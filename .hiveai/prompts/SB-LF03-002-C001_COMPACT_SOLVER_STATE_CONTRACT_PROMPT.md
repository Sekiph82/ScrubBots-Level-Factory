# SB-LF03-002-C001 — Compact Solver State Contract

Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`
Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Mission

Work only on:

`SB-LF03-002 — Define compact solver state.`

Create the matching builder log before product/test edits:

`.hiveai/codex-logs/SB-LF03-002-C001_COMPACT_SOLVER_STATE_CONTRACT_CODEX_LOG.md`

Do not modify root `TASKS.md`.

## Required reads

Read completely:
- root `TASKS.md`;
- `.hiveai/audits/SB-LF03-001-C001_HEADLESS_PUZZLE_SIMULATION_BOUNDARY_STRICT_AUDIT.md`;
- `.hiveai/audit-criteria/SB-LF03-002-C001_COMPACT_SOLVER_STATE_CONTRACT_AUDIT_CRITERIA.md`;
- accepted C001 simulation boundary module/tests;
- current canonical `Sekiph82/Scrubbots` gameplay authority.

Resolve current `Sekiph82/Scrubbots/main` SHA when execution begins.

Inspect at minimum:
- `scripts/gameplay/solver/proof_state.gd`;
- `docs/03_LEVEL_DATA_SPEC.md`;
- any directly referenced canonical slot/supply lifecycle constants required to interpret ProofState fields.

## 1. Preserve authority

Do not design an independent Level Factory game state.

The main-game `ProofState` remains the semantic authority.

The Factory state contract may serialize/validate that state shape, but must not become the place where gameplay rules are decided.

Record:
- authority repository;
- exact inspected SHA;
- exact ProofState source path;
- state-contract version.

Carry forward the C001 requirement:
**before any future AVAILABLE cross-repository state/result is trusted, the actual checkout/source authority must be verified against the declared SHA.**

A caller-provided SHA string alone is not proof of checkout identity.

## 2. Define the compact state data envelope

Create a dedicated state-contract module, separate from WFC/generator code.

Represent only canonical future-relevant state needed for faithful ProofState reconstruction.

The current authority includes:
- immutable LevelData identity/reference;
- ACTIVE/CLEARED mask;
- per-column FIFO supply queues;
- exactly five slots under the current ProofState authority;
- occupied slot fields required by ProofState;
- next placement sequence;
- column count;
- preview depth;
- palette size.

Use versioned typed immutable structures.

Do not add:
- UI/render state;
- animation state;
- timestamps;
- provider/network data;
- difficulty score;
- campaign metadata;
- solver search metrics.

## 3. Level identity

Do not embed a mutable second copy of canonical LevelData as gameplay truth.

Bind the state to immutable canonical level identity, such as:
- source/LevelData SHA-256;
- stable level ID if available;
- width/height/cell-count necessary for structural validation.

If raw source bytes are accepted at construction time, copy/hash them and prove caller mutation cannot alter stored identity.

## 4. Board lifecycle

Represent only the canonical ACTIVE/CLEARED logical mask.

Requirements:
- row-major;
- exact cell count;
- only canonical values;
- immutable after construction.

Do not encode rendered RGBA pixels.

## 5. Supply queues

Represent canonical FIFO supply per column exactly enough for faithful reconstruction.

Preserve deterministic column and queue order.

Validate batch entries against the authoritative ProofState shape.

Do not expose hidden supply as a player-facing API; this module is solver/tooling data only.

## 6. Slots and sequence truth

Represent the exact current ProofState slot structure.

Do not generalize slot count from guesses.

Preserve:
- EMPTY vs occupied;
- canonical occupied fields needed by ProofState;
- placement sequence information required for faithful reconstruction.

Do not independently decide gameplay placement or slot legality.

## 7. Deterministic serialization

Provide deterministic canonical serialization and digest for the **data contract**.

Important:
- this digest is a Factory contract/state-envelope digest;
- it is **not automatically the canonical gameplay `ProofState.canonical_key()`** unless a real authority bridge later provides/verifies that exact key.

Do not reimplement `ProofState.canonical_key()` in Python under this task.

Do not implement visited-state memoization policy beyond what deterministic serialization requires.

## 8. Fail-closed structural validation

Reject malformed state:
- schema/version mismatch;
- malformed authority identity;
- mask/cell-count mismatch;
- non ACTIVE/CLEARED mask values;
- supply column mismatch;
- malformed queue entries;
- wrong slot count;
- malformed occupied slots;
- unknown fields when parsing closed-schema dictionaries;
- invalid scalar types/ranges.

Structural validation must not claim:
- state is legally reachable;
- state is solvable;
- a move is legal;
- board is won/lost.

## 9. Cross-language protection

Add narrow static/contract tests comparing the Level Factory contract assumptions with the currently inspected main-game ProofState source.

At minimum protect:
- ProofState source path;
- slot count;
- ACTIVE/CLEARED constants;
- core field names/domains represented by the Factory contract.

If the main-game authority changes incompatibly, tests/authority verification must fail closed rather than silently accepting drift.

Do not hard-code a private machine path into the product contract.

## 10. Scope guard

Do not implement:
- legal action provider;
- move application;
- quiesce;
- target/routing logic;
- solve/deadlock search;
- solution traces;
- difficulty metrics.

Those remain later M03/M04 tasks.

## 11. Verification

Run:
- focused SB-LF03-002 tests;
- retained SB-LF03-001 tests;
- relevant M01/M02 immutability/LevelData tests;
- full `python -m pytest -q`;
- `python -m compileall -q src tests`;
- Level Factory Godot headless editor boot;
- `git diff --check`;
- `git diff --exit-code -- TASKS.md`.

Record all failures and corrections truthfully.

## Acceptance

PASS eligibility requires:
- compact state contract faithfully mirrors canonical ProofState data domains;
- deterministic immutable serialization;
- exact authority/SHA/source binding;
- no second gameplay mechanics implementation;
- no WFC coupling;
- no legal-move/search scope theft;
- malformed states fail closed;
- regression suite green;
- TASKS untouched.

## Publication

Push implementation/tests/finalized builder log to `main`.

At completion return only:
1. finalized builder-log GitHub URL;
2. final implementation commit SHA;
3. terminal log-only commit SHA.

Then stop for independent ChatGPT strict audit.
