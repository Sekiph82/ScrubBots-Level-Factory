# SB-LF03-004-C001 - Deterministic Baseline Search

Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`

## Mission

Implement only:

`SB-LF03-004 - Implement deterministic baseline search when semantics available.`

Create before product edits:

`.hiveai/codex-logs/SB-LF03-004-C001_DETERMINISTIC_BASELINE_SEARCH_CODEX_LOG.md`

Do not edit `TASKS.md`.

Read the accepted SB-LF03-001..003 contracts, the SB-LF03-004 audit criteria, and current `Sekiph82/Scrubbots` ProofState/ProofKernel/SolvabilitySolver authority.

## Implementation

Add a dedicated generic baseline search layer.

Requirements:
- versioned deterministic algorithm policy;
- consume legal moves only through SB-LF03-003 provider contract;
- consume child-state/completion truth only through a canonical simulation/transition provider boundary;
- deterministic branch order;
- no gameplay-rule derivation in Factory Python;
- no WFC coupling;
- explicit UNAVAILABLE when production canonical transition execution is not safely available.

A test-only graph provider is allowed for algorithm correctness.

Do not copy `ProofState.legal_action_columns()`, `ProofKernel.apply_placement()`, or main-game reachability/routing logic.

Do not claim production SOLVED/UNSOLVABLE from fixture providers.

## Required tests

Prove:
- deterministic repeat;
- branching search can find an alternate successful branch;
- zero-move terminal behavior is provider-defined, not guessed;
- malformed/duplicate/provider-error paths fail closed;
- production adapter remains unavailable without canonical execution;
- state/request inputs do not mutate;
- no search behavior depends on wall-clock ordering.

Run focused tests, retained LF03 tests, full pytest, compileall, Godot headless boot, diff-check and TASKS no-diff.

Publish implementation, tests/docs, task log, then terminal log-only commit. Stop only for this task when executed standalone.
