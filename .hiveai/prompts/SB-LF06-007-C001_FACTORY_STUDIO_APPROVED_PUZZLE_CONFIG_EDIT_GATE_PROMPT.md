# SB-LF06-007-C001 — Factory Studio Approved Puzzle-Config Edit Gate

Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`
Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Mission

Work only on:

`SB-LF06-007 — Approved puzzle-config edits only.`

Retain all accepted LF06-001..006 behavior. This cycle must not invent gameplay or puzzle semantics.

The repository currently has an authoritative generation-request contract, but that is not automatically the same thing as an authoritative editable gameplay/puzzle-config contract. Treat those domains separately.

Before product edits, inspect the current canonical repository for the authoritative puzzle/level configuration schema and any explicit editability rules. Only fields that are both canonical and explicitly safe/approved for manual Studio editing may become editable.

If no such current authoritative editable puzzle-config fields exist, the correct implementation is a fail-closed Studio surface reporting `UNAVAILABLE — no approved canonical puzzle-config edit contract`, with no mutation capability. Do not repurpose generation request fields merely to make the task look implemented.

Create the matching builder log before product edits:

`.hiveai/codex-logs/SB-LF06-007-C001_FACTORY_STUDIO_APPROVED_PUZZLE_CONFIG_EDIT_GATE_CODEX_LOG.md`

Do not modify root `TASKS.md`.

## Required reads

Read completely:
- root `TASKS.md`;
- `.hiveai/audits/SB-LF06-006-C001-R01_EDITOR_STATE_RECONCILIATION_REMEDIATION_STRICT_AUDIT.md`;
- accepted LF06-001..006 Studio scripts/tests;
- canonical Python request/result/output contracts;
- any canonical LevelData/puzzle/config schemas present in this repository;
- M03/M04/M05 dependency notes relevant to unresolved gameplay semantics;
- `docs/product/FACTORY_STUDIO_OWNER_OPERATIONS_EXTENSIONS_V01.md`;
- current Factory README/governance/boundary tests.

## 1. Mandatory contract discovery gate

Produce code/tests based on repository truth, not assumptions.

Determine whether a current authoritative puzzle-config contract exists and, if so:
- exact schema/version;
- exact editable field names;
- exact allowed values/types/ranges;
- whether changing each field is permitted before solver/revalidation authority exists;
- how edit state is distinguished from canonical/validated truth.

Forbidden substitutions:
- `GenerationRequest` fields are not automatically puzzle-config fields;
- request difficulty is not measured difficulty;
- WFC options are not gameplay solver configuration;
- artwork pixels are not puzzle-config values;
- candidate presentation labels are not canonical IDs.

If the repository does not prove an editable field is approved, keep it non-editable.

## 2. Studio component

Prefer a dedicated component such as:

`level_factory/scripts/factory_studio_puzzle_config_editor.gd`

It must expose explicit state such as:
- `UNAVAILABLE` — no approved canonical editable puzzle-config contract/fields;
- `CLEAN` — approved config loaded and working copy equals source;
- `DIRTY` — one or more approved fields differ;
- `ERROR` — canonical source/config cannot be safely read.

Do not create a second persistent truth store.

## 3. Source and immutability

If editable puzzle-config fields exist:
- load them only from a real successful canonical artifact/config source;
- duplicate approved values into a memory-only working copy;
- never mutate canonical source bundle/config files in place;
- retain source candidate/artifact/config identity;
- preserve exact source bytes throughout manual edits.

If no approved fields exist:
- do not create fake source config;
- do not enable edit controls;
- explain the dependency truthfully in the UI/snapshot.

## 4. Edit contract

For any field actually enabled:
- validate against the authoritative canonical type/range/enum contract;
- reject unsupported keys and values fail-closed;
- derive CLEAN/DIRTY from exact source-vs-working equality;
- expose exact changed-field count/list;
- allow explicit reset to source;
- remain `UNVALIDATED` until later canonical revalidation;
- do not infer solution, measured difficulty, load, risk, owner acceptance or production readiness.

No arbitrary JSON editor, free-form dictionary editor or hidden override map.

## 5. Truth separation

Keep distinct:
- current canonical action result;
- canonical artwork preview;
- canonical evidence panel;
- LF06-006 artwork edit buffer;
- puzzle-config edit buffer/gate.

A dirty artwork edit must not silently become puzzle-config state, and puzzle-config edits must not relabel artwork/evidence truth.

Explicitly preserve:
- `MANUAL CONFIG EDIT != VALIDATED CANDIDATE`;
- `MANUAL CONFIG EDIT != OWNER ACCEPT`;
- `QA PASS != OWNER ACCEPT`.

## 6. Dependency gates

Do not implement or fake:
- gameplay solver semantics from M03;
- measured Difficulty V1 from M04;
- unified validation/revalidation from M05/SB-LF06-008;
- production promotion;
- revision-history persistence;
- main-game runtime behavior.

If an edit cannot be proven safe without one of those dependencies, keep it unavailable.

## 7. Required runtime evidence

Committed Godot tests must prove the applicable branch.

### If approved editable fields exist
Prove:
1. canonical config loads from the real successful source;
2. initial state CLEAN;
3. one approved field edit produces exact DIRTY state;
4. invalid/unknown field/value is rejected;
5. source bytes remain unchanged;
6. restoring the value returns CLEAN automatically;
7. failed/newer actions do not silently erase/replace DIRTY edits;
8. preview/evidence/art editor identities stay unchanged;
9. config editor remains UNVALIDATED;
10. reset restores exact source values.

### If no approved editable fields exist
Prove:
1. component reports UNAVAILABLE truthfully;
2. no controls permit mutation;
3. no fake config is synthesized from GenerationRequest or draft UI;
4. all LF06-001..006 behavior remains green.

## 8. Static/cross-language protection

Add narrow tests proving:
- any embedded schema/enum/range literals exactly match their authoritative Python contract;
- only explicitly approved fields are editable;
- unknown fields fail closed;
- no arbitrary JSON editing;
- no canonical source write path;
- no provider/network dependency;
- no solver/difficulty/validator duplication;
- no persistence/revision-history scope creep;
- root `TASKS.md` unchanged by builder.

## 9. Verification

Run:
- focused LF06-007 tests;
- retained LF06-001..006 tests;
- relevant canonical contract tests;
- committed real Godot integration;
- full `python -m pytest -q`;
- compileall;
- Godot headless boot;
- `git diff --check`;
- changed-file/scope review.

Record all failures and corrections truthfully.

## Acceptance criteria

PASS eligibility requires:
- no puzzle/config semantics invented;
- only authoritative explicitly approved fields editable, or truthful UNAVAILABLE if none exist;
- canonical source remains immutable;
- manual config state is memory-only and UNVALIDATED;
- CLEAN/DIRTY is exact if editing exists;
- no GenerationRequest/puzzle-config conflation;
- no M03/M04/M05 dependency fabrication;
- retained LF06-001..006 green;
- root `TASKS.md` untouched by builder;
- implementation commit followed by exactly one terminal log-only publication commit.

## Publication

Push implementation/tests/finalized builder log to `main`.

At completion give only:
1. finalized builder-log GitHub URL;
2. final implementation commit SHA;
3. actual terminal publication commit SHA.

Then stop for independent ChatGPT strict audit.