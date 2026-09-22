# SB-LF03-003-C001 — Canonical Legal-Move Provider Interface

Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`
Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Mission

Work only on:

`SB-LF03-003 — Define legal-move-provider interface.`

Create the builder log before product/test edits:

`.hiveai/codex-logs/SB-LF03-003-C001_CANONICAL_LEGAL_MOVE_PROVIDER_INTERFACE_CODEX_LOG.md`

Do not modify root `TASKS.md`.

## Required reads

Read completely:
- root `TASKS.md`;
- `.hiveai/audits/SB-LF03-002-C001-R01_AUTHORITY_SOURCE_DRIFT_AND_RECONSTRUCTABILITY_STRICT_AUDIT.md`;
- `.hiveai/audit-criteria/SB-LF03-003-C001_CANONICAL_LEGAL_MOVE_PROVIDER_INTERFACE_AUDIT_CRITERIA.md`;
- accepted `simulation_boundary.py`;
- accepted `compact_solver_state.py`;
- current canonical `Sekiph82/Scrubbots` gameplay authority.

Resolve current `Sekiph82/Scrubbots/main` SHA when execution starts.

Inspect at minimum:
- `scripts/gameplay/solver/proof_state.gd`;
- `scripts/gameplay/solver/proof_kernel.gd`;
- `scripts/gameplay/solver/solvability_solver.gd`;
- relevant M23/M24 sources referenced by those files.

## 1. Preserve gameplay authority

The current canonical legal player choices are determined by the main-game ProofState/ProofKernel stack.

Do not implement this logic in Factory Python:

`has empty slot && non-empty supply column => legal`

even though the current canonical source can be read that way.

That would create a second gameplay-rules implementation and would drift when gameplay changes.

The Factory interface transports canonical decisions. It does not decide them.

## 2. Define the provider interface

Create a dedicated headless module, separate from WFC/generator code.

Define immutable/versioned structures for at least:
- legal-move query/request;
- legal move value;
- provider capability/evidence;
- legal-move result.

Use a protocol/interface abstraction for the provider.

The request must bind to the accepted `CompactSolverState` and its deterministic digest.

The result must bind to:
- request/state digest;
- exact gameplay authority;
- provider/interface version;
- capability/evidence.

## 3. Current move representation

Under the current authority, a legal player decision is a supply-column/front selection.

Represent it narrowly, for example:
- move kind: canonical column/front selection;
- column index.

Do not add:
- target cell;
- destination slot;
- route;
- clear target;
- UI coordinates;
- animation/player presentation fields.

Those are not player choices under the canonical solver authority.

## 4. Truthful availability

Use explicit result/capability dispositions:
- AVAILABLE;
- UNAVAILABLE;
- ERROR.

AVAILABLE is allowed only if legal moves actually came from a verified canonical gameplay provider.

Carry forward SB-LF03-002 authority gates:
- checkout identity verified against exact commit;
- actual source bytes verified;
- bounded source contract verified;
- state authority matches provider authority.

If no stable canonical invocation path is available in this task:
- canonical provider returns UNAVAILABLE;
- zero canonical moves are not fabricated;
- do not reimplement `ProofState.legal_action_columns()` in Python.

This truthful UNAVAILABLE route is acceptable for SB-LF03-003 because the task is to define the provider interface.

## 5. Zero legal moves are not a solver verdict

An AVAILABLE result containing zero moves can be structurally valid.

Do not infer:
- SOLVED;
- DEADLOCK;
- UNSOLVABLE;
- INCONCLUSIVE.

Those classifications belong to later search/solver tasks using canonical completion/progress semantics.

## 6. Validation

Fail closed on malformed output.

At minimum:
- schema/version exact;
- move kind exact/versioned;
- column is exact int, not bool/float/string;
- `0 <= column < state.column_count`;
- no duplicate moves;
- canonical current ordering preserved;
- AVAILABLE requires verified authority/provider evidence;
- UNAVAILABLE/ERROR must not carry fabricated moves;
- request/result authority and state digest must match.

Use closed schemas where persisted/serialized dictionaries are supported.

## 7. Test-only fake provider

You may implement a test-only fake provider to prove:
- interface dispatch;
- deterministic ordering validation;
- duplicate/out-of-range rejection;
- AVAILABLE/UNAVAILABLE/ERROR result validation.

The fake provider must be clearly test-only and must never be exported or selected as production gameplay authority.

Do not make product behavior depend on fixture moves.

## 8. Production canonical adapter

A product adapter may:
- expose capability discovery;
- verify authority through accepted SB-LF03-002 verification;
- report UNAVAILABLE until a real stable main-game invocation exists.

Do not add a subprocess command that merely scrapes or pattern-matches GDScript to compute legal moves.

Source inspection proves compatibility. It is not execution.

If you establish a real canonical Godot bridge, it must execute main-game authority and be proven with real cross-repository integration. Otherwise remain UNAVAILABLE.

## 9. Immutability

Snapshot and prove no mutation of:
- CompactSolverState bytes/digest;
- LevelIdentity;
- source/candidate/review artifacts;
- external main-game checkout.

No move cache or second truth store in C001.

## 10. Scope guard

Do not implement:
- applying a move;
- generating child states;
- DFS/BFS/A*;
- canonical state memoization policy;
- solution traces;
- deadlock/solved classification;
- difficulty metrics.

Those are later M03/M04 work.

## 11. Verification

Run:
- focused SB-LF03-003 tests;
- retained SB-LF03-001 and SB-LF03-002 tests;
- relevant M01/M02 immutability tests;
- full `python -m pytest -q`;
- `python -m compileall -q src tests`;
- Level Factory Godot headless editor boot;
- `git diff --check`;
- `git diff --exit-code -- TASKS.md`.

No provider credits or external network calls merely for tests.

## Acceptance

PASS eligibility requires:
- strict versioned provider interface exists;
- moves are only transported from canonical authority, never rederived in Python;
- unavailable canonical execution stays UNAVAILABLE;
- result binds state + authority + provider identity;
- zero moves do not become a solver verdict;
- no search/transition scope theft;
- all regressions green;
- TASKS untouched.

## Publication

Push implementation/tests/docs and finalized builder log to `main`.

At completion return only:
1. finalized builder-log GitHub URL;
2. implementation commit SHA;
3. terminal log-only commit SHA.

Then stop for independent ChatGPT strict audit.
