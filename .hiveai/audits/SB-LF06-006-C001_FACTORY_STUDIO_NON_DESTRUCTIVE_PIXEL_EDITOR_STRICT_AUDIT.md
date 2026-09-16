# SB-LF06-006-C001 — Factory Studio Non-Destructive Pixel Editor — Strict Audit

Document role: INDEPENDENT CHATGPT STRICT AUDIT

## Verdict

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Severity summary:
- BLOCKER: 0
- MAJOR: 1
- MINOR: 0

## Audited builder chain

- Starting HEAD: `b3928898b683903b2ff6c368bad452905fe616de`
- Implementation commit: `81c501f2adf5e4c23e01d84e3a8fe5ca53c4ee9d`
- Terminal builder publication: `81dc1f7de7b20a1c2f4ea256e0ecb2ce7c7411d2`
- Terminal publication is log-only.

## Accepted implementation retained

The C001 implementation establishes the intended non-destructive editor architecture and most acceptance gates correctly:

- real successful canonical `<output_path>/artwork.png` is the only edit source;
- source pixels are duplicated into an in-memory working image;
- the editor never opens canonical bundle files for write;
- source action/candidate/bundle/artwork identity and source SHA-256 are presented separately from working-buffer state;
- only `C01..C16` are paintable; `BG01`, unknown colors and out-of-bounds cells are rejected;
- the Studio palette mapping is guarded against Python `CANONICAL_PALETTE`;
- one logical artwork pixel is one editable logical cell;
- rectangular 20x21 runtime evidence is present;
- integer nearest-neighbor presentation is used;
- failed actions do not erase a dirty working buffer;
- later successful Reproduce does not silently replace a dirty Generate-bound editor source;
- explicit reset restores source pixels;
- explicit clean load can switch to the latest successful Reproduce source;
- preview/evidence/editor/action truth remains separated;
- edited state remains explicitly `UNVALIDATED — revalidation pending SB-LF06-008`;
- no persistence, revision history, revalidation, owner acceptance, production promotion, provider, solver/difficulty, Dashboard, Import, Library, Content Platform or main-game scope was added;
- root `TASKS.md` was not modified by the builder.

The committed real Godot integration checks actual source and working pixels, exact one-cell mutation, untouched-cell equality, source-byte immutability, invalid paint rejection, dirty-buffer retention, reset and explicit source switching.

Builder-reported verification is substantial: focused LF06-006 `5 passed`, retained focused regressions `96 passed`, full regression `712 passed`, compileall green, Godot headless boot green, and committed real LF06-003..006 integration green. These executions were not independently rerun in this audit environment; committed source/test semantics and GitHub topology were independently inspected.

## MAJOR finding

### F-SB-LF06-006-MAJOR-001 — Editor state can remain DIRTY when the working buffer exactly matches the immutable source

The authoritative editor state contract is semantic:

- `CLEAN` means the working buffer equals the immutable canonical source;
- `DIRTY` means one or more logical cells differ from source.

Current `paint_cell()` sets `_state = DIRTY` after every effective pixel write. It does not re-evaluate whether that write restored the last differing cell to its source color.

Concrete reproducible sequence:

1. load a canonical source -> `CLEAN`, dirty count `0`;
2. paint one cell to another canonical color -> `DIRTY`, dirty count `1`;
3. paint that same cell back to its original source color -> `_dirty_cell_count()` becomes `0`, but `_state` remains `DIRTY`.

The UI can therefore truthfully calculate `dirty cells=0` while simultaneously displaying `DIRTY EDIT != CANONICAL SOURCE`. `working_buffer_differs` also becomes `false` while state remains `DIRTY`.

This violates the prompt's requirements that editor state and dirty-cell evidence remain truthful and that `CLEAN` represent equality with source. It is also an operator-truth defect because downstream revalidation UX will rely on whether a manual edit actually differs from source.

The current runtime suite does not cover this reversal path. It tests a no-op paint while already DIRTY and tests `Reset to source`, but not painting the last dirty cell back to its source value.

### Required remediation

Retain the accepted editor architecture. In a bounded R01:

1. after every successful effective paint, derive editor state from actual source-vs-working equality / dirty-cell count rather than setting `DIRTY` unconditionally;
2. if the last differing cell is restored to the source value, state must become `CLEAN`, dirty count `0`, and `working_buffer_differs=false`;
3. if any differing cells remain, state remains `DIRTY` with the exact count;
4. preserve the existing clean no-op behavior and invalid-paint rejection;
5. add real Godot runtime regression that paints one cell away from source and then paints it back using the source cell's canonical palette color, proving automatic `CLEAN` recovery without using Reset;
6. prove source bytes/hash, canonical preview and evidence remain unchanged throughout;
7. preserve all accepted C001 boundaries and do not broaden into persistence, revalidation or revision-history work.

## Publication / scope finding

No publication defect found. `81c501f... -> 81dc1f7...` changes only the builder log. No additional remediation is required for publication discipline.

## Closure decision

`SB-LF06-006` remains open. Do not start `SB-LF06-007` until the bounded R01 editor-state reconciliation remediation passes independent audit.
