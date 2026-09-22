# SB-LF03-002 — Compact Solver State Contract

Document role: DURABLE BUILDER BOUNDARY EVIDENCE

## Canonical authority snapshot

The canonical gameplay authority inspected for C001/R01 is:

`https://github.com/Sekiph82/Scrubbots@1144704e6c3647ed1cf76c610be5bd675585734a`

Primary source:

`scripts/gameplay/solver/proof_state.gd`

The locked ProofState source identity at that authority is UTF-8 SHA-256
`408893348e8abab089de98586999fc15bafc3b07b83f21458152788a34e78620`.

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

`verify_authority_checkout()` performs only read-only local Git operations for
an explicit caller path. It resolves the actual HEAD, proves the declared
commit and exact ProofState path/blob exist locally, reads the committed source
bytes, compares them byte-for-byte with the working source, and fails closed on
any dirty checkout. It returns `VERIFIED`, `UNAVAILABLE`, `MISMATCH`, or
`ERROR`; a declared SHA alone is never treated as proof of checkout identity.
The checkout path is not stored in state identity. A future AVAILABLE
bridge/state import must require a `VERIFIED` result against the declared SHA.

`verify_authority_source_contract()` is a versioned, bounded source inspection
that parses the locked ProofState constants and field declarations, hashes the
exact supplied bytes, and binds the resulting contract fingerprint to the
canonical authority SHA, relative source path, and expected source identity.
Drifted or incompatible source evidence is `MISMATCH`, not a usable contract.

Occupied slots are reconstructable-only data: `remaining` must be strictly
positive and `next_seq` must exceed every occupied slot sequence. Empty initial
state retains canonical `next_seq=1`.

No UI, rendering, animation, provider, network, persistence, WFC, legal-move,
or gameplay-mechanics dependency is introduced.
