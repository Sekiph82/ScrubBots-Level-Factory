# SB-CP00-002-C001-R01 — Current Production Contract Binding — Audit Criteria

## PASS rule

PASS only if the existing fail-closed content boundary is preserved and all remotely eligible declarative families are truthfully bound to current Level Factory / Scrubbots payload authorities.

## A. Current contract binding

Require:
- supply plan identity matches current `scrubbots.level_supply_plan.v1`;
- publisher metadata identity matches current `scrubbots.level.metadata.v1`;
- LevelData identity represents actual Level Data Spec Version 1 semantics without pretending the payload carries a nonexistent embedded schema string.

## B. Cross-authority regressions

Require tests proving:
- current LevelData V1 output descriptor accepted;
- current SupplyExporter supply descriptor accepted;
- current publisher metadata descriptor accepted;
- obsolete/synthetic mismatched identities rejected;
- authority drift fails loudly.

Task-local examples alone are insufficient.

## C. Security preservation

Retain all prior PASS behavior:
- allow-list/fail-closed;
- path safety;
- executable/script/plugin/binary rejection;
- no payload execution/import;
- no network or remote mutation;
- no provider implementation;
- no credentials;
- no runtime/game imports;
- no reverse dependency;
- no second tracker.

## D. Regression

Require:
- focused R01 tests PASS;
- original SB-CP00-002 tests PASS;
- SB-CP00-001 tests PASS;
- governance/tracker tests PASS;
- full pytest PASS except truthful pre-capability skips;
- compileall PASS;
- git diff --check PASS.

Codex must not edit root `TASKS.md` or audit files.
