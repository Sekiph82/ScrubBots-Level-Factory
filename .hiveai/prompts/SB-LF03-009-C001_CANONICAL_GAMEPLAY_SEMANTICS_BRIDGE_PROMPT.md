# SB-LF03-009-C001 - Canonical Gameplay Semantics Bridge

Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`

## Mission

Implement only:

`SB-LF03-009 - Reuse canonical reachability/routing semantics rather than importing another game's rules.`

Create first:

`.hiveai/codex-logs/SB-LF03-009-C001_CANONICAL_GAMEPLAY_SEMANTICS_BRIDGE_CODEX_LOG.md`

Do not edit `TASKS.md`.

## Canonical authority

Resolve current `Sekiph82/Scrubbots/main`.

Read current:
- `scripts/gameplay/solver/proof_state.gd`;
- `proof_kernel.gd`;
- `solvability_solver.gd`;
- every routing/targeting/slot/supply dependency actually used by ProofKernel.

## Required outcome

Establish a real read-only headless bridge from Level Factory tooling to the canonical main-game runtime.

Preferred architecture:
- caller-configured canonical Scrubbots checkout;
- SB-LF03-002 exact authority/source verification first;
- Level Factory-owned external bridge runner/request file outside the main-game checkout;
- Godot runs with the canonical Scrubbots project as `--path`;
- bridge executes canonical GDScript authority;
- JSON or similarly strict declarative request/response envelope;
- no modification of main-game checkout.

Do not assume an external script technique works. Test it. If another safe read-only mechanism is required, document it.

Do not copy gameplay logic into Python or generated bridge code.

The bridge may only orchestrate canonical classes and serialize their outputs.

## Request identity

Bind:
- bridge schema/version;
- exact authority SHA;
- exact verified source-contract identity;
- LevelData source/hash identity;
- compact-state/request digest;
- requested operation.

Support only the minimum operations needed by LF03, such as:
- legal moves;
- canonical state key;
- apply legal placement/transition;
- solved/completion query;
- canonical solver invocation.

Do not expose UI/runtime presentation.

## Real tests

Use a real main-game checkout capability if present.

Prove:
- exact checkout/source verification;
- real Godot headless invocation;
- at least one canonical legal move query;
- real transition/solver response;
- deterministic repeat;
- malformed/tampered authority fails closed;
- main-game checkout status and required files unchanged before/after.

Ordinary CI may capability-gate external-checkout integration, but committed fixture/contract tests must remain deterministic.

If no safe real bridge can be completed, log the exact blocker and preserve truthful UNAVAILABLE. Do not fabricate PASS.

Run all retained LF03 and full repository gates. Publish task implementation + task log + terminal log-only commit.
