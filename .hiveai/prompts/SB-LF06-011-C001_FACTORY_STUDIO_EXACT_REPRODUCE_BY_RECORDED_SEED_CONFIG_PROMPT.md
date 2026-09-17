# SB-LF06-011-C001 — Factory Studio Exact Reproduce by Recorded Seed / Config

Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`
Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Mission

Work only on:

`SB-LF06-011 — Reproduce candidate by seed/config. [PARTIAL]`

This is primarily a Studio integration / regression-closure task. Canonical Python already owns exact reproduction. Do not write a second reproduction engine.

Create/finalize builder log:

`.hiveai/codex-logs/SB-LF06-011-C001_FACTORY_STUDIO_EXACT_REPRODUCE_BY_RECORDED_SEED_CONFIG_CODEX_LOG.md`

Do not modify root `TASKS.md`.

## Required reads

Read fully before edits:
- root `TASKS.md`;
- `.hiveai/audits/SB-LF06-010-C001_FACTORY_STUDIO_EDITOR_PRESENTATION_TRUTH_SEPARATION_STRICT_AUDIT.md`;
- `.hiveai/audit-criteria/SB-LF06-011-C001_EXACT_REPRODUCE_BY_RECORDED_SEED_CONFIG_AUDIT_CRITERIA.md`;
- accepted LF06-003 Reproduce bridge prompt/audit;
- accepted LF06-010 truth-separation implementation/test;
- `level_factory/scripts/factory_core_gateway.gd`;
- `level_factory/scripts/factory_core_launcher.py`;
- `level_factory/scripts/factory_studio_target_controls.gd`;
- canonical CLI `src/scrubbots_pixel_factory/cli/main.py` reproduce path;
- retained M08/M09 output/reproduce tests and audits.

## 1. Preserve canonical reproduction authority

The canonical Python CLI already:
- reads a valid candidate bundle from `metadata.json`;
- reconstructs the exact recorded `metadata.generation.request`;
- preserves typed seed and full versioned config;
- regenerates through the canonical router;
- requires exact logical grid/hash equality;
- reconstructs exact recorded quality policy/report;
- rebuilds the canonical export bundle;
- returns MATCH only when canonical artifact bytes match.

Do not duplicate or reinterpret these semantics in GDScript.

## 2. Studio Reproduce source authority

Keep the existing Studio contract:
- Reproduce is unavailable before a successful Generate establishes a metadata source;
- the gateway retains the last successful `metadata.json` path;
- Reproduce arguments come from that retained metadata path plus governed output location;
- current draft controls are not reproduction inputs.

Do not add a historical candidate picker or raw manual seed/config override in this task.

## 3. Required real Studio runtime integration

Add a committed Godot integration suite dedicated to LF06-011, or extend a suitable suite if that remains clearer and bounded.

Use the real Studio scene and canonical local Python bridge.

### Source A

1. Confirm Reproduce is disabled/UNAVAILABLE before successful Generate.
2. Configure a deterministic source A with an explicit seed and legal non-default request values where practical; use a rectangular board.
3. Generate A through the real canonical bridge.
4. Capture A:
   - candidate ID;
   - grid hash;
   - selected seed representation;
   - mode;
   - dimensions;
   - output/metadata path;
   - exact `metadata.generation.request`;
   - canonical artifact bytes/hashes.
5. Confirm Reproduce becomes available because A metadata exists.

### Draft divergence

6. Change draft controls without Generate. Change at least seed and dimensions, plus mode/difficulty/presentation label where legal and practical.
7. Prove retained reproduction source metadata still identifies A.
8. Invoke Reproduce.
9. Require action=`Reproduce`, state=`SUCCESS`, disposition=`MATCH`.
10. Prove reproduced candidate ID, grid hash, selected seed, mode and dimensions equal A.
11. Read reproduction metadata and prove `generation.request` equals A's recorded request exactly.
12. Prove changed draft-only values did not leak into reproduced request or identity.
13. Prove canonical source A bytes did not change.
14. Prove reproduction canonical artifacts are byte-identical to A for `metadata.json`, `artwork.json`, `artwork.png`, and preview when present.
15. Prove candidate presentation text is not candidate identity and does not cross the Reproduce process boundary.

### Source B transition

16. Generate a distinct canonical B with a different deterministic source request.
17. Confirm the gateway's retained successful metadata source moves from A to B.
18. Change draft controls again without Generate.
19. Invoke Reproduce.
20. Prove it MATCHes B, not A and not the current draft.
21. Prove B source/reproduction request equality and governed canonical artifact equality.

### Unavailable-action retention

22. With B retained, invoke dependency-gated Validate/Solve/Analyze.
23. Prove the latest action attempt is UNAVAILABLE.
24. Prove the retained successful metadata source remains B.
25. Invoke Reproduce again and prove B still MATCHes.

## 4. Exact request equality

Do not reduce the assertion to seed-only equality.

Compare the complete recorded canonical request object, including as applicable:
- schema/version;
- difficulty;
- width/height;
- typed seed;
- generator mode;
- style;
- theme;
- palette subset;
- generator options namespace/version/values.

The point of LF06-011 is exact seed **and config** reproduction.

## 5. Byte fidelity

For successful source/reproduction pairs, compare exact bytes for canonical artifacts governed by the existing reproduce contract.

Do not create a weaker Studio-only definition of MATCH.

## 6. Static regression guards

Add focused guards proving:
- gateway Reproduce arguments are based on retained metadata path, not `draft_snapshot()` fields;
- candidate presentation is absent from Reproduce arguments;
- editor working-grid data is absent from Reproduce arguments;
- no GDScript canonical-request reconstruction/reproduction algorithm is added;
- existing canonical CLI `_reproduce()` remains the authority.

Static guards do not replace the real Godot integration.

## 7. Retain fail-closed canonical behavior

Run retained canonical M08/M09 reproduce/output tests.

Do not weaken mismatch behavior for malformed metadata, request mismatch, logical-grid mismatch, quality mismatch or byte mismatch.

Historical M09 already contains accepted reproduction-fidelity evidence; reuse it rather than rebuilding the whole CLI acceptance matrix.

## 8. Preserve previous Studio truth separation

LF06-010 must remain green:
- draft remains presentation-only;
- canonical preview/evidence follow successful action bundles;
- DIRTY editor remains independent;
- Reproduce does not consume manual working pixels;
- unavailable actions do not erase retained success.

You do not need to repeat every LF06-010 scenario if its committed regression suite remains green.

## 9. Forbidden scope

Do not:
- redesign canonical Python reproduce semantics;
- create a second request parser or reproduction compiler in Godot;
- add arbitrary historical candidate browsing/selection;
- add persistence/revision history;
- add manual-edit export/save;
- implement M03/M04/M05;
- start SB-LF06-012+;
- start any SB-LFX task;
- modify Content Platform/main-game repositories;
- modify root `TASKS.md`.

If a genuine canonical Python reproduce defect is discovered, document it clearly and keep any remediation narrowly bounded. Do not silently expand scope.

## 10. Verification

Run and record:
- focused LF06-011 tests;
- committed real LF06-011 Godot integration;
- retained LF06-003..010 Studio regressions;
- relevant canonical M08/M09 reproduce/output tests;
- full `python -m pytest -q`;
- compileall;
- `godot --headless --path level_factory --quit`;
- `git diff --check`;
- `git diff -- TASKS.md` must be empty;
- exact changed-file/scope review.

Record failed iterations and corrections honestly.

## Acceptance criteria

PASS eligibility requires:
- Reproduce unavailable before a successful canonical source exists;
- Generate A → mutate current draft → Reproduce still exactly MATCHes recorded A seed/config;
- exact full request equality source A vs reproduction A;
- exact canonical artifact byte fidelity;
- Generate B moves retained reproduction source to B;
- later draft mutation does not alter B reproduction;
- unavailable action does not redirect or destroy retained B reproduce source;
- candidate presentation/manual editor state does not become reproduce input;
- canonical source bundles remain immutable;
- prior LF06 contracts remain green;
- root `TASKS.md` untouched;
- exactly one terminal builder-log-only publication commit follows implementation.

## Publication

Push implementation/tests/finalized builder log to `main`.

At completion give only:
1. full GitHub URL of `.hiveai/codex-logs/SB-LF06-011-C001_FACTORY_STUDIO_EXACT_REPRODUCE_BY_RECORDED_SEED_CONFIG_CODEX_LOG.md`;
2. final implementation commit SHA;
3. terminal log-only publication commit SHA.

Then stop for independent ChatGPT strict audit.
