# SB-LF03-002-C001 — Compact Solver State Contract — Strict Audit

Document role: INDEPENDENT CHATGPT STRICT AUDIT

## VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Severity:
- BLOCKER: 0
- MAJOR: 3
- MINOR: 0

## Audited chain

- implementation: `cc1b9b618acfa659683ee5613fda920747449709`
- terminal log-only publication: `8ed7cc3eaf882a684484bbf4b1266f987abd31f8`
- canonical gameplay authority inspected independently: `Sekiph82/Scrubbots@1144704e6c3647ed1cf76c610be5bd675585734a`
- canonical state source: `scripts/gameplay/solver/proof_state.gd`
- canonical reconstruction source: `scripts/gameplay/solver/proof_kernel.gd`

## Accepted implementation retained

The implementation gets the large architectural choices right and they should be preserved:

- dedicated standard-library-only compact state module;
- immutable typed data structures;
- no UI/render/provider/network dependency;
- no WFC coupling;
- no legal-move/search/target/routing/difficulty implementation;
- canonical repository + declared commit SHA + ProofState path binding;
- deterministic closed-schema JSON serialization;
- explicit statement that the Factory digest is not `ProofState.canonical_key()`;
- immutable LevelData source identity;
- ACTIVE/CLEARED mask;
- FIFO supply columns;
- five-slot shape;
- next sequence / column count / preview depth / palette size;
- closed-schema parser;
- caller-owned mutable byte input copied before hashing;
- full repository regression suite green;
- root `TASKS.md` untouched by the builder.

These parts are not to be rewritten unless required for the findings below.

# MAJOR-001 — checkout verification proves HEAD, not the actual ProofState source bytes

`verify_authority_checkout()` currently:

1. checks the configured path exists;
2. checks `proof_state.gd` exists;
3. runs `git -C <checkout> rev-parse HEAD`;
4. returns VERIFIED when HEAD equals the declared SHA.

That is insufficient for the carry-forward requirement from SB-LF03-001 and the SB-LF03-002 criteria.

A checkout can be at the correct commit SHA while `scripts/gameplay/solver/proof_state.gd` is modified in the working tree. The current verifier would still return VERIFIED.

Therefore an AVAILABLE future bridge could trust source bytes that are not the bytes belonging to the declared canonical commit.

## Required remediation

Verification must bind the actual source bytes to the declared commit.

A valid offline approach may:
- obtain the committed source bytes/blob for `<declared SHA>:scripts/gameplay/solver/proof_state.gd` using local Git only;
- compare those committed bytes/blob identity with the working-tree file used by the bridge;
- or prove the target source path is clean and byte-identical to the declared commit.

Fail closed on:
- dirty/mutated ProofState working-tree bytes;
- missing commit object;
- missing source at the declared commit;
- source mismatch;
- unresolved Git identity.

No network call is required or allowed for this verification.

# MAJOR-002 — committed cross-language drift tests do not actually compare against ProofState source

The criteria require:

> cross-language/static evidence shows state fields remain aligned with current ProofState

and the implementation prompt requires tests comparing the Factory contract assumptions with the currently inspected main-game `ProofState` source.

The committed unit test currently checks only Factory-local constants:

- `PROOF_STATE_FIELDS`
- `SLOT_COUNT`
- `ACTIVE_BYTE`
- `CLEARED_BYTE`

It does not read/parse/verify the authoritative GDScript source.

Therefore if the main-game ProofState changes but the Python constants remain unchanged, this committed guard can remain green.

## Required remediation

Add a bounded authority-contract fingerprint/inspection mechanism that is genuinely derived from the canonical source.

The committed test suite must prove the contract against actual authoritative source bytes when a canonical checkout is available, while keeping ordinary CI independent from a private machine path.

Acceptable designs include:
- a versioned source-contract fingerprint bound to exact commit + exact ProofState source SHA/blob identity, plus a local-checkout integration gate that parses/asserts the required constants/field declarations;
- another equally strict offline source inspection mechanism.

At minimum verify from authoritative source:
- `SLOT_COUNT = 5`;
- `ACTIVE_BYTE = 1`;
- `CLEARED_BYTE = 0`;
- the state domains `level, active, supply, slots, next_seq, column_count, preview_depth, palette_size`;
- the locked ProofState source path.

If the source drifts incompatibly, capability/contract verification must fail closed rather than silently accepting the Python schema.

Do not copy gameplay transition mechanics into Python.

# MAJOR-003 — the Factory accepts an occupied slot state that canonical ProofKernel cannot reconstruct

`OccupiedSlot.__post_init__()` currently allows:

`remaining == 0`

because it rejects only `remaining < 0`.

However the canonical `ProofKernel._build_live()` reconstructs an occupied slot with:

`SlotBatchState.make_occupied(batch_id, color, remaining, seq)`

and canonical `SlotBatchState.make_occupied()` requires:

`initial_count > 0`.

Therefore an occupied Factory slot with `remaining=0` passes the Factory contract but fails canonical reconstruction.

This violates the task goal of a state contract faithful enough for canonical ProofState reconstruction.

A related canonicality invariant should also be enforced for sequencing:
- when occupied slots exist, `next_seq` must be greater than every occupied slot sequence;
- otherwise canonical reconstruction normalizes the next sequence rather than faithfully reproducing the supplied envelope.

## Required remediation

- occupied slot `remaining` must be strictly positive;
- add deterministic tests rejecting zero-remaining occupied slots;
- enforce `next_seq > max(occupied seq)` for canonical states;
- add positive and negative tests for sequence reconstruction invariants;
- retain EMPTY as `None` and do not invent additional slot lifecycle semantics.

## Regression evidence reviewed

Builder reported:
- focused SB-LF03-002: `8 passed, 1 warning`;
- retained focused set: `176 passed, 1 warning`;
- full suite: `777 passed, 1 warning`;
- compileall PASS;
- Godot headless editor boot PASS;
- diff-check PASS;
- `TASKS.md` unchanged.

These regressions are green, but the tests do not cover the three strict semantic gaps above.

## Disposition

`SB-LF03-002` remains active for R01 remediation.

Do not advance to SB-LF03-003 until this task independently re-audits PASS.
