# SB-LF03-002 — Compact Solver State Contract

Document role: DURABLE BUILDER BOUNDARY EVIDENCE

## Canonical authority snapshot

The canonical gameplay authority inspected for C001 is:

`https://github.com/Sekiph82/Scrubbots@1144704e6c3647ed1cf76c610be5bd675585734a`

Primary source:

`scripts/gameplay/solver/proof_state.gd`

Supporting LevelData source:

`docs/03_LEVEL_DATA_SPEC.md`

The inspected ProofState defines a pure-data snapshot containing an immutable
LevelData reference, a row-major ACTIVE/CLEARED mask (`1`/`0`), FIFO supply
queues with `{id,color,count}` entries, exactly five slots, occupied slot
entries `{batch_id,color,remaining,seq,state}`, `next_seq`, `column_count`,
`preview_depth`, and `palette_size`.

Directly referenced supply/slot contracts lock column count to 3..5, preview
depth to 3..4, non-negative color IDs, positive batch counts, and occupied slot
states `ACTIVE`/`WAITING`. These are structural field domains only; this module
does not decide placement, clearing, legality, targeting, routing, or search.

## Factory contract

`src/scrubbots_pixel_factory/compact_solver_state.py` provides frozen typed
structures for:

- `SolverStateAuthority` — canonical repository, exact commit SHA, exact
  ProofState source path, and authority version;
- `LevelIdentity` — source SHA-256, stable level ID, width/height, and derived
  cell-count identity, without storing a mutable LevelData copy;
- `SupplyBatch` and `OccupiedSlot` — exact ProofState data entries;
- `CompactSolverState` — immutable mask, FIFO columns, five-slot tuple, and
  reconstruction configuration fields;
- deterministic closed-schema serialization and a Factory state-envelope
  digest.

The digest is explicitly not `ProofState.canonical_key()`. No canonical-key,
move, transition, quiesce, search, solver metric, or difficulty implementation
exists in this module.

## Authority verification and fail-closed behavior

`verify_authority_checkout()` performs only read-only local `git rev-parse
HEAD` plus ProofState-source presence checks for an explicit caller path. It
returns `VERIFIED`, `UNAVAILABLE`, `MISMATCH`, or `ERROR`; a declared SHA alone
is never treated as proof of checkout identity. The checkout path is not stored
in state identity. A future AVAILABLE bridge/state import must require a
`VERIFIED` result against the declared SHA.

No UI, rendering, animation, provider, network, persistence, WFC, legal-move,
or gameplay-mechanics dependency is introduced.
