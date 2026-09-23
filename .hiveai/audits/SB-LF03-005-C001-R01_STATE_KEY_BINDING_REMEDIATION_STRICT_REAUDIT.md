# SB-LF03-005-C001-R01 — STATE KEY BINDING REMEDIATION — Strict Re-Audit

Document role: INDEPENDENT CHATGPT STRICT RE-AUDIT

## VERDICT

**CHANGES_REQUIRED**

- BLOCKER: 0
- MAJOR: 1
- MINOR: 0

## Audited chain

- C001 implementation retained
- R01 implementation: `a31f52caffbe2e38622dd872ca569acd04a68c5a`
- R01 terminal builder-log publication: `24af28755bfc0b74f022f46f205061f5f28ed6a9`
- R01 master publication: `3d886d4f46eb239bd880fe70b1bef5d3ba4d3c29`
- canonical gameplay authority independently remains `Sekiph82/Scrubbots@1144704e6c3647ed1cf76c610be5bd675585734a`

## Independent finding

## MAJOR-001 — The unbound memoization API remains accepted

R01 added `StateKeyResult.validate_for_state()` and updated the evidence collector to call `memo.observe(state, result)`, which is correct.

However `DeterministicVisitedMemo.observe()` still explicitly accepts a bare `StateKeyResult` with no state argument. In that path `state is None`, so `validate_for_state()` is skipped and the old unbound result can still create FIRST_VISIT/MEMO_HIT entries.

The retained focused tests continue to call `memo.observe(key_result(...))` and expect success, proving the bypass is part of the public contract rather than dead code.

Therefore the R01 mission “bind every opaque canonical key result back to the exact state supplied to key(state)” is not fully closed.

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

Remove or fail-close the bare StateKeyResult observation path. Production/public memo observation must require the exact queried CompactSolverState plus its StateKeyResult. Migrate tests/callers. UNAVAILABLE/ERROR results must also be state-bound when observed. Add a regression proving bare/unbound observation cannot mutate memo counts.
