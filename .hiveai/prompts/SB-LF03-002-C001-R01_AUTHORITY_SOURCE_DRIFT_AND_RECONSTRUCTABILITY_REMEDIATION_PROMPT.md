# SB-LF03-002-C001-R01 — Authority Source Drift + Canonical Reconstructability Remediation

Document role: CODEX REMEDIATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`
Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Mission

Remediate only the strict-audit findings in:

`.hiveai/audits/SB-LF03-002-C001_COMPACT_SOLVER_STATE_CONTRACT_STRICT_AUDIT.md`

Target remains:

`SB-LF03-002 — Define compact solver state.`

Create the R01 builder log **before product/test edits**:

`.hiveai/codex-logs/SB-LF03-002-C001-R01_AUTHORITY_SOURCE_DRIFT_AND_RECONSTRUCTABILITY_REMEDIATION_CODEX_LOG.md`

Do not modify root `TASKS.md`.

## Preserve accepted C001 architecture

Retain:
- dedicated compact-state module;
- immutable typed structures;
- no gameplay transition implementation;
- no WFC coupling;
- deterministic closed-schema serialization;
- LevelData identity;
- ACTIVE/CLEARED mask;
- FIFO supply;
- five-slot contract;
- Factory digest distinct from `ProofState.canonical_key()`;
- no legal move/search/target/routing/difficulty logic.

Do not broaden scope into SB-LF03-003.

## Finding 1 — verify actual authoritative source bytes, not HEAD alone

Current `verify_authority_checkout()` must not return VERIFIED merely because:

`git rev-parse HEAD == declared SHA`.

A dirty working tree at the correct commit must fail closed.

Implement offline verification that binds:
- canonical repository authority;
- declared commit SHA;
- exact `scripts/gameplay/solver/proof_state.gd` path;
- actual committed source bytes/blob identity;
- actual working source bytes used by any future bridge.

Use local Git only. No fetch/network dependency.

At minimum:
1. resolve HEAD;
2. prove the declared commit object/source path exists locally;
3. obtain committed ProofState bytes/blob identity for the declared SHA;
4. compare working-tree ProofState bytes to those committed bytes;
5. return MISMATCH/ERROR/UNAVAILABLE on dirty, missing or unresolved authority.

A caller-supplied SHA is never sufficient proof.

Add tests using a temporary local Git repository that prove:
- exact clean checkout => VERIFIED;
- correct HEAD but modified `proof_state.gd` => MISMATCH;
- wrong HEAD => MISMATCH;
- missing source => UNAVAILABLE/MISMATCH as contractually defined;
- path is never persisted as gameplay state identity.

## Finding 2 — real cross-language/source drift guard

The committed guard must validate Factory assumptions against actual authoritative GDScript source, not only against Factory constants.

Implement a bounded, versioned authority contract inspection/fingerprint.

Do not copy gameplay mechanics.

Verify from authoritative `proof_state.gd` source:
- `const SLOT_COUNT := 5`;
- `const ACTIVE_BYTE := 1`;
- `const CLEARED_BYTE := 0`;
- declarations/domains for:
  - `level`
  - `active`
  - `supply`
  - `slots`
  - `next_seq`
  - `column_count`
  - `preview_depth`
  - `palette_size`
- locked ProofState relative source path.

The contract/fingerprint must be bound to the exact authority SHA and exact authoritative source identity.

Ordinary CI must not depend on the user's absolute checkout path. A capability-gated real-checkout test is acceptable, but the repository must also retain deterministic authority-contract evidence sufficient to detect incompatible drift when the canonical source is supplied.

Add tests proving an intentionally drifted source fails closed.

## Finding 3 — reconstructable occupied-slot and sequence invariants

Align structural validity with canonical ProofKernel reconstruction.

Required:
- occupied `remaining` must be strictly `> 0`;
- `remaining=0` occupied state must fail closed;
- for every occupied slot, `next_seq` must be greater than its `seq`;
- if multiple occupied slots exist, `next_seq > max(seq)`;
- preserve canonical slot count, lifecycle values and batch identity behavior.

Do not implement placement semantics. These are reconstruction invariants only.

Add tests proving:
- valid multi-slot sequence state round-trips;
- zero-remaining occupied slot rejected;
- `next_seq <= max occupied seq` rejected;
- empty-slot-only initial state with canonical `next_seq=1` accepted.

## Canonical source reads

Resolve current `Sekiph82/Scrubbots/main` SHA when execution begins and inspect at minimum:
- `scripts/gameplay/solver/proof_state.gd`;
- `scripts/gameplay/solver/proof_kernel.gd`;
- `scripts/gameplay/slots/slot_batch_state.gd`;
- `scripts/gameplay/slots/five_slot_batch_engine.gd`;
- `scripts/gameplay/supply/batch_supply_engine.gd`.

Record exact SHA and exact source identities in the builder log.

## Verification

Run:
- focused R01 SB-LF03-002 tests;
- retained SB-LF03-001 + SB-LF03-002 tests;
- relevant M01/M02/LevelData immutability tests;
- full `python -m pytest -q`;
- `python -m compileall -q src tests`;
- Level Factory Godot headless editor boot;
- `git diff --check`;
- `git diff --exit-code -- TASKS.md`.

No provider credits/network calls merely for tests.

## Acceptance

R01 is eligible for PASS only when:
- dirty ProofState at correct HEAD cannot verify;
- cross-language assumptions are checked against actual authoritative source evidence;
- occupied state is canonically reconstructable;
- no legal-move/search/gameplay mechanics are introduced;
- all regressions are green;
- TASKS remains untouched.

## Publication

Push implementation/tests/docs and finalized R01 builder log to `main`.

At completion return only:
1. R01 builder-log GitHub URL;
2. final R01 implementation SHA;
3. terminal R01 log-only SHA.

Then stop for independent ChatGPT strict re-audit.
