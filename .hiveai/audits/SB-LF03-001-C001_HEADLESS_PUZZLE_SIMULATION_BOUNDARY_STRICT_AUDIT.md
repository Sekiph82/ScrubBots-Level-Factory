# SB-LF03-001-C001 — Pure / Headless Puzzle Simulation Boundary — Strict Audit

Document role: INDEPENDENT CHATGPT STRICT AUDIT

## VERDICT

**PASS / CLOSED**

Severity:
- BLOCKER: 0
- MAJOR: 0
- MINOR: 0

## Audited chain

- implementation: `6a402ce538c05d440286375265c126764ac6cfec`
- terminal log-only publication: `d2344f777a967d1378f779910f6603ca558634b8`
- canonical gameplay authority inspected: `Sekiph82/Scrubbots@1144704e6c3647ed1cf76c610be5bd675585734a`

## Independent findings

The C001 implementation satisfies the task as scoped.

### 1. The boundary is pure/headless

`src/scrubbots_pixel_factory/simulation_boundary.py` is a dedicated standard-library-only module.

It does not import:
- Godot/UI/render code;
- provider/network clients;
- Factory WFC/generator search;
- gameplay BoardState/target/routing mechanics.

Its request/result/capability envelopes are immutable dataclasses with deterministic canonical serialization.

### 2. Main-game gameplay authority remains external

The implementation records and constrains the canonical authority to:

`https://github.com/Sekiph82/Scrubbots`

and the inspected authority source set:
- `docs/01_GAMEPLAY_SPEC.md`
- `docs/03_LEVEL_DATA_SPEC.md`
- `scripts/gameplay/board/board_state.gd`
- `scripts/gameplay/solver/proof_state.gd`
- `scripts/gameplay/solver/proof_kernel.gd`
- `scripts/gameplay/solver/solvability_solver.gd`

The Level Factory does not copy gameplay transition semantics into Python.

The Factory WFC solver is not imported or selected as gameplay authority.

### 3. The unavailable bridge is truthful

C001 found no stable configured headless invocation path to the main-game ProofKernel.

The implementation therefore does **not** treat source-file presence as executable capability.

Even with all required source files present, capability remains:

`UNAVAILABLE`

with no fabricated canonical solver disposition.

This is explicitly permitted by the C001 prompt and strict audit criteria.

### 4. Determinism and immutability

The request copies caller bytes into immutable `bytes`, binds the request to an authority digest, and produces deterministic capability/result bytes for identical inputs.

Tests prove:
- caller bytearray is unchanged;
- checkout fixture bytes are unchanged;
- repeated capability/result output is byte-identical;
- malformed authority/request fails closed;
- missing checkout fails closed;
- no hidden gameplay truth store is created.

### 5. Regression evidence

Builder evidence reports:
- focused C001: `8 passed, 1 warning`;
- retained focused M01/M02/LF06/LFX set: `160 passed, 1 warning`;
- full suite: `769 passed, 1 warning`;
- compileall PASS;
- Level Factory Godot headless editor boot PASS;
- diff-check PASS;
- root `TASKS.md` unchanged.

## Non-blocking carry-forward requirement

The current boundary accepts a caller-supplied 40-character authority SHA but, because C001 never exposes an AVAILABLE bridge, it does not yet prove that a configured local checkout's actual Git HEAD/source snapshot equals that declared SHA.

This is **not a C001 closure defect** because:
- checkout presence never becomes executable gameplay capability;
- no gameplay result can be attributed to an unverified checkout;
- every path remains UNAVAILABLE.

Before any later task is allowed to report an AVAILABLE canonical gameplay bridge/result, the implementation must verify the actual checkout/source authority identity against the declared authority SHA and fail closed on mismatch.

## Disposition

`SB-LF03-001` is accepted and may be marked complete.

Next canonical task:

`SB-LF03-002 — Define compact solver state.`
