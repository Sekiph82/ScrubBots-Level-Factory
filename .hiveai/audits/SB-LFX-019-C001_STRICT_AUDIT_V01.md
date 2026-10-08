# SB-LFX-019-C001 — ChatGPT Strict Audit V01

Date: 2026-10-08  
Repository: `Sekiph82/ScrubBots-Level-Factory`  
Audited implementation: `51c7db12a4629c67d233d3acd57867c6b22fcfe7`  
Builder evidence publications:
- `a4999766db8b9dd83696e7c541f690e4992b80f6`
- `62b62eccf4e7ba019eb0cec44f5117a3dee412ce`

Builder log:
`.hiveai/codex-logs/SB-LFX-019-C001_TRANSPARENT_VOID_END_TO_END_CODEX_LOG.md`

Criteria:
`.hiveai/audit-criteria/SB-LFX-019-C001_TRANSPARENT_VOID_END_TO_END_AUDIT_CRITERIA.md`

## VERDICT

**CHANGES_REQUIRED / R01**

The core transparent-artwork -> VOID implementation is directionally correct and is retained.

R01 is required only to close missing permanent end-to-end fixture coverage, owner-authentic artwork evidence, and the incomplete broad regression.

Do not redesign the accepted VOID architecture.

## A — Game capability authority: PASS / RETAIN

Accepted:

- exact current `Sekiph82/Scrubbots:main` was resolved from canonical origin;
- audited game VOID commit `7d0d148b8609ec04852fdee02f6b8ef37598c616` remained an ancestor of current game main;
- LF gate positively verifies:
  - legacy V1 authority;
  - `FORMAT_VERSION_VOID == 2`;
  - `VOID_CELL == -1`;
  - ADR-030;
  - D1;
  - D2;
- configured game authority must be clean and equal exact `origin/main`;
- no implicit Desktop-game fallback is permitted;
- absent/incompatible game authority fails closed.

The gate implementation in `void_capability.py` is accepted.

## B — Import / QA: PASS / RETAIN

Accepted source behavior:

- RGBA PNG decoding supports binary alpha;
- alpha 0 becomes logical `VOID`;
- alpha 255 remains canonical C-ID artwork;
- alpha 1..254 rejects;
- used-color counting excludes VOID;
- all-VOID artwork rejects;
- TRANSPARENT intent is required when VOID exists;
- owner-upload source bytes remain immutable;
- closed game capability gate returns UNAVAILABLE and no candidate output.

The 32x32 unit fixture with 550 transparent pixels proves the basic alpha/artwork/color-count contract.

## C — Solver / supply core: PASS / RETAIN

Accepted source behavior:

- solver bridge constructs native game V2 LevelData with `-1` cells;
- it invokes the real current-game `LevelLoader`;
- it invokes `ProductionLevelValidator`;
- each candidate plan is loaded through the real `SupplyPlanLoader`;
- VOID starts through the game's own LevelData/ProofState semantics, not a fake color-0 + manual-cleared workaround;
- official game solver/replay is authoritative;
- official `LevelDifficultyAnalyzerV1` is used for VOID levels;
- supply accounting is over non-VOID artwork;
- 3/4/5 columns are exercised by the transparent 32x32 integration fixture;
- corridor screening parity is checked against the current game trace.

The generated 32x32 fixture reached READY for 3, 4 and 5 columns with SOLVED, replay WIN, Difficulty V1 and current-game loader evidence.

## D — Export / identity / publish: PASS in source, retain

Independent source inspection confirms:

- exporter emits V2 iff VOID is present;
- VOID cells remain `-1`;
- V1 remains V1 when VOID is absent;
- `artworkCellCount` and `voidCellCount` are emitted only for VOID content;
- `game_publisher.py` rejects non-canonical V1/V2 VOID encodings;
- TRANSPARENT / VOID publication is capability-gated;
- VOID requires TRANSPARENT source intent;
- scrubpack solver identity binds artwork/VOID counts into the canonical solver-state identity for VOID levels;
- V1 identity schema remains legacy-shaped without VOID count fields;
- content-pipeline packaging revalidates the exact packaged V2 cells and count identity.

No separate VOID difficulty fiction was introduced.

## E — Preview: PASS / RETAIN

Factory Studio artwork preview now places alpha-transparent artwork over BG01 `#202533`, matching the owner/game D1 presentation contract.

This is presentation only; logical VOID truth remains in the canonical grid.

## F01 — BLOCKING: required permanent fixture matrix is incomplete end-to-end

Audit criteria require permanent fixtures for:

- ring;
- enclosed hole;
- border-touching VOID;
- VOID-only row/column;
- legal corridor/reachability;
- plus accepted transparent fixtures exporting/loading/replaying WIN and producing official Difficulty V1 evidence.

Current permanent tests do not satisfy that matrix.

What exists:

- unit screening test covers a small ring/sealed-hole/corridor connectivity shape;
- current-game integration covers a corridor differential;
- one generated 32x32 transparent upload goes through the complete production pipeline.

What is missing:

- no permanent end-to-end ring fixture proving export -> current-game LevelLoader + ProductionLevelValidator + SupplyPlanLoader -> solver/replay WIN -> Difficulty V1;
- no equivalent enclosed-hole end-to-end fixture;
- no equivalent explicit border-touching fixture;
- no equivalent VOID-only row/column fixture.

Screening-only assertions are not equivalent to the required production/load/replay/difficulty proof.

R01 must add the missing parameterized current-game end-to-end fixtures without weakening the existing screening parity tests.

## F02 — BLOCKING: owner-real 32x32 artwork evidence was not used

The prompt/criteria requested the owner's real 32x32 transparent sprite case, approximately 550 transparent pixels.

The builder explicitly records:

> the end-to-end test therefore uses a clearly labeled generated 32x32 fixture, not owner-authored evidence

The generated fixture is useful and should remain as deterministic regression, but it does not satisfy the owner-real evidence requirement.

R01 must:

1. inspect the owner-local Level Factory workspace read-only for an actual owner/Claude-created 32x32 binary-alpha transparent PNG, prioritizing the real level-art set and an orange-fox style fixture if present;
2. never modify, normalize, overwrite or commit that owner source without explicit authorization;
3. run the exact source bytes through owner upload -> validation -> pipeline for 3, 4 and 5 columns;
4. require READY, SOLVED, replay WIN, Difficulty V1 and current-game loader evidence;
5. record source path, SHA-256, dimensions, transparent count, artwork count and the three column results in the builder log;
6. preserve the source bytes exactly.

If no owner-authentic qualifying file exists in the authorized owner workspace, STOP with:

`OWNER_TRANSPARENT_32X32_FIXTURE_REQUIRED`

Do not relabel a synthetic fixture as owner-real.

The deterministic generated fixture remains valid permanent test coverage, but not owner evidence.

## H01 — BLOCKING: full repository regression is incomplete

Audit criteria require a safe full LF suite.

Builder evidence says the broad run:

- reached 78%;
- had already emitted multiple `F` markers;
- entered `factory_studio_action_integration_suite.gd`;
- stalled/restarted that runtime suite;
- was manually interrupted;
- produced no final traceback summary.

After interruption, a changed Studio script parse error was discovered and fixed.

However the full repository suite was **not rerun to completion after that fix**.

Therefore the unknown earlier `F` markers cannot be classified as fixed, unrelated or environment-only.

Task-specific focused passes are valuable but cannot replace this gate.

## H02 — action-integration hang must be classified, not skipped

The builder later deselected the long real Studio preview/action integration case.

That is acceptable for a focused diagnostic command, but not sufficient for final full-regression closure.

R01 must execute the exact action-integration case separately and establish one of:

1. it passes current HEAD under a bounded correct environment; or
2. current changes caused the hang and R01 fixes it without weakening the test; or
3. the identical case demonstrably hangs/fails at the pre-VOID base under the same environment, in which case record exact base-vs-head evidence and obtain a complete all-other-tests green run.

Do not mark the test xfail/skip or weaken assertions merely to obtain green output.

## I — regression items retained

Retain:

- focused C001 suite;
- current-game corridor parity;
- generated 32x32 3/4/5 regression;
- opaque identity/offline regression;
- Godot editor parse scan;
- compileall;
- diff check;
- no TASKS builder edit;
- no audit builder edit.

R01 must add missing fixture and final regression evidence rather than rewrite the implementation.

## R01 required outcome

R01 closes only:

1. ring/hole/border/row-column full current-game production fixture matrix;
2. owner-authentic 32x32 transparent artwork live evidence at 3/4/5 columns;
3. full regression completion and action-integration hang classification/repair;
4. any narrowly discovered regression from those checks.

If all close:

`PASS / CLOSED`

Then advance to:

`SB-LFX-018-C001 — Simple Owner UI`

## FINAL

**CHANGES_REQUIRED / R01**
