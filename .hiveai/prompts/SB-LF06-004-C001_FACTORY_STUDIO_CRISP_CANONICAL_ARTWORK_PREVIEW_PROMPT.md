# SB-LF06-004-C001 — Factory Studio Crisp Canonical Artwork Preview
Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`
Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Mission

Implement only:

`SB-LF06-004 — Crisp board/art preview.`

The accepted Studio shell, target controls and canonical action bridge from `SB-LF06-001..003` must be retained.

This cycle adds a **presentation-only crisp visual preview of real canonical artwork artifacts** produced by successful Generate/Reproduce actions.

The preview must consume canonical output truth. It must not regenerate artwork, infer cells from the draft, create a second board compiler, or invent preview content.

Do not begin `SB-LF06-005+`, any `SB-LFX-*` extension, M03/M04/M05, Dashboard operations, Import, Library, providers, Content Platform or main-game work.

## Required reads before edits

Read completely from GitHub:

1. root `TASKS.md`;
2. this prompt;
3. `.hiveai/audits/SB-LF06-003-C001-R01_CORE_AVAILABILITY_ERROR_AND_RESULT_TRUTH_REMEDIATION_STRICT_AUDIT.md`;
4. accepted current Factory Studio shell/workspace/target/action scripts;
5. `level_factory/tests/factory_studio_runtime_suite.gd`;
6. `level_factory/tests/factory_studio_action_integration_suite.gd`;
7. focused LF06-001/002/003 Python tests;
8. `src/scrubbots_pixel_factory/output/artwork.py`;
9. `src/scrubbots_pixel_factory/output/png.py`;
10. `src/scrubbots_pixel_factory/output/bundle.py`;
11. current `level_factory/README.md`, directory boundaries and LF00 clean-checkout tests.

Before product edits create:

`.hiveai/codex-logs/SB-LF06-004-C001_FACTORY_STUDIO_CRISP_CANONICAL_ARTWORK_PREVIEW_CODEX_LOG.md`

Do not edit root `TASKS.md`.

## 1. Canonical preview source

A successful canonical candidate bundle already contains:

- `artwork.json`;
- `metadata.json`;
- `artwork.png`.

The canonical Python output contract defines `artwork.png` as the exact logical image: **one RGB image pixel per logical artwork cell**, encoded directly from canonical C01..C16 cells with no scaling/interpolation.

An optional `artwork.preview.png` exists only when canonical export is explicitly asked for a preview scale. The current Studio Generate bridge does not request that optional artifact.

For this cycle:

- use the successful action result's canonical `output_path`;
- derive the visual source only as `<output_path>/artwork.png`;
- do **not** modify canonical Generate/Reproduce semantics merely to request `artwork.preview.png`;
- do **not** reconstruct artwork from draft controls, candidate presentation label, difficulty, palette guesses, metadata fields, or GDScript generation logic.

`artwork.png` remains authoritative content. Any enlargement is presentation-only and in-memory.

## 2. Preview component

Prefer a small dedicated presentation component, conceptually something like:

`level_factory/scripts/factory_studio_art_preview.gd`

Exact naming/layout may differ if repository conventions justify it.

The preview must have clear states such as:

- `EMPTY` / no successful canonical artwork yet;
- `READY` / canonical artwork loaded;
- `ERROR` / successful action evidence exists but its visual artifact cannot be safely loaded.

The component must expose enough deterministic snapshot state for runtime tests, for example:

- preview state;
- source action (`Generate` / `Reproduce`);
- canonical candidate ID;
- canonical source bundle path;
- exact `artwork.png` path;
- logical width/height obtained from the loaded canonical image;
- integer presentation scale;
- displayed width/height;
- whether the currently shown preview is the latest successful preview or retained prior-success evidence after a later action failure.

This snapshot is presentation evidence only, not a new canonical record.

## 3. Crisp pixel rendering contract

The preview must remain pixel-crisp.

Required behavior:

- no bilinear/trilinear filtering;
- no antialiasing;
- no color averaging;
- no fractional presentation resampling that changes logical color blocks;
- preserve source aspect ratio exactly;
- rectangular boards must display correctly;
- source logical pixels must remain visually discrete square blocks.

Preferred deterministic rendering strategy:

1. load the real canonical `artwork.png` as an `Image` using a project-boundary-safe API compatible with the existing LF00 clean-checkout prohibition on literal `load(`/`preload(` in tracked Godot runtime source;
2. choose a deterministic **integer** presentation scale;
3. duplicate/resize in memory using Godot nearest-neighbor interpolation only;
4. create a presentation texture from that in-memory image;
5. set the display control's texture filter to nearest as an additional guard.

A suitable bounded scale policy is:

- maximum preview edge: 512 presentation pixels;
- maximum scale: 16x;
- `scale = max(1, min(16, floor(512 / max(logical_width, logical_height))))`.

Equivalent deterministic integer scaling is acceptable if it keeps 59x59 supported and proves no fractional interpolation.

Do not write the enlarged presentation image back into the canonical bundle.

## 4. Generate and Reproduce behavior

### Successful Generate

After a real canonical Generate succeeds:

- preview the exact `<Generate output_path>/artwork.png`;
- associate it with the canonical candidate ID from Core evidence;
- do not use `candidate_presentation` as identity;
- show dimensions based on the loaded canonical image, not merely the draft values;
- keep action result evidence and preview state distinct.

### Successful Reproduce

After a canonical Reproduce succeeds with `MATCH`:

- update the preview to the reproduced bundle's own `<Reproduce output_path>/artwork.png`;
- do not keep pointing at the original Generate file while claiming the reproduction output is shown;
- verify in tests that the reproduction preview pixels are identical to the canonical Generate artwork for the deterministic MATCH case.

## 5. Failure and retention behavior

A later FAILED or UNAVAILABLE action must not silently destroy the last successful preview.

If a successful preview already exists and a later action fails:

- retain the last successful preview;
- keep the current action failure visible in the existing action-result area;
- clearly label the preview as retained last-success evidence rather than current failed-action output.

If a new successful action points to missing/corrupt/unreadable `artwork.png`:

- preview state must become `ERROR` for that attempted preview;
- do not fabricate a board from draft values;
- do not silently substitute a different artifact while claiming it belongs to the new success;
- if a prior successful visual remains displayed for operator continuity, it must be explicitly labeled stale/retained rather than current.

Do not turn a preview-load failure into a false canonical Generate/Reproduce failure. Action truth and preview-presentation truth remain separate.

## 6. UI scope

Place the preview on the existing Generate surface in a clear presentation area near the action result.

At minimum show:

- the crisp artwork image;
- preview state;
- canonical candidate ID for the shown artifact;
- logical dimensions;
- source action and/or artifact path sufficient to identify what is being displayed.

Do not implement in this cycle:

- solver path visualization;
- difficulty/load/risk metrics;
- palette analytics;
- QA dashboards;
- provenance panels beyond minimal source identification;
- pan/zoom/editor paint tools;
- manual import;
- library selection;
- comparison UI;
- owner approval controls.

Those belong to later tasks.

## 7. Truth separation

The preview is a view over canonical files, never a new truth store.

Do not:

- parse `artwork.json` and reserialize a competing artwork model merely for preview;
- mutate canonical bundle files;
- rewrite `metadata.json`;
- change action result evidence;
- infer acceptance/owner approval from the ability to display an image;
- mark preview READY from draft inputs alone.

`QA PASS != OWNER ACCEPT` remains unchanged.

## 8. Project boundary and offline rules

The preview reads only local governed Factory output artifacts.

No:

- provider/network access;
- HTTP;
- credentials/API keys;
- sibling repository dependency;
- absolute owner-specific Windows path;
- temporary helper dependency;
- generated artifact committed to Git.

Respect the existing clean-checkout runtime-source contract that forbids literal `load(` and `preload(` markers in tracked `level_factory` Godot runtime files. Use a boundary-compatible image-loading method such as `Image.load_from_file(...)` or an equally safe repository-native approach.

## 9. Required runtime tests

Extend/add committed Godot runtime evidence proving at minimum:

1. existing LF06-001/002 runtime contract remains green;
2. existing LF06-003 real action integration remains green;
3. before any success, preview is EMPTY/truthful and no fabricated texture is shown;
4. real deterministic Generate creates a READY preview sourced exactly from `<output_path>/artwork.png`;
5. source logical dimensions are correct for an independent rectangular case such as 20x21;
6. presentation scale is an integer and deterministic;
7. display dimensions equal logical dimensions multiplied by that integer scale;
8. nearest-neighbor pixel integrity is real: for the integration artwork, displayed blocks correspond exactly to source logical pixels with no blended/foreign colors;
9. a later deterministic failed action retains and labels the prior successful preview;
10. real Reproduce MATCH updates preview source to the reproduction output bundle;
11. reproduced preview pixels equal Generate artwork pixels for the MATCH case;
12. candidate presentation label is not used as canonical preview identity;
13. missing/corrupt canonical artwork produces truthful preview ERROR/no-fabrication behavior;
14. generated test outputs are cleaned after the run.

Do not satisfy crispness only with grep assertions. At least one Godot runtime test must inspect the real loaded/display image or texture pixels.

## 10. Required Python/static regression protection

Add narrow Python assertions protecting:

- preview component existence and project locality;
- no provider/network path;
- nearest/integer scaling contract markers;
- preview source is canonical `artwork.png` beneath action `output_path`;
- no candidate-presentation identity forwarding;
- no canonical Python Core duplication;
- no `load(`/`preload(` clean-checkout contract regression.

Do not make Python-only tests fabricate acceptance instead of the required real Godot pixel test.

## 11. Required regression and verification

Run and record at minimum:

1. focused LF06-004 tests;
2. LF06-001/002/003 focused regressions;
3. committed Factory Studio runtime suite;
4. committed real Studio/Core action integration suite with preview assertions;
5. deterministic Generate -> preview -> failed action -> retained preview -> Reproduce MATCH -> reproduced preview sequence;
6. LF01 rectangular/dimension tests;
7. relevant canonical output/PNG round-trip tests;
8. full `python -m pytest -q`;
9. `python -m compileall -q src tests level_factory/scripts/factory_core_launcher.py`;
10. `godot --headless --path level_factory --quit`;
11. `git diff --check`;
12. changed-file review proving root `TASKS.md`, canonical Python Core semantics, providers, solver/difficulty implementation, Dashboard, Import, Library, Content Platform, main-game and `SB-LF06-005+` are untouched.

Record failed commands and corrections truthfully.

## 12. Allowed scope

Allowed only as needed:

- `level_factory/scenes/**` if a committed scene change is genuinely useful;
- `level_factory/scripts/factory_studio_*` presentation scripts;
- one dedicated preview presentation script if appropriate;
- `level_factory/tests/**`;
- narrow LF06-004 Python tests;
- narrow Studio docs describing the preview contract;
- matching builder log.

Avoid changing `factory_core_gateway.gd` unless a tiny presentation-result handoff is absolutely necessary. Do not change canonical Python generator/output semantics.

Do not modify root `TASKS.md`.

## 13. Acceptance criteria

PASS eligibility requires all of the following:

- [ ] preview is sourced only from real canonical successful bundle `artwork.png`;
- [ ] no preview is fabricated from draft state;
- [ ] rectangular artwork displays with exact aspect ratio;
- [ ] logical source pixels are presented using deterministic integer nearest-neighbor scaling;
- [ ] no blended/foreign-color pixels are introduced by presentation scaling;
- [ ] 59x59 remains within bounded preview policy;
- [ ] successful Generate updates preview from Generate bundle;
- [ ] successful Reproduce MATCH updates preview from Reproduce bundle;
- [ ] Generate/Reproduce MATCH previews are pixel-identical for the deterministic integration case;
- [ ] candidate presentation label is not canonical preview identity;
- [ ] later FAILED/UNAVAILABLE action does not silently erase last successful preview;
- [ ] retained preview is labeled truthfully after failure;
- [ ] missing/corrupt artwork fails preview truthfully without fabricating content;
- [ ] action truth and preview truth remain separate;
- [ ] no metrics/editor/import/library/provider scope creep;
- [ ] existing action gates and canonical Core authority remain intact;
- [ ] committed Godot pixel-level integration evidence passes;
- [ ] prior LF06/LF01/full regression passes;
- [ ] root `TASKS.md` unchanged by builder;
- [ ] finalized builder log is published truthfully using implementation/equality/log-only discipline;
- [ ] builder stops for independent ChatGPT strict audit.

## 14. Publication discipline

Use the accepted non-self-referential pattern:

1. implementation commit(s);
2. push and record final implementation equality checkpoint;
3. one final log-only publication commit;
4. hand the actual final publication SHA externally.

Do not create a post-final equality-log commit.

## GitHub handoff

Push implementation/tests/finalized builder log to `main`.

At completion give the user only:

1. full GitHub URL of the finalized builder log;
2. final implementation commit SHA;
3. actual final publication commit SHA.

Then stop for independent ChatGPT strict audit.
