# SB-LF03-009-C001-R01 — Real Canonical Godot Bridge Remediation

Document role: CODEX REMEDIATION PROMPT

Target: `SB-LF03-009 — Reuse canonical reachability/routing semantics rather than importing another game's rules.`

Audit:
`.hiveai/audits/SB-LF03-009-C001_CANONICAL_GAMEPLAY_SEMANTICS_BRIDGE_STRICT_AUDIT.md`

Create first:
`.hiveai/codex-logs/SB-LF03-009-C001-R01_REAL_CANONICAL_GODOT_BRIDGE_REMEDIATION_CODEX_LOG.md`

Do not edit `TASKS.md`.

## Canonical authority

Resolve current:
https://github.com/Sekiph82/Scrubbots

A local main-game checkout may be used **read-only** only after verifying it matches the resolved authority SHA and required source bytes. Do not modify, clean, reset, stash, generate files into, or commit in that checkout.

## Mission

Create a committed Level-Factory-owned external Godot runner outside the canonical Scrubbots checkout.

Run Godot with the verified Scrubbots project as `--path`, while the external runner only orchestrates canonical main-game scripts.

The runner must execute real canonical behavior, not source-pattern emulation.

Support the minimum strict operations required for proof, for example:
- legal moves from canonical ProofState;
- apply a canonical placement/transition through ProofKernel;
- solved/completion query;
- optional canonical SolvabilitySolver solve.

Define closed request/response schemas and bind:
- exact authority SHA;
- verified ProofState/source identity;
- request digest;
- state/LevelData identity;
- operation;
- runner/bridge version.

Validate LevelData/state reconstruction. No Python gameplay clone.

## Capability truth

`capability()` must not report AVAILABLE merely because a runner file exists.

AVAILABLE must require a verified configuration that can actually satisfy the bridge contract. Runner must be outside main-game checkout and must be the expected committed runner identity/version.

## Real integration tests

Actually call `invoke()` and prove:
- real canonical legal moves or equivalent canonical result;
- at least one real ProofKernel transition or SolvabilitySolver result;
- deterministic repeated response;
- an illegal/unavailable/error case;
- authority/source mismatch fail-closed;
- malformed response rejection;
- bounded stdout/stderr/error handling;
- main-game checkout byte/status immutability before/after.

Do not skip the real integration if the canonical checkout is available locally. If a required Godot executable is unavailable, document exact blocker; do not fabricate PASS.

Run focused 009 real integration + retained LF03 + full gates. Publish R01 implementation/log/terminal commit.
