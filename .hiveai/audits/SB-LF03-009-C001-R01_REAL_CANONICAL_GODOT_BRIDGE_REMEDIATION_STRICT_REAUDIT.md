# SB-LF03-009-C001-R01 — REAL CANONICAL GODOT BRIDGE REMEDIATION — Strict Re-Audit

Document role: INDEPENDENT CHATGPT STRICT RE-AUDIT

## VERDICT

**CHANGES_REQUIRED**

- BLOCKER: 1
- MAJOR: 1
- MINOR: 0

## Audited chain

- C001 implementation retained
- R01 implementation: `7e540c8145890f568991a98ce5f65c998eac18d7`
- R01 terminal builder-log publication: `4fd60412082a381a01da57a660a344f2bf67e988`
- R01 master publication: `3d886d4f46eb239bd880fe70b1bef5d3ba4d3c29`
- canonical gameplay authority independently remains `Sekiph82/Scrubbots@1144704e6c3647ed1cf76c610be5bd675585734a`

## Independent finding

## BLOCKER-001 — Real canonical invoke still did not execute

R01 added a Level-Factory-owned external Godot runner that imports canonical `ProofState`, `ProofKernel`, `SolvabilitySolver`, LevelData and supply scripts. This is meaningful progress and avoids a Python gameplay clone.

But the required real integration did not execute. The builder reports the owner checkout is dirty and authority verification therefore fails closed. No successful `CanonicalHeadlessBridge.invoke()` result exists for legal moves, placement transition or solve.

The task criteria require actual canonical gameplay execution before PASS.

## MAJOR-001 — Capability still overstates runner readiness

After checkout/source verification, `capability()` returns AVAILABLE when `runner_path` merely exists as a file. It does not enforce that the runner is outside the canonical checkout, that it is the expected committed runner identity/version, or that a contract handshake/invocation succeeds. Those stricter checks happen later in `invoke()`.

Thus capability can still say AVAILABLE for a runner configuration that invoke immediately rejects.

## Regression evidence

R01 batch reports:
- retained LF03: `87 passed, 3 skipped, 1 warning`;
- full pytest: `842 passed, 3 skipped, 2 warnings, 6 failed`;
- compileall PASS;
- Godot headless editor boot PASS;
- TASKS builder diff zero.

The six full-suite failures are not automatically attributed to this task. Task closure is based on its own contract plus any explicit repository-wide gate in its criteria.

## Architecture / safety

No Python copy of canonical ProofState/ProofKernel gameplay mechanics was accepted. Dirty canonical authority correctly fails closed rather than being used as production truth.

## Final disposition

**CHANGES_REQUIRED**

## Required next action

Use a clean verified Scrubbots checkout at the exact authority commit, without modifying the owner's dirty checkout. Execute real legal_moves plus apply_placement and/or solve through the committed external runner, prove deterministic repeat and checkout immutability. Harden capability so AVAILABLE requires the same runner-location/identity/version safety preconditions used by invoke, preferably a lightweight schema/version handshake.
