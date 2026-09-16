# SB-LF06-005-C001 — Factory Studio Canonical Evidence / Metrics Panel
Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`
Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Mission

Implement only:

`SB-LF06-005 — Display solution/difficulty/load/risk/art QA metrics/provenance.`

The accepted Studio shell, target controls, canonical action bridge and crisp canonical artwork preview from `SB-LF06-001..004` must remain intact.

This cycle adds a **read-only evidence/metrics presentation panel** sourced from the real successful canonical candidate bundle.

The critical rule is truthfulness:

- show canonical evidence that actually exists;
- show `UNAVAILABLE` / `NOT YET CANONICAL` where the governing capability does not yet exist;
- never derive gameplay solution, Difficulty V1, load, risk, owner approval, or semantic recognizability from unrelated structural/art metrics;
- never invent placeholders that look like real numeric results.

Do not begin `SB-LF06-006+`, any `SB-LFX-*` task, M03/M04/M05 implementation, Dashboard operations, Import, Library, providers, Content Platform or main-game work.

## Required reads before edits

Read completely from GitHub:

1. root `TASKS.md`;
2. this prompt;
3. `.hiveai/audits/SB-LF06-004-C001_FACTORY_STUDIO_CRISP_CANONICAL_ARTWORK_PREVIEW_STRICT_AUDIT.md`;
4. accepted Factory Studio shell/workspace/target/action/preview scripts;
5. `level_factory/tests/factory_studio_runtime_suite.gd`;
6. `level_factory/tests/factory_studio_action_integration_suite.gd`;
7. focused LF06-001..004 Python tests;
8. `src/scrubbots_pixel_factory/output/bundle.py`;
9. `src/scrubbots_pixel_factory/quality/core.py`;
10. `src/scrubbots_pixel_factory/core/request.py`;
11. `src/scrubbots_pixel_factory/core/result.py`;
12. current `level_factory/README.md`, directory boundaries and clean-checkout tests.

Before product edits create:

`.hiveai/codex-logs/SB-LF06-005-C001_FACTORY_STUDIO_CANONICAL_EVIDENCE_METRICS_PANEL_CODEX_LOG.md`

Do not edit root `TASKS.md`.

## 1. Canonical evidence source

A successful canonical Generate/Reproduce bundle contains `metadata.json` bound to the same canonical artwork/result.

For this Studio cycle:

- use the successful action result's canonical `output_path`;
- derive evidence source only as `<output_path>/metadata.json`;
- treat that file as read-only canonical evidence;
- do not recompute quality metrics in GDScript;
- do not reconstruct GenerationRequest/GenerationResult classes in GDScript;
- do not create a second schema validator or second quality engine;
- do not rewrite metadata or copy it into another persistent truth store.

The Studio may parse the canonical JSON for presentation and may perform narrow consistency checks needed to avoid showing obviously mismatched evidence.

## 2. Dedicated evidence panel

Prefer a small dedicated presentation component, conceptually:

`level_factory/scripts/factory_studio_evidence_panel.gd`

Exact naming/layout may vary if repository conventions justify it.

Expose clear presentation states:

- `EMPTY` — no successful canonical bundle evidence loaded yet;
- `READY` — supported canonical metadata loaded and displayed;
- `ERROR` — a successful action exists but its metadata cannot be safely/readably presented;
- retained/stale labeling when a prior successful panel remains after a later action failure or after a newer successful bundle has unreadable/mismatched metadata.

Expose deterministic snapshot state for runtime tests, including at minimum:

- panel state;
- source action;
- source bundle path;
- metadata path;
- canonical candidate ID;
- canonical grid hash;
- logical dimensions;
- generation mode;
- generator ID/version where present;
- request schema/version where present;
- quality schema/version;
- canonical structural quality decision and rejection codes;
- selected structural/art QA metrics actually present in canonical metadata;
- explicit solution/difficulty/load/risk availability dispositions;
- whether displayed evidence is retained last-success evidence.

Snapshot state is presentation evidence only, not a second canonical record.

## 3. Evidence categories and semantic labels

### 3.1 Solution

Current canonical repository has no authoritative gameplay solver from M03.

Display:

`Solution: UNAVAILABLE — gameplay solver pending M03.`

Do not use WFC as gameplay Solve.
Do not infer solvability from successful generation, structural quality, region counts, or Reproduce MATCH.
Do not fabricate move count/path/depth/branching/dead ends.

### 3.2 Difficulty

Current canonical repository has no accepted solver-derived Difficulty V1 result from M04.

Display:

`Difficulty analysis: UNAVAILABLE — Difficulty Intelligence pending M04.`

The generation request's `difficulty` field may be displayed only as **request/target context**, clearly labeled as such. It must never be presented as computed/validated difficulty evidence.

Do not derive difficulty from:

- dimensions;
- color count;
- structural quality metrics;
- generator mode;
- entropy/symmetry/checkerboard values.

### 3.3 Load / risk

No canonical gameplay load/risk model is accepted yet.

Display those categories as unavailable/not-yet-canonical.

Do not invent numeric load, frustration, retention, risk, deadlock, bait, slot pressure, or dependency metrics.

### 3.4 Art / structural QA

Canonical `metadata.json` already includes the exported `quality` binding and versioned structural quality report.

Display only real canonical fields, clearly labeled **Structural / Art QA evidence**, for example where present:

- quality decision `ACCEPT` / `REJECT`;
- rejection codes;
- quality schema/version;
- quality policy version;
- used colors;
- occupied ratio;
- occupied component count;
- isolated occupied count;
- tiny region count / tiny region cell count;
- largest occupied region dominance;
- largest color dominance;
- edge-touch ratio;
- horizontal/vertical/aggregate symmetry;
- color entropy;
- checkerboard score;
- negative-space ratio.

You do not need to display every metric above if the UI would become noisy. Choose a stable, useful subset and keep complete raw canonical evidence retrievable through snapshot state if practical.

These values are **structural quality evidence**, not gameplay difficulty and not owner acceptance.

Always preserve the semantic distinction:

`Structural QA ACCEPT != OWNER ACCEPT`

Do not claim semantic recognizability from structural metrics.

### 3.5 Provenance / identity

Display real canonical evidence where present, such as:

- candidate ID;
- grid hash;
- logical dimensions;
- generator mode;
- generator ID/version;
- selected seed/typed seed;
- request schema/version;
- generator-options namespace/version;
- source bundle path;
- metadata path;
- generator provenance fields already recorded by canonical Core.

Do not create a new provenance format.

## 4. Narrow consistency checks

Because this is a presentation reader, do not duplicate the Python bundle validator.

However, before showing a new bundle as READY, perform narrow consistency checks against the successful action evidence where practical:

- metadata candidate ID equals action-result candidate ID;
- metadata artwork grid hash equals action-result grid hash;
- metadata artwork width/height agree with the canonical successful action dimensions/evidence;
- source remains beneath governed Factory output;
- expected canonical metadata schema/version is recognized.

If a newer successful action points to unreadable JSON, unsupported schema/version, missing required presentation evidence, or clear identity mismatch:

- panel becomes `ERROR` for the attempted new evidence;
- do not fabricate metrics/provenance from action draft values;
- do not overwrite/erase the prior successful evidence snapshot;
- if prior evidence remains visible, label it retained/stale;
- do not convert the canonical action itself into FAILED.

Cross-language tests must guard any schema/version/key assumptions used by Studio against the canonical Python constants/serialization.

## 5. Generate / Reproduce behavior

### Successful Generate

After real Generate success:

- load `<Generate output_path>/metadata.json`;
- panel becomes READY only from canonical metadata;
- source action is Generate;
- art QA/provenance values reflect that bundle;
- solution/difficulty/load/risk unavailable dispositions remain explicit.

### Successful Reproduce MATCH

After canonical Reproduce MATCH:

- load the reproduction bundle's own `metadata.json`;
- panel source action becomes Reproduce;
- source path changes to the reproduction bundle;
- candidate/grid identity remains MATCH-consistent;
- do not continue pointing at original Generate metadata while claiming reproduction evidence is displayed.

## 6. Failure and retention behavior

A later FAILED/UNAVAILABLE action must not silently erase last successful evidence panel state.

Retain prior successful panel evidence and visibly mark it as retained last-success evidence.

If the current successful action's metadata cannot be shown safely, panel state must truthfully indicate ERROR for the attempted newer evidence while preserving the previous successful evidence separately/visibly where available.

Current action result, preview state and evidence-panel state are three distinct presentation truths.

## 7. UI scope

Place the evidence panel on the existing Generate surface near Action result / Canonical artwork preview.

At minimum expose clearly separated sections for:

- Identity / provenance;
- Structural / Art QA;
- Solution;
- Difficulty;
- Load / risk.

The last three sections must visibly state unavailable where canonical evidence is absent.

Do not implement:

- solution path visualization;
- solver execution;
- difficulty computation;
- mutation/automatic targeting;
- manual paint/edit tools;
- owner approval workflow;
- Dashboard;
- Import/Library;
- comparison UI;
- provider cost/accounting;
- Content Platform.

## 8. Truth separation

The panel is a view over canonical metadata, never a new truth store.

Do not:

- write or mutate `metadata.json`;
- persist a second evidence database/index;
- recompute structural quality in GDScript;
- interpret `request.difficulty` as measured difficulty;
- map quality metrics into difficulty/load/risk scores;
- infer solver disposition;
- infer owner acceptance;
- mark QA ACCEPT as publication/production acceptance.

`QA PASS != OWNER ACCEPT` remains locked.

## 9. Project boundary / offline rules

Evidence reading is local-only under governed Factory output.

No:

- provider/network access;
- HTTP;
- credentials/API keys;
- sibling repository dependency;
- owner-specific absolute path;
- temporary helper dependency;
- generated metadata/evidence committed to Git.

Respect existing tracked-runtime clean-checkout rules, including the literal `load(`/`preload(` prohibition in tracked Godot runtime source.

## 10. Required Godot runtime evidence

Extend committed runtime/integration evidence proving at minimum:

1. LF06-001..004 retained behavior remains green;
2. before success, evidence panel is EMPTY and does not fabricate values;
3. real Generate yields READY panel from exactly `<Generate output_path>/metadata.json`;
4. candidate ID, grid hash and dimensions agree with canonical action evidence;
5. panel displays real canonical structural quality decision/version plus selected real structural metrics;
6. request `difficulty` is labeled only as target/request context, not measured difficulty;
7. Solution is visibly UNAVAILABLE pending M03;
8. Difficulty analysis is visibly UNAVAILABLE pending M04;
9. Load/risk are visibly UNAVAILABLE/not-yet-canonical;
10. later deterministic FAILED action retains and labels prior successful evidence;
11. Reproduce MATCH switches metadata source to reproduction bundle;
12. candidate/grid identity remains consistent after Reproduce MATCH;
13. missing/corrupt/unsupported/mismatched metadata produces truthful panel ERROR/no fabrication;
14. preview remains independent and correct;
15. generated test outputs are cleaned.

Use real canonical Generate/Reproduce integration. Do not satisfy this cycle with grep-only assertions.

## 11. Required Python/static regression protection

Add narrow tests protecting:

- evidence component exists and is project-local;
- metadata source is `<successful output_path>/metadata.json`;
- Studio does not implement quality formulas or solver/difficulty formulas;
- no provider/network path;
- request difficulty is not labeled measured difficulty;
- explicit unavailable solution/difficulty/load/risk semantics;
- structural QA fields used by Studio correspond to real canonical metadata paths;
- schema/version assumptions are cross-checked against canonical Python constants/contracts;
- no clean-checkout `load(`/`preload(` regression;
- no canonical Python Core duplication.

## 12. Required regression / verification

Run and record at minimum:

1. focused LF06-005 tests;
2. LF06-001..004 focused regressions;
3. committed Factory Studio runtime suite;
4. real Studio/Core action integration including preview + evidence panel;
5. Generate -> evidence -> failed action -> retained evidence -> Reproduce MATCH -> reproduced evidence sequence;
6. corrupt/unsupported/mismatched metadata error path;
7. LF01 request/dimension regressions;
8. canonical output/bundle/quality tests;
9. full `python -m pytest -q`;
10. `python -m compileall -q src tests level_factory/scripts/factory_core_launcher.py`;
11. `godot --headless --path level_factory --quit`;
12. `git diff --check`;
13. changed-file review proving root `TASKS.md`, canonical Python Core semantics, providers, solver/difficulty implementation, Dashboard, Import, Library, Content Platform, main-game and SB-LF06-006+ are untouched.

Record failed commands and corrections truthfully.

## 13. Allowed scope

Allowed only as necessary:

- `level_factory/scripts/factory_studio_*` presentation scripts;
- one dedicated evidence/metrics presentation script;
- `level_factory/tests/**`;
- narrow LF06-005 Python tests;
- narrow Studio docs if genuinely needed;
- matching builder log.

Avoid changing `factory_core_gateway.gd`; no new operational Core action is required for this presentation cycle.

Do not change canonical Python generator/request/result/output/quality semantics.
Do not modify root `TASKS.md`.

## 14. Acceptance criteria

PASS eligibility requires all of the following:

- [ ] panel reads only real successful-bundle canonical `metadata.json`;
- [ ] no evidence fabricated from draft state;
- [ ] identity/provenance displayed from canonical evidence;
- [ ] structural/art QA displayed only from canonical quality evidence;
- [ ] structural QA is not relabeled as gameplay difficulty/load/risk;
- [ ] request difficulty is clearly target/request context only;
- [ ] Solution truthfully UNAVAILABLE pending M03;
- [ ] Difficulty analysis truthfully UNAVAILABLE pending M04;
- [ ] load/risk truthfully unavailable where no canonical model exists;
- [ ] no solver/difficulty/load/risk formulas are invented in Studio;
- [ ] `QA PASS != OWNER ACCEPT` remains explicit;
- [ ] Generate loads Generate bundle metadata;
- [ ] Reproduce MATCH loads Reproduce bundle metadata;
- [ ] action/evidence identity consistency is checked;
- [ ] later action failure retains and labels prior successful evidence;
- [ ] malformed/unsupported/mismatched metadata yields panel ERROR/no fabrication;
- [ ] action truth, preview truth and evidence-panel truth stay distinct;
- [ ] existing action/preview behavior remains green;
- [ ] no prohibited scope creep;
- [ ] root `TASKS.md` unchanged by builder;
- [ ] full regression and real Godot integration green;
- [ ] finalized builder log uses implementation/equality/log-only publication discipline;
- [ ] builder stops for independent ChatGPT strict audit.

## 15. Publication discipline

Use the accepted pattern:

1. implementation commit(s);
2. push and record actual final implementation equality checkpoint;
3. one final log-only publication commit;
4. hand the actual terminal publication SHA externally.

Do not create a post-final equality-log commit.

## GitHub handoff

Push implementation/tests/finalized builder log to `main`.

At completion give the user only:

1. full GitHub URL of the finalized builder log;
2. final implementation commit SHA;
3. actual final publication commit SHA.

Then stop for independent ChatGPT strict audit.
