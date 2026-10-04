# SB-CP00-005-C001 - Versioned Auditable Release State - Audit Criteria

## PASS rule

PASS only if publish/promotion/rollback control-plane state is versioned, deterministic, append-only, replayable, and invalid transitions fail closed.

## A. State machine
Require explicit legal transitions, no draft-to-production bypass, environment consistency, stale-state rejection.

## B. Audit history
Require immutable/versioned events, deterministic replay, duplicate/tamper/order detection, and no history deletion.

## C. Rollback
Rollback must be a new event referencing known prior content. It must not erase history.

## D. Determinism
No hidden wall-clock/random state in core transition semantics.

## E. Architecture preservation
No provider/network mutation, credentials, runtime/game imports, reverse dependency, or second tracker.

## F. Regression
Require focused SB-CP00-005 PASS, prior SB-CP00-001..004 PASS, governance PASS, full pytest PASS except truthful skips, compileall PASS, diff check PASS.