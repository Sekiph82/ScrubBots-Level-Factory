# SB-LF06-011-C001 — Exact Reproduce by Recorded Seed / Config — Strict Audit Criteria

Document role: INDEPENDENT CHATGPT AUDIT CRITERIA

Target requirement:

`SB-LF06-011 — Reproduce candidate by seed/config. [PARTIAL]`

## 1. Purpose

Close the Studio-side reproduction requirement without inventing a second reproduction engine.

Canonical Python already owns reproduction. The accepted CLI reads the source bundle, reconstructs the exact recorded `metadata.generation.request` including typed seed and complete versioned generation config, regenerates through the canonical router, reuses the recorded quality policy, requires exact logical-grid agreement, rebuilds the bundle, and byte-compares canonical artifacts.

LF06-011 must prove Factory Studio Reproduce is truthfully bound to that recorded metadata authority rather than to whatever values happen to be visible in current draft controls.

## 2. Severity model

### BLOCKER
Automatic FAIL if any of the following occurs:
- Studio Reproduce derives reproduction from current draft controls instead of recorded successful metadata;
- current draft seed/config/presentation label can alter the reproduction of an already generated source candidate;
- Reproduce accepts a logical-grid or canonical-bundle mismatch as MATCH;
- manual editor working pixels are used as canonical Reproduce input;
- a second reproduction algorithm/compiler is implemented in GDScript;
- candidate presentation label is used as candidate identity;
- source canonical bundle is mutated in place;
- root `TASKS.md` is modified by the builder.

### MAJOR
Examples:
- Reproduce reports SUCCESS/MATCH but candidate ID, grid hash, typed seed, mode or dimensions disagree with the recorded source;
- reproduction metadata request differs from the source recorded generation request;
- source/reproduction artifact byte identity is not proven where canonical CLI promises it;
- after a new successful Generate B, Studio still reproduces older A without an explicit A selection contract;
- only static tests exist and no real Studio→canonical Python Reproduce integration proves draft independence;
- Reproduce becomes available before a successful canonical source metadata path exists.

### MINOR
Examples:
- correct reproduction identity with a narrow missing presentation assertion;
- a diagnostic omits a useful recorded-request field while canonical equality remains proven.

## 3. Canonical source authority

Reproduce authority is the last successful canonical source metadata path retained by the existing action gateway.

The canonical Python path must continue to:
- require a valid candidate `metadata.json` bundle;
- reconstruct the exact recorded generation request;
- preserve typed seed semantics;
- preserve recorded dimensions, difficulty, generator mode, style/theme/palette/options as present in the canonical request contract;
- regenerate through the canonical router;
- compare exact logical grid/hash;
- reuse exact recorded quality policy/report;
- require rebuilt canonical artifact identity;
- return MATCH only on exact reproduction.

Do not reimplement these semantics in Godot.

## 4. Critical Studio runtime scenario

PASS eligibility requires one committed real Godot integration using the actual Studio scene and canonical local Python bridge.

Minimum sequence:

1. Before any successful Generate, prove Reproduce is UNAVAILABLE/disabled.
2. Configure a deterministic source request A using a deliberate seed and non-default legal draft values where practical, including a rectangular board.
3. Generate canonical A successfully.
4. Capture:
   - A candidate ID;
   - A grid hash;
   - A selected typed seed representation;
   - A mode and dimensions;
   - A output/metadata path;
   - source `metadata.generation.request`;
   - source canonical artifact bytes/hashes.
5. Confirm Reproduce becomes available only because successful A metadata exists.
6. Change current draft controls substantially **without Generate**: seed, dimensions, difficulty, mode and candidate presentation label where practical.
7. Prove those draft-only changes do not change the retained reproduction source metadata identity.
8. Invoke real Studio Reproduce.
9. Prove returned action is `Reproduce`, state SUCCESS and disposition MATCH.
10. Prove reproduced candidate ID, grid hash, selected seed, mode and dimensions match canonical source A.
11. Prove reproduction `metadata.generation.request` equals A's recorded request exactly and does not contain the changed draft values.
12. Prove canonical artifact bytes are byte-identical between source A and reproduction for every artifact governed by the canonical reproduce contract (`metadata.json`, `artwork.json`, `artwork.png`, and preview when present).
13. Prove source A bytes remain unchanged.
14. Prove candidate presentation label never becomes canonical identity or reproduce input.

## 5. Latest-success source transition

The runtime suite must also prove source transition behavior:

1. Generate a distinct canonical B after A.
2. Confirm the gateway's retained successful metadata source moves to B.
3. Change current draft again without Generate.
4. Invoke Reproduce.
5. Prove Reproduce now matches B, not A and not the current draft.

No historical-source picker is required in this task. Without an explicit selection contract, Studio Reproduce follows the existing last-successful metadata authority.

## 6. Failed/unavailable action retention

After successful B exists, invoke a dependency-gated unavailable action such as Validate/Solve/Analyze.

Prove:
- latest action attempt is UNAVAILABLE;
- retained successful metadata source remains B;
- subsequent Reproduce still matches B;
- unavailable action does not redirect reproduction source.

## 7. Manual editor independence

Reproduce remains canonical-bundle reproduction, not manual-working-copy reproduction.

If a DIRTY editor is included in the scenario:
- its pixels must not enter the canonical Reproduce request;
- Reproduce may update canonical preview/evidence/latest-success surfaces per accepted contracts;
- DIRTY editor replacement remains explicit under LF06-006/LF06-010.

This task need not repeat all LF06-010 truth-separation cases if retained tests already prove them.

## 8. Fail-closed canonical mismatch retention

Do not weaken existing canonical CLI mismatch behavior.

Static/retained tests must continue to prove that unsupported/malformed source metadata, request mismatch, grid mismatch, quality-policy/report mismatch or rebuilt bundle mismatch cannot be reported as MATCH.

A new corruption framework is not required if accepted canonical tests already cover these cases. Reuse historical M09 evidence rather than duplicating the whole CLI test matrix.

## 9. Required tests

PASS requires:
- real Godot Studio Generate A → mutate draft → Reproduce A MATCH;
- exact recorded request equality source vs reproduction;
- byte-level canonical artifact equality;
- source bytes unchanged;
- Reproduce unavailable before source success;
- Generate B → mutate draft → Reproduce B MATCH;
- unavailable action does not destroy B reproduction source;
- candidate presentation remains presentation-only;
- retained canonical reproduce mismatch tests remain green;
- LF06-003..010 regressions remain green.

Static guards should ensure:
- `_reproduce_arguments()` uses retained metadata path, not draft fields;
- candidate presentation is absent from Reproduce process arguments;
- no GDScript reproduction algorithm exists;
- no manual editor working-grid data is passed to canonical Reproduce.

## 10. Scope limits

Do not implement:
- arbitrary historical candidate browser/selector;
- manual seed/config override for Reproduce;
- second canonical request parser in Godot;
- M03 solver;
- M04 Difficulty V1;
- M05 unified validation;
- persistence/revision history;
- owner acceptance or production promotion;
- SB-LF06-012+;
- SB-LFX work;
- Content Platform or main-game work.

Canonical Python Core semantics should normally remain unchanged. If an actual canonical reproduce defect is discovered, stop expansion and document it rather than silently redesigning Core under this Studio task.

## 11. Builder evidence expected

Record:
- focused LF06-011 tests;
- real committed Godot reproduction integration;
- retained LF06-003..010 regressions;
- relevant canonical CLI reproduce/output tests;
- full pytest;
- compileall;
- Godot headless boot;
- `git diff --check`;
- `git diff -- TASKS.md` empty;
- exact changed-file review;
- exactly one terminal builder-log-only publication commit.

## PASS closure rule

`SB-LF06-011` may close when real Studio runtime evidence proves Reproduce is determined by the exact recorded successful seed/config metadata and canonical bundle, remains independent of current draft/manual presentation state, follows the existing last-successful metadata source transition, and returns MATCH only for exact canonical reproduction.
