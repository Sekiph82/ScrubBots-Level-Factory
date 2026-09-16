# SB-LF06-006-C001-R01 — Editor State Reconciliation Remediation

Document role: CODEX REMEDIATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`
Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Mission

Work only on `SB-LF06-006-C001-R01`.

Read first:
- root `TASKS.md`;
- `.hiveai/audits/SB-LF06-006-C001_FACTORY_STUDIO_NON_DESTRUCTIVE_PIXEL_EDITOR_STRICT_AUDIT.md`;
- original `SB-LF06-006-C001` prompt;
- current `factory_studio_art_editor.gd` and LF06 action integration suite.

Create the matching R01 builder log before product edits:

`.hiveai/codex-logs/SB-LF06-006-C001-R01_EDITOR_STATE_RECONCILIATION_REMEDIATION_CODEX_LOG.md`

Retain the accepted C001 architecture. Fix only the editor-state truth defect identified by the strict audit.

## Required fix

The editor state must be derived from actual working-buffer equality with the immutable source:

- `CLEAN` iff the working buffer exactly equals the loaded immutable source;
- `DIRTY` iff one or more logical cells differ from source;
- `dirty_cell_count` must equal the actual number of differing cells;
- `working_buffer_differs` must be equivalent to `dirty_cell_count > 0`.

Current C001 sets `DIRTY` unconditionally after an effective paint. Replace that behavior with bounded reconciliation after successful paint mutation.

Required behavior:

1. load source -> `CLEAN`, dirty count `0`;
2. paint one source cell to a different canonical color -> `DIRTY`, dirty count `1`;
3. paint the same cell back to its exact original source palette color -> automatically return to `CLEAN`, dirty count `0`, `working_buffer_differs=false`, without calling Reset;
4. with multiple dirty cells, restoring only one must keep `DIRTY` and decrement the count truthfully;
5. no-op paint must not create false DIRTY state;
6. invalid/BG01/out-of-bounds operations remain non-mutating;
7. `Reset to source` behavior remains accepted and unchanged.

Do not introduce cached dirty flags that can drift from actual pixels unless they are rigorously derived and cross-checked. Prefer source-vs-working truth.

## Required real Godot regression

Extend the committed LF06 integration with a real pixel path proving:

- capture the original canonical source color for a chosen cell;
- select a different valid canonical color and paint that cell;
- assert `DIRTY`, dirty count `1`, and exact changed RGB;
- paint the cell back using the canonical ID corresponding to its original source RGB;
- assert automatic `CLEAN`, dirty count `0`, `working_buffer_differs=false`;
- assert working image again equals source image pixel-for-pixel;
- assert canonical `artwork.png` bytes/hash remain unchanged;
- assert canonical preview/evidence identity remains unchanged;
- then continue retained C001 scenarios, including dirty-buffer retention across failure/Reproduce and Reset/source-switch behavior.

If the test needs RGB->canonical-ID lookup, keep it bounded to the existing C01..C16 mapping and cross-language guard. Do not add alternate palette semantics.

## Preserve all accepted C001 boundaries

- source is only real successful canonical `artwork.png`;
- source bundle files remain immutable;
- edits remain memory-only;
- only C01..C16 are paintable;
- BG01 remains presentation-only;
- no arbitrary RGB/alpha/interpolation/multi-cell painting;
- rectangular boards remain supported;
- editor remains explicitly UNVALIDATED pending SB-LF06-008;
- newer success does not silently replace a DIRTY editor source;
- action/preview/evidence/editor truths remain separate;
- no persistence, revision history, revalidation, owner acceptance or production promotion;
- no provider/network, solver/difficulty, Dashboard, Import, Library, Content Platform or main-game work;
- no canonical Python Core semantic changes.

## Forbidden scope

Do not start `SB-LF06-007+`.
Do not start any `SB-LFX-*` task.
Do not modify root `TASKS.md`.
Do not add persistence or derived edited artifacts.
Do not implement SB-LF06-008 revalidation.

## Verification

Run and record at minimum:

1. focused LF06-006 R01 tests;
2. retained LF06-001..006 focused regressions;
3. canonical palette regressions;
4. committed real Godot action/editor integration;
5. full `python -m pytest -q`;
6. compileall;
7. `godot --headless --path level_factory --quit`;
8. `git diff --check`;
9. scope review proving root `TASKS.md` and forbidden areas are untouched.

Record failed commands and corrections truthfully.

## Acceptance criteria

PASS eligibility requires:

- [ ] `CLEAN` iff working pixels equal source pixels;
- [ ] `DIRTY` iff at least one working pixel differs;
- [ ] dirty count is exact;
- [ ] painting the last differing cell back to source auto-recovers `CLEAN`;
- [ ] multi-dirty partial restoration retains `DIRTY` with decremented exact count;
- [ ] source bytes/hash remain unchanged;
- [ ] preview/evidence remain canonical and unchanged by working edits;
- [ ] existing C001 behavior and full regressions remain green;
- [ ] no scope creep;
- [ ] root `TASKS.md` unchanged by builder;
- [ ] implementation commit is followed by exactly one terminal log-only publication commit;
- [ ] builder stops for independent ChatGPT strict audit.

## Publication

Use implementation commit(s), push/equality checkpoint, then exactly one final log-only publication commit.

At completion give only:
1. full GitHub URL of finalized R01 builder log;
2. final remediation implementation SHA;
3. actual terminal publication SHA.

Then stop for independent ChatGPT strict audit.
