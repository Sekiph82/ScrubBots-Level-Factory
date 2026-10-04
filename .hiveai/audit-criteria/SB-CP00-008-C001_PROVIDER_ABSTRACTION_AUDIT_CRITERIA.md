# SB-CP00-008-C001 - Provider Abstraction - Audit Criteria

## PASS rule

PASS only if core control-plane logic depends on a provider-neutral, capability-driven interface with no concrete network/vendor provider implementation.

## A. Provider neutrality
No vendor SDK/network dependency or provider-specific core semantics.

## B. Capability model
Explicit versioned capabilities. Unsupported required capability fails before mutation.

## C. Read/plan vs mutation separation
Dry-run/read-only planning cannot require or invoke a mutating implementation.

## D. Error contract
Provider-neutral deterministic result/error categories; no secret leakage.

## E. Architecture preservation
No live mutation, credentials, runtime/game imports, reverse dependency, or second tracker.

## F. Regression
Require focused SB-CP00-008 PASS, prior SB-CP00-001..007 PASS, governance PASS, full pytest PASS except truthful skips, compileall PASS, diff check PASS.