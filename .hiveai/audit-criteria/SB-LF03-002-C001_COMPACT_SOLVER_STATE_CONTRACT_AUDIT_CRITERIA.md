# SB-LF03-002-C001 — Compact Solver State Contract — Strict Audit Criteria

Target:
`SB-LF03-002 — Define compact solver state.`

## Canonical authority

The Level Factory must not invent a second solver-state semantics.

Current canonical state authority lives in:
`Sekiph82/Scrubbots`

At criteria preparation, main-game `main` is:
`1144704e6c3647ed1cf76c610be5bd675585734a`

The builder must resolve the current SHA again when execution begins.

Primary authority:
- `scripts/gameplay/solver/proof_state.gd`
- `docs/03_LEVEL_DATA_SPEC.md`
- relevant accepted gameplay specs.

The current main-game `ProofState` carries:
- immutable source LevelData reference;
- ACTIVE/CLEARED row-major mask;
- FIFO supply queues per column;
- five slots;
- monotonic placement sequence state;
- column count;
- preview depth;
- palette size.

Its canonical future-state fingerprint intentionally excludes rendering, timestamps, instance IDs and absolute placement sequence values where relative ordering is sufficient.

## Principle

SB-LF03-002 defines a **data contract**, not a transition engine.

Allowed:
- a versioned, deterministic compact solver-state envelope;
- exact field/type/shape validation derived from canonical ProofState;
- immutable source/authority identity binding;
- deterministic serialization/digest;
- explicit unavailable/error handling when canonical state cannot be obtained.

Forbidden:
- implementing legal move generation;
- implementing placement, clearing, target selection, routing or solver search;
- reimplementing `ProofState.is_solved()`, `legal_action_columns()`, `canonical_key()` semantics in Factory Python as gameplay authority;
- treating WFC state as gameplay solver state;
- inventing slot/supply semantics beyond canonical main-game truth.

## Required state domains

The compact state contract must account for the canonical future-relevant domains without UI/runtime object identity:

1. **Authority identity**
   - canonical repository;
   - exact authority SHA;
   - schema/contract version.

2. **Immutable level identity**
   - canonical LevelData/source identity or digest;
   - width/height/cell-count identity sufficient to validate mask shape;
   - no mutation of source LevelData.

3. **Board lifecycle**
   - row-major ACTIVE/CLEARED mask only;
   - no rendered pixel state.

4. **Supply**
   - deterministic per-column FIFO queues;
   - batch identity where needed for faithful reconstruction;
   - color/count values;
   - column ordering preserved.

5. **Slots**
   - exactly the canonical slot count currently defined by ProofState;
   - empty vs occupied;
   - batch/color/remaining/placement-sequence/lifecycle fields required by the authority.

6. **Sequencing/config needed for faithful reconstruction**
   - next sequence;
   - column count;
   - preview depth;
   - palette size.

Do not add analytics, measured difficulty, campaign state, UI state or provider metadata.

## Compactness

The state must be data-oriented and deterministic:
- no Node/RefCounted/live engine instances;
- no timestamps;
- no absolute filesystem path as state identity;
- no rendered image bytes;
- no duplicated derived fields that can disagree with canonical data unless independently validated.

## Authority drift / identity

The contract must bind to the exact main-game authority version used to derive it.

Before a future AVAILABLE bridge/state import is accepted, actual checkout/source authority must be verified against the declared SHA. A caller-supplied SHA alone is insufficient.

If runtime authority identity cannot be verified, fail closed.

## Validation

Fail closed on at least:
- wrong schema/version;
- wrong authority repository/SHA format;
- authority mismatch when a checkout/source is claimed verified;
- mask length not matching canonical cell count;
- mask byte outside canonical ACTIVE/CLEARED values;
- supply column count mismatch;
- malformed FIFO batch entry;
- slot count mismatch;
- malformed occupied slot entry;
- invalid integer/range types;
- unknown top-level fields if the schema is closed.

Validation may prove structural contract integrity. It must not claim gameplay legality/solvability.

## Determinism / immutability

Tests must prove:
- identical logical state serializes byte-identically;
- caller-owned input containers cannot alias/mutate the stored state;
- source LevelData/input bytes remain unchanged;
- serialization order does not depend on dictionary iteration;
- no hidden persistence/truth store is created.

## Scope guard

SB-LF03-002 must not implement:
- SB-LF03-003 legal-move-provider interface;
- SB-LF03-004 search;
- SB-LF03-005 memoization policy beyond deterministic state digest/serialization required by this state contract;
- solver metrics/difficulty.

## Required evidence

1. exact main-game ProofState authority SHA/source path recorded;
2. cross-language/static evidence shows state fields remain aligned with current ProofState;
3. canonical slot count and ACTIVE/CLEARED values are authority-derived or locked against source;
4. malformed state cases fail closed;
5. no gameplay transitions exist in the Factory state module;
6. no WFC solver coupling;
7. full repository suite green;
8. TASKS unchanged by builder.

## PASS rule

PASS when the Level Factory has a compact, deterministic, immutable, versioned solver-state data contract that faithfully represents canonical ProofState truth without becoming a second gameplay mechanics implementation.
