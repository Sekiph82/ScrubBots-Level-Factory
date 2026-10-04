# SB-CP00-006-C001 - Secret Handling, No Credentials in Git - Audit Criteria

## PASS rule

PASS only if Content Pipeline models/config/evidence can reference secrets without storing or serializing secret values, with environment separation and repository guards.

## A. Secret references
Only opaque, non-secret references are modeled. No raw credential value field.

## B. Evidence safety
Plans/reports/events/log-safe serialization cannot expose secret material. Redaction behavior deterministic.

## C. Environment scope
Staging and production secret references cannot be silently interchanged.

## D. Repository guard
Focused static checks catch obvious committed credential/private-key material without relying on regex as sole security authority.

## E. Architecture preservation
No live secret manager access, network/provider mutation, runtime/game imports, reverse dependency, or second tracker.

## F. Regression
Require focused SB-CP00-006 PASS, prior SB-CP00-001..005 PASS, governance PASS, full pytest PASS except truthful skips, compileall PASS, diff check PASS.