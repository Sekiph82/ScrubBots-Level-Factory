# SB-LF06-006-C001 — Factory Studio Non-Destructive Pixel Editor

Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`
Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Mission

Implement only:

`SB-LF06-006 — Owner/designer paint/edit where appropriate.`

Retain the accepted Factory Studio shell, target controls, canonical Generate/Reproduce bridge, crisp canonical artwork preview and canonical evidence panel from `SB-LF06-001..005`.

This cycle adds a **non-destructive logical-pixel editor** for the operator. It edits an in-memory working copy of a real successful canonical `artwork.png` source.

The editor is not canonical truth, is not a validated candidate, is not owner acceptance and must not mutate the canonical source bundle.

Do not begin `SB-LF06-007+`, `SB-LFX-*`, M03/M04/M05 implementation, Dashboard, Import, Library, providers, Content Platform or main-game work.

## Required reads before edits

Read completely from GitHub:

1. root `TASKS.md`;
2. this prompt;
3. `.hiveai/audits/SB-LF06-005-C001-R01_FAIL_CLOSED_METADATA_PRESENTATION_GATE_REMEDIATION_STRICT_AUDIT.md`;
4. accepted current Factory Studio shell/workspace/target/action/preview/evidence scripts;
5. `level_factory/tests/factory_studio_runtime_suite.gd`;
6. `level_factory/tests/factory_studio_action_integration_suite.gd`;
7. focused LF06-001..005 Python tests;
8. `src/scrubbots_pixel_factory/contracts/palette.py`;
9. `data/palette/scrubbots_palette_v2.json`;
10. canonical output/artwork contracts used by the accepted preview;
11. `docs/product/FACTORY_STUDIO_OWNER_OPERATIONS_EXTENSIONS_V01.md`, especially immutable-source and revision-lineage rules;
12. current `level_factory/README.md`, directory boundaries and clean-checkout tests.

Before product edits create:

`.hiveai/codex-logs/SB-LF06-006-C001_FACTORY_STUDIO_NON_DESTRUCTIVE_PIXEL_EDITOR_CODEX_LOG.md`

Do not edit root `TASKS.md`.

## 1. Source-of-truth boundary

The editor may start only from a **real successful canonical artwork source** already known to Studio.

Use the successful action evidence / accepted canonical preview source:

`<successful output_path>/artwork.png`

Required:

- load the real logical image;
- duplicate it into an in-memory editable working image/buffer;
- retain source candidate ID, source action, source bundle path and source artwork path for presentation identity;
- logical width/height come from the loaded source image;
- source bundle files remain read-only.

Forbidden:

- editing `artwork.png` in place;
- editing `artwork.json` or `metadata.json`;
- writing edited pixels back into the successful canonical bundle;
- reconstructing the edit source from draft controls or candidate presentation labels;
- treating an edited working buffer as a canonical GenerationResult or accepted candidate.

The canonical source file bytes must be identical before and after edit operations.

## 2. Editor lifecycle and states

Prefer a dedicated presentation/editor component such as:

`level_factory/scripts/factory_studio_art_editor.gd`

Expose explicit states such as:

- `EMPTY` — no canonical source loaded;
- `CLEAN` — working buffer equals its immutable canonical source;
- `DIRTY` — one or more logical cells differ from source;
- `ERROR` — requested source cannot be safely loaded/presented.

The working buffer is intentionally **UNVALIDATED** in this cycle.

UI and snapshot evidence must say this plainly. A dirty edit must never be shown as QA-passed, owner-accepted, production-ready, canonical, or validated.

Expose deterministic snapshot state sufficient for runtime tests, including at minimum:

- editor state;
- source action;
- source candidate ID;
- source bundle path;
- source artwork path;
- logical width/height;
- selected canonical color ID;
- dirty-cell count;
- explicit validation disposition such as `UNVALIDATED — revalidation pending SB-LF06-008`;
- whether the working buffer differs from source.

This snapshot is presentation/editor state only, never a second canonical record.

## 3. Canonical palette contract

Editing is limited to logical palette IDs `C01..C16`.

`BG01` is presentation/background-only and must never be paintable into a logical cell.

The Studio may carry a small palette presentation mapping only if it is protected by a Python cross-language regression that proves the Studio `C01..C16` ID/RGB or ID/HEX mapping exactly equals current `CANONICAL_PALETTE`.

Do not invent alternate colors, nearest-color snapping, gradients, opacity, alpha painting or arbitrary RGB entry.

Do not silently alter the canonical palette contract.

## 4. Logical-cell editing behavior

One logical artwork pixel equals one logical editable cell.

Required editing API/behavior:

- select one canonical `C01..C16` color;
- paint exactly one logical `(x, y)` cell at a time;
- bounds-check coordinates;
- reject unknown/off-palette/BG01 colors;
- preserve dimensions and aspect ratio;
- preserve full opacity / exact canonical RGB values;
- no interpolation, antialiasing, blending or fractional logical-cell edits;
- rectangular boards remain fully supported;
- 20..59 independent dimension envelope remains unchanged.

A no-op paint to the cell's current source/working value must not create false dirty evidence.

A paint operation must modify only the intended working-buffer logical cell.

## 5. UI interaction

Add a bounded editor area near the existing canonical preview/evidence area.

At minimum provide:

- explicit `Load current canonical artwork` / `Start editing current artwork` action;
- crisp editable board rendering;
- canonical palette selector for `C01..C16`;
- selected color indicator;
- editor state / dirty count / `UNVALIDATED` warning;
- explicit `Reset to source` action.

A mouse click/paint gesture should map deterministically to the intended logical cell. The visual board must use integer nearest-neighbor presentation only.

Do not add freeform image transforms, brushes larger than one logical cell, resize, crop, rotate, fill tools, AI inpaint, semantic regeneration or provider calls in this cycle.

## 6. Reset and action-retention behavior

`Reset to source` must restore the working buffer exactly to the immutable loaded source and return the editor to `CLEAN`.

A later FAILED/UNAVAILABLE Studio action must not silently erase an active edit buffer.

A later successful Generate/Reproduce must also not silently overwrite a `DIRTY` edit buffer. If a newer canonical success exists while edits are dirty, keep the dirty editor bound to its original source until the operator explicitly loads/replaces the editor source.

If the editor is `CLEAN`, explicit loading of the latest successful canonical artwork may replace its source.

The editor's source identity must always remain visible enough to avoid confusing an older dirty edit with a newer preview/action result.

## 7. No persistence or promotion in this cycle

This cycle deliberately does **not** persist edited artwork as a canonical or derived candidate.

Do not create:

- edited `metadata.json`;
- edited `artwork.json` inside a canonical bundle;
- a new accepted candidate;
- owner-review acceptance;
- production promotion;
- persistent revision history;
- undo-history database;
- edit lineage schema;
- revalidation output.

`SB-LF06-008` will own revalidation after manual changes. Owner-approved persistent revision history belongs to `SB-LFX-012`.

An in-memory working buffer and deterministic test snapshots are sufficient for this cycle.

## 8. Truth separation

Maintain all of these as distinct truths:

- current action result;
- canonical artwork preview;
- canonical evidence panel;
- editor working buffer.

A dirty editor must not mutate or relabel the accepted preview/evidence components.

Keep explicit:

- `Structural QA ACCEPT != OWNER ACCEPT`;
- `DIRTY EDIT != VALIDATED CANDIDATE`;
- `DIRTY EDIT != CANONICAL SOURCE`.

Do not infer solution, measured difficulty, load or risk from edits.

## 9. Project/offline boundaries

No:

- provider/network/HTTP access;
- credentials/API keys;
- sibling repository dependency;
- owner-specific absolute paths;
- temporary helper dependency;
- generated edited artifact committed to Git.

Respect the existing project-local runtime contract, including the tracked Godot literal `load(`/`preload(` prohibition.

## 10. Required real Godot runtime evidence

Extend/add committed runtime integration proving at minimum:

1. LF06-001..005 retained behavior remains green;
2. before loading a source, editor is `EMPTY` and cannot fabricate/edit pixels;
3. real deterministic Generate produces the canonical 20x21 integration artwork;
4. explicitly loading that canonical artwork creates a `CLEAN` editor bound to the exact Generate candidate/path/dimensions;
5. editor source pixels equal the real canonical `artwork.png` pixels before edits;
6. source `artwork.png` bytes/hash are captured before edit;
7. selecting a canonical color and painting one known cell changes exactly that working-buffer cell;
8. all untouched working cells remain byte/color-identical to the source logical image;
9. edited cell RGB exactly equals the selected canonical palette RGB;
10. editor becomes `DIRTY`, dirty-cell count is truthful and validation disposition remains `UNVALIDATED`;
11. canonical source `artwork.png` bytes/hash remain unchanged after painting;
12. preview and evidence panel remain bound to unchanged canonical source truth;
13. invalid coordinate, unknown color and `BG01` attempts do not mutate the working buffer;
14. a no-op paint does not create false dirty evidence;
15. a later FAILED action does not erase the dirty edit;
16. a later successful Reproduce does not silently overwrite the existing dirty edit source;
17. `Reset to source` restores exact source pixels and returns editor to `CLEAN`;
18. explicitly loading the current Reproduce source while clean switches editor source correctly;
19. generated integration output is cleaned after the run.

At least one runtime test must inspect actual working-image pixels, not only labels or source strings.

## 11. Required Python/static regression protection

Add narrow tests proving:

- editor component exists and is project-local;
- Studio palette mapping exactly matches Python `CANONICAL_PALETTE` if a mapping is embedded;
- `BG01` is absent from logical paint choices;
- no provider/network path;
- no canonical Python generator/validator/solver duplication;
- source bundle files are never opened for edit/write by editor code;
- editor state is explicitly `UNVALIDATED`;
- no candidate presentation label is used as edit identity;
- no persistence/revision-history scope creep;
- existing clean-checkout resource-loading contract remains green;
- real Godot editor integration is executed by a committed test.

## 12. Verification

Run and record at minimum:

1. focused LF06-006 tests;
2. retained LF06-001..005 focused regressions;
3. LF01 dimension/palette regressions relevant to editor contracts;
4. canonical palette tests;
5. committed Factory Studio runtime suite;
6. real Studio/Core action integration plus editor pixel tests;
7. full `python -m pytest -q`;
8. `python -m compileall -q src tests level_factory/scripts/factory_core_launcher.py`;
9. `godot --headless --path level_factory --quit`;
10. `git diff --check`;
11. changed-file review proving root `TASKS.md`, canonical Python Core semantics, providers, solver/difficulty, Dashboard, Import, Library, Content Platform, main-game, `SB-LF06-007+` and `SB-LFX-*` are untouched.

Record failed commands and corrections truthfully.

## 13. Acceptance criteria

PASS eligibility requires all of the following:

- [ ] editor loads only a real successful canonical `artwork.png` source;
- [ ] canonical source bundle remains byte-for-byte unchanged;
- [ ] editing occurs only in an in-memory working buffer;
- [ ] one logical pixel equals one editable cell;
- [ ] only canonical `C01..C16` may be painted;
- [ ] `BG01`, arbitrary RGB, alpha and interpolation are impossible through the editor contract;
- [ ] palette mapping is cross-language guarded against canonical Python palette truth;
- [ ] rectangular artwork edits correctly;
- [ ] exact one-cell mutation is proven at runtime;
- [ ] dirty count/state are truthful;
- [ ] editor remains explicitly `UNVALIDATED`;
- [ ] failed actions do not erase dirty edits;
- [ ] newer success does not silently replace a dirty editor source;
- [ ] reset restores exact immutable source pixels;
- [ ] action/preview/evidence/editor truths remain separate;
- [ ] no persistence, revision-history, validation, acceptance or promotion scope creep;
- [ ] existing LF06 functionality remains green;
- [ ] root `TASKS.md` unchanged by builder;
- [ ] full regression and real Godot pixel-level integration green;
- [ ] finalized builder log follows implementation/equality/log-only publication discipline;
- [ ] builder stops for independent ChatGPT strict audit.

## 14. Publication discipline

Use the accepted pattern:

1. implementation commit(s);
2. push and record actual final implementation equality checkpoint;
3. exactly one final log-only publication commit;
4. hand the actual terminal publication SHA externally.

Do not create a post-final equality-log commit.

## GitHub handoff

Push implementation/tests/finalized builder log to `main`.

At completion give the user only:

1. full GitHub URL of the finalized builder log;
2. final implementation commit SHA;
3. actual terminal publication commit SHA.

Then stop for independent ChatGPT strict audit.
