# SB-CP00-004-C001 - Separate Staging and Production - Audit Criteria

## PASS rule

PASS only if staging and production are mechanically distinct, versioned local control-plane targets and accidental cross-environment state/content use fails closed.

## A. Distinct targets
Require distinct staging/production environment, state, and content identities. Alias/collision must reject.

## B. Promotion boundary
Production must require explicit promotion intent. Staging artifacts cannot silently become production.

## C. Determinism
Environment/target serialization and reasoned validation outcomes must be deterministic and versioned.

## D. Security preservation
No provider network mutation, credentials, runtime/game import, reverse dependency, executable remote content, or second tracker.

## E. Regression
Require focused SB-CP00-004 PASS, prior SB-CP00-001..003 PASS, governance PASS, full pytest PASS except truthful pre-capability skips, compileall PASS, and git diff --check PASS.

Codex must not edit root `TASKS.md` or audit files.