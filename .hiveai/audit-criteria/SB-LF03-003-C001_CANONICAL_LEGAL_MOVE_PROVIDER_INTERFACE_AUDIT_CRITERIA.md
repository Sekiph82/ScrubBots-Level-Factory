# SB-LF03-003-C001 — Canonical Legal-Move Provider Interface — Strict Audit Criteria

Target:
`SB-LF03-003 — Define legal-move-provider interface.`

## Canonical authority

Legal player action semantics are not authored by the Level Factory.

Current authority lives in:
`Sekiph82/Scrubbots`

Primary sources:
- `scripts/gameplay/solver/proof_state.gd`
- `scripts/gameplay/solver/proof_kernel.gd`
- relevant M23/M24 accepted gameplay engines.

At criteria preparation, main-game `main` is:
`1144704e6c3647ed1cf76c610be5bd675585734a`.

The builder must resolve current main again when execution starts.

Current canonical ProofState exposes `legal_action_columns()` and current ProofKernel applies a selected column through `apply_placement()`.

## Principle

SB-LF03-003 defines a **provider interface and truth envelope**, not a second legal-move implementation.

The Factory may:
- define versioned request/result/move value types;
- define a legal-move-provider protocol/interface;
- bind requests/results to the accepted CompactSolverState and exact gameplay authority;
- expose AVAILABLE / UNAVAILABLE / ERROR truth;
- consume moves returned by a real verified canonical gameplay bridge when such a bridge exists.

The Factory may not:
- infer legal moves in Python from slot emptiness/supply contents;
- reimplement `ProofState.legal_action_columns()`;
- apply placements/transitions;
- implement target selection/routing/quiescence;
- implement search.

## Move identity

Under the current canonical gameplay authority the player decision is a supply-column/front-batch selection.

The interface may represent a canonical move as a versioned value containing:
- move kind, currently column/front selection;
- canonical column index;
- state/request identity;
- authority/provider identity as evidence.

Do not include UI coordinates, rendered controls, presentation labels, timestamps or player-facing hidden supply contents.

## Result truth

A legal-move query result must be explicit:
- `AVAILABLE`: only when moves came from a verified canonical gameplay provider/bridge;
- `UNAVAILABLE`: canonical provider cannot be invoked safely;
- `ERROR`: malformed input or provider failure.

An AVAILABLE result may legally contain **zero moves**. Zero moves alone must not be labeled:
- DEADLOCK;
- UNSOLVABLE;
- SOLVED.

Those conclusions belong to later canonical solver/search logic.

## Determinism

For identical verified canonical state + provider/authority version:
- move ordering must be deterministic;
- duplicate moves are forbidden;
- canonical current authority ordering is ascending column order when returned by the canonical provider;
- result serialization/digest must be deterministic.

Do not reorder a canonical provider's output into a different gameplay policy unless the interface contract explicitly preserves the canonical order.

## Authority / state binding

Every query/result must bind to:
- accepted `CompactSolverState` digest;
- exact main-game authority SHA;
- provider/interface version;
- canonical source-contract evidence required by SB-LF03-002.

An AVAILABLE provider must not accept:
- unverified checkout;
- source-contract mismatch;
- authority SHA mismatch;
- malformed compact state.

## Interface-only acceptance

Because SB-LF03-001 currently has no stable executable canonical gameplay bridge, SB-LF03-003 may truthfully ship with the canonical adapter reporting UNAVAILABLE.

That is preferable to copying `legal_action_columns()` into Python.

A fake/test provider may be used only as a clearly non-production fixture to prove interface validation. It must never become product authority.

## Validation

Fail closed on:
- wrong schema/version;
- wrong state type/digest binding;
- malformed move kind;
- non-integer/bool column values;
- column outside `0 <= column < state.column_count`;
- duplicates;
- unsorted order when the canonical current provider contract claims ascending order;
- provider authority mismatch;
- AVAILABLE result without verified authority/provider evidence;
- moves present in UNAVAILABLE/ERROR result.

## Immutability

Querying legal moves must not mutate:
- compact state;
- LevelData/source identity;
- supply/slot contents;
- main-game checkout;
- Factory source/candidate/review evidence.

No hidden move cache/truth store is introduced in this task.

## Scope guard

Do not implement:
- SB-LF03-004 deterministic search;
- SB-LF03-005 visited-state memoization policy;
- move application/child-state transition;
- solution/deadlock disposition;
- solver metrics;
- difficulty.

## Required evidence

1. exact canonical main-game SHA and relevant source paths recorded;
2. provider interface is headless and deterministic;
3. no WFC coupling;
4. no Python legal-move derivation;
5. unavailable canonical adapter is truthful when no real bridge exists;
6. structural fake-provider tests prove move/result validation without establishing production authority;
7. AVAILABLE production path, if implemented, requires verified checkout + source contract;
8. state/query bytes remain immutable;
9. full suite green;
10. root TASKS unchanged by builder.

## PASS rule

PASS when Level Factory has a strict versioned legal-move-provider interface that can transport canonical legal choices without becoming another gameplay rules engine, and that fails closed when the canonical provider cannot be invoked safely.
