# SB-CP00-003-C001 — Declarative-Only Remote Payload Policy — Audit Criteria

## PASS rule

PASS only if remotely eligible payload bytes/data are validated as strictly declarative, bound to the accepted descriptor, and cannot carry executable/application behavior.

## A. Strict parser

Require:
- UTF-8 JSON only;
- malformed JSON rejected;
- duplicate keys rejected;
- NaN/Infinity rejected;
- deterministic bounded depth/size/string limits;
- no payload execution/import/resource loading.

## B. Type-specific validation

Require current structural validation for:
- LevelData V1;
- `scrubbots.level_supply_plan.v1`;
- `scrubbots.level.metadata.v1`.

Do not duplicate solver/gameplay/Difficulty logic.

## C. Descriptor binding

Require rejection on:
- type/contract/version mismatch;
- level identity mismatch;
- descriptor/payload structural projection mismatch;
- SHA-256 mismatch.

## D. Executable prohibition

Reject executable/script/plugin/addon/native/module/expression/resource smuggling and unknown behavior-bearing fields.

## E. Architecture preservation

Retain:
- no network/provider mutation;
- no credentials;
- no runtime/game imports;
- no reverse dependency;
- no second tracker;
- SB-CP00-002 fail-closed classifier.

## F. Regression

Require:
- focused SB-CP00-003 PASS;
- SB-CP00-002/R01 PASS;
- SB-CP00-001 PASS;
- governance/tracker PASS;
- full pytest PASS except truthful pre-capability skips;
- compileall PASS;
- git diff --check PASS.

Codex must not edit root `TASKS.md` or audit files.
