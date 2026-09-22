# SB-LF03-001 — Pure / Headless Puzzle Simulation Boundary

Document role: DURABLE BUILDER BOUNDARY EVIDENCE

## Authority snapshot

The canonical gameplay repository inspected for C001 is:

`https://github.com/Sekiph82/Scrubbots@1144704e6c3647ed1cf76c610be5bd675585734a`

The inspected source set is:

- `docs/01_GAMEPLAY_SPEC.md`
- `docs/03_LEVEL_DATA_SPEC.md`
- `scripts/gameplay/board/board_state.gd`
- `scripts/gameplay/solver/proof_state.gd`
- `scripts/gameplay/solver/proof_kernel.gd`
- `scripts/gameplay/solver/solvability_solver.gd`

The main-game board, proof kernel and solvability solver remain the sole
gameplay-mechanics authority. The Level Factory WFC solver is generation
machinery and is explicitly not selected by this boundary.

## C001 boundary

`src/scrubbots_pixel_factory/simulation_boundary.py` defines a versioned,
headless-only envelope containing:

- canonical authority repository, exact inspected commit SHA, source surfaces
  and bridge version;
- opaque immutable canonical input bytes and their request digest;
- deterministic capability and result dispositions: `AVAILABLE`,
  `UNAVAILABLE`, and `ERROR`;
- bounded, deterministic dependency/error reasons.

The module has no UI, Godot editor, rendering, animation, provider, network,
wall-clock, compact solver-state, legal-move-provider, or gameplay-mechanics
dependency. It does not persist simulation truth or write input/source files.

## Canonical bridge status at C001

`CanonicalGameplayBridge` discovers an explicitly supplied checkout path or the
`SCRUBBOTS_CANONICAL_CHECKOUT` environment capability. Source-file presence is
checked read-only. Because the inspected main-game repository does not expose a
stable configured headless proof-kernel invocation contract in this task, C001
returns `UNAVAILABLE` and never fabricates a Python simulator or gameplay
result. A future real bridge must bind every result to the authority descriptor
and bridge version before it can report `AVAILABLE`.

This evidence records the observed authority snapshot; callers must provide the
authority SHA rather than treating this snapshot as eternal runtime truth.
