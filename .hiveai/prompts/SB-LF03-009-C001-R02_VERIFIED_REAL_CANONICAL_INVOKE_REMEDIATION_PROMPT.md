# SB-LF03-009-C001-R02 — Verified Real Canonical Invoke Remediation

Document role: CODEX REMEDIATION PROMPT

Target: SB-LF03-009 — Reuse canonical reachability/routing semantics rather than importing another game's rules.

R01 re-audit:
.hiveai/audits/SB-LF03-009-C001-R01_REAL_CANONICAL_GODOT_BRIDGE_REMEDIATION_STRICT_REAUDIT.md

Create first:
.hiveai/codex-logs/SB-LF03-009-C001-R02_VERIFIED_REAL_CANONICAL_INVOKE_REMEDIATION_CODEX_LOG.md

Do not edit TASKS.md.

## Absolute goal

R02 does not pass until a real CanonicalHeadlessBridge.invoke() successfully executes canonical ScrubBots gameplay code.
The committed Level Factory runner may orchestrate canonical ProofState, ProofKernel, SolvabilitySolver, LevelData and supply dependencies. It must not duplicate gameplay rules.

## Do not mutate the owner's dirty ScrubBots checkout

Resolve the local ScrubBots repository and current canonical main SHA.
If the primary working checkout is dirty, do not clean/reset/stash/edit it.

Instead create an independent temporary clean Git checkout sourced locally from its Git object database, such as a local-path temporary clone. No network is required or desired.

The temporary execution checkout must:
- resolve the exact canonical SHA;
- have clean git status --porcelain --untracked-files=all;
- have exact required canonical source bytes;
- remain byte/status clean after every bridge invocation;
- be deleted after tests if ephemeral.

Do not use a plain archive/copy if the authority verifier requires Git identity.

## Harden runner capability

capability() must not report AVAILABLE from arbitrary runner-file existence.
Before AVAILABLE require:
- verified clean canonical checkout;
- runner outside canonical checkout;
- runner path points to the expected committed Level Factory bridge runner;
- expected runner SHA-256/version/schema identity;
- Godot executable availability;
- preferably a lightweight real handshake/contract probe.

An arbitrary external GDScript file must not qualify as the canonical bridge runner.

## Real invoke tests

Actually invoke canonical operations:
1. legal_moves: valid canonical request, AVAILABLE response, canonical legal columns.
2. apply_placement: real ProofKernel.apply_placement transition with deterministic structural result.
3. solve: real SolvabilitySolver.solve on a small valid fixture.

Also prove deterministic repeated response, invalid/illegal operation safety, authority/source mismatch fail-closed, malformed response rejection, runner-outside-checkout rule, bounded stdout/stderr/error behavior, and canonical checkout immutability before/after.

Validate that CanonicalBridgeRequest LevelData/source hash is actually consistent with the LevelData payload, not merely transported beside unrelated bytes.

Use the same Godot executable that successfully boots the Level Factory project if available.
Do not skip real invoke merely because the primary owner checkout is dirty. Create the independent clean local execution checkout.

Run focused 009 real integration, retained LF03, full repository pytest, compileall, Godot headless, diff-check and TASKS no-diff.
Publish implementation + finalized R02 task log + terminal log-only commit.