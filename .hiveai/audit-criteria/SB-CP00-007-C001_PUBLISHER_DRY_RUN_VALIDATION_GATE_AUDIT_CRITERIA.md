# SB-CP00-007-C001 - Publisher Dry-Run / Validation Gate - Audit Criteria

## PASS rule

PASS only if a deterministic validation-only publication plan is mandatory before any future mutation and current implementation performs zero remote mutation.

## A. Plan evidence
Require versioned plan with target environment, content digests, deterministic operations/checks, expected release state, and approval status.

## B. Preconditions
Reject unvalidated payloads, stale state, hash/environment mismatch, production bypass, and missing required approval.

## C. Zero mutation
Dry-run/CLI must make no mutation call. Canary tests must prove this.

## D. Secret safety
Plans/reports contain references only, never secret values.

## E. Architecture preservation
No live provider/network implementation, runtime/game import, reverse dependency, or second tracker.

## F. Regression
Require focused SB-CP00-007 PASS, prior SB-CP00-001..006 PASS, governance PASS, full pytest PASS except truthful skips, compileall PASS, diff check PASS.