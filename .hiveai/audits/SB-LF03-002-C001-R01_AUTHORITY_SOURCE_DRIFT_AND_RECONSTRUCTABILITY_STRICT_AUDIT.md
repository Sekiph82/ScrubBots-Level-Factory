# SB-LF03-002-C001-R01 — Authority Source Drift + Canonical Reconstructability — Strict Re-Audit

Document role: INDEPENDENT CHATGPT STRICT RE-AUDIT

## VERDICT

**PASS / CLOSED**

Severity:
- BLOCKER: 0
- MAJOR: 0
- MINOR: 0

## Audited chain

- original C001 implementation: `cc1b9b618acfa659683ee5613fda920747449709`
- original C001 audit: `.hiveai/audits/SB-LF03-002-C001_COMPACT_SOLVER_STATE_CONTRACT_STRICT_AUDIT.md`
- R01 implementation: `da17261003791f5c48a0b9fd25097daa63220e9d`
- R01 terminal log-only publication: `92ed729cf35ced86b47552a535df41e8736921b6`
- canonical gameplay authority independently rechecked: `Sekiph82/Scrubbots@1144704e6c3647ed1cf76c610be5bd675585734a`

## Closure of MAJOR-001 — actual authority source identity

The retained verifier no longer trusts matching HEAD alone.

`verify_authority_checkout()` now:
- resolves checkout HEAD;
- proves the declared commit object exists locally;
- resolves the exact `<commit>:scripts/gameplay/solver/proof_state.gd` blob;
- reads the committed bytes through local Git;
- reads the actual working-tree ProofState bytes;
- compares committed and working bytes;
- records blob/source identities;
- rejects source-byte mismatch;
- rejects a dirty working tree;
- fails closed on missing/unresolved commit/source/Git capability.

The temporary local-Git tests exercise:
- clean checkout => VERIFIED;
- correct HEAD + modified ProofState => MISMATCH;
- wrong HEAD => MISMATCH;
- missing source => unavailable/fail-closed.

No network access is required by the product verifier.

## Closure of MAJOR-002 — real source-contract drift guard

R01 adds `verify_authority_source_contract()`, which inspects supplied authoritative ProofState source bytes.

The bounded contract checks:
- locked canonical repository and declared authority SHA;
- locked `scripts/gameplay/solver/proof_state.gd` path;
- exact source identity;
- `SLOT_COUNT := 5`;
- `ACTIVE_BYTE := 1`;
- `CLEARED_BYTE := 0`;
- declarations for:
  - `level`
  - `active`
  - `supply`
  - `slots`
  - `next_seq`
  - `column_count`
  - `preview_depth`
  - `palette_size`.

The contract fingerprint is deterministic and source-bound. Intentionally drifted source fails MISMATCH.

The canonical main-game source was independently re-read during this audit and still exposes exactly those constants/domains at the same main SHA.

The optional real-local-checkout test remains capability-gated so ordinary CI does not depend on a private absolute path.

## Closure of MAJOR-003 — canonical reconstructability

R01 now rejects occupied slots whose `remaining <= 0`.

This matches canonical `ProofKernel._build_live()`, which reconstructs occupied slots through `SlotBatchState.make_occupied(..., remaining, seq)`, where the initial/remaining count must be strictly positive.

R01 also enforces:

`next_seq > max(occupied slot seq)`

whenever occupied slots exist.

This prevents the Factory envelope from claiming a sequence state that canonical ProofKernel would normalize during reconstruction.

Tests cover:
- valid multi-slot state round-trip;
- zero-remaining rejection;
- non-increasing next-sequence rejection;
- canonical all-empty initial state with `next_seq=1`.

## Architecture retained

The remediation does not add:
- legal-move generation;
- move application;
- target/routing logic;
- search;
- canonical-key reimplementation;
- difficulty semantics;
- WFC/gameplay coupling.

The Factory compact-state digest remains explicitly distinct from `ProofState.canonical_key()`.

## Regression evidence

Builder evidence reports:
- focused SB-LF03-002: `12 passed, 1 skipped, 1 warning`;
- retained focused set: `162 passed, 1 skipped, 1 warning`;
- full suite: `781 passed, 1 skipped, 1 warning`;
- compileall PASS;
- Godot 4.7.2 headless editor boot PASS;
- diff-check PASS;
- root `TASKS.md` unchanged.

The single skip is the intentionally capability-gated real external checkout test.

## Disposition

`SB-LF03-002` is accepted and may be marked complete.

Next canonical task:

`SB-LF03-003 — Define legal-move-provider interface.`
