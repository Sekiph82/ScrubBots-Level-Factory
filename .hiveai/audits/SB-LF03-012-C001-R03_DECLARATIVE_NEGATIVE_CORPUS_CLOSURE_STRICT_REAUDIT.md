# SB-LF03-012-C001-R03 — Declarative Negative Corpus Closure — Strict Re-Audit

Document role: INDEPENDENT CHATGPT STRICT RE-AUDIT

## VERDICT

**CHANGES_REQUIRED**

- BLOCKER: 0
- MAJOR: 3
- MINOR: 0

## Audited chain

- R03 implementation: `e5c7be2028c2cb44e407d56daf6b621fe46a5834`
- R03 terminal builder-log commit: `62dc5784abb32ac19a57f2880aae2a1716b579ec`
- R03 master publication: `73aaac9dc2bbbb9476860800157b94336271a8e1`

## Accepted R03 progress

R03 materially improves the corpus:
- the eight former string-only IDs are now versioned declarative objects with payload SHA-256;
- checksum verification exists;
- real canonical bridge regression executes repeated legal_moves/apply_placement/solve;
- exact LevelData source bytes are used by the real bridge fixture;
- full repository suite is green at `856 passed, 1 skipped, 1 warning`.

Those accepted improvements are retained.

## MAJOR-001 — Two declared historical defect fixtures do not execute the historical defect they claim to protect

### Transition authority drift fixture

`LF03_TRANSITION_AUTHORITY_DRIFT_V1` is declared as `transition_authority_drift`.

But the regression test does not run a baseline/search transition that returns a child state under a foreign authority. It instead constructs a `LegalMoveQuery` whose query authority already disagrees with the state and expects query validation to fail.

That protects legal-query authority binding, not the historical SB-LF03-004 defect: an AVAILABLE transition returning a child `CompactSolverState` under a different authority.

### Enumeration binding fixture

`LF03_ENUMERATION_BINDING_V1` is declared as `enumeration_binding`.

But the test creates a `LegalMoveResult` with moves `[1,0]` and expects construction/ordering validation to fail. It does not exercise `SolutionCountEngine` receiving a validly typed move result bound to another query/state, nor an authority-switched child transition.

That protects move-order validation, not the historical SB-LF03-008 enumeration-binding defect.

A regression corpus must make its family labels truthful.

## MAJOR-002 — Timeout corpus protects only timeout-before-result, not the accepted attached-telemetry invariant

`LF03_TIMEOUT_NONCANONICAL_V1` contains only:
- timeout seconds;
- `before_result=true`;
- expected operational INCONCLUSIVE + canonical null.

Its test calls `wrap_operational_execution(None,...)`.

The R03 remediation contract also required the durable corpus to prove:

same completed deterministic result with and without operational timeout telemetry => identical canonical deterministic bytes/digest.

That invariant is covered by the task-specific SB-LF03-011 unit test, but not by the declarative SB-LF03-012 regression corpus that was explicitly tasked with locking the R03 fix.

## MAJOR-003 — Canonical bridge corpus does not itself exercise stale LevelData-source-hash rejection

The real bridge fixture now uses exact LevelData source bytes and a correct SHA, and the task-specific SB-LF03-009 tests exercise stale-hash tampering.

But the R03 SB-LF03-012 contract explicitly required the regression suite itself to prove:
- source hash recomputed from exact bytes;
- one-cell tamper while retaining the stale source hash fails closed;
- valid real operations remain green.

The current SB-LF03-012 real bridge test executes only the valid path. It does not drive a stale-hash mutation from the declarative corpus.

## Regression evidence

The repository is otherwise healthy:
- focused/affected R03 + retained LF03/LF00/LF06: `95 passed, 1 warning`;
- full pytest: `856 passed, 1 skipped, 1 warning`;
- compileall PASS;
- Godot headless PASS;
- real canonical operations PASS;
- TASKS builder diff zero.

The remaining findings are regression-corpus fidelity gaps, not product-runtime blockers.

## FINAL VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

## Required remediation

Keep the accepted R03 corpus structure and add narrowly scoped R04 fixture corrections:

1. `LF03_TRANSITION_AUTHORITY_DRIFT_V1` must declaratively drive a transition provider that returns an AVAILABLE child state under a foreign authority and prove BaselineSearchEngine fails closed.
2. `LF03_ENUMERATION_BINDING_V1` must declaratively drive SolutionCountEngine with a wrong-query/state legal result and/or foreign-authority child transition and prove ERROR, never EXACT/LOWER_BOUND.
3. Extend the timeout declarative fixture so one case wraps a completed deterministic result with operational timeout telemetry and proves canonical bytes/digest remain identical to the unwrapped deterministic result; retain the existing timeout-before-result case.
4. Extend the canonical bridge declarative fixture with a stale-hash LevelData tamper case and prove request/invoke fails closed before gameplay execution.
5. Recompute every modified fixture payload SHA-256 and keep the full repository gate green.
