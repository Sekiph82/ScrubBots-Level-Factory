# SB-LFX-018-C001-R02-R05-R09-R02-R04-R02 — Owner Windows Evidence Review + Batch Authority Audit V01

**2026-10-13. Owner screenshot inspection with independent source review. Verdict: R04-R01 visible DATA/POOL recovery confirmed; REPLAY UX FAIL, SUPPLY UX FAIL, responsive geometry FAIL. New R04-R02 OPEN.**

## Screens supplied

Owner screenshot of original 002 frog selected in Level Factory shows right Details: `Columns: 4`, `Solver: READY`, `Replay: WIN`, `Difficulty V1: MEDIUM`, `Pipeline: READY`, `Review: IN_RELEASE_POOL`. Owner's Release Pool screenshot independently shows `READY levels: 1`, `Visible: 1`, `Selected: 1` and frog thumbnail. This fulfills earlier owner's visual *one-item pool* check without proving game publication or complete CPX-002.

Supply screenshot shows 4 columns, 51 batches, three-row preview depth, 736 total pixels/robots, and actual FIFO color quantities. Real data now exists, previous `{}` no longer shown. BUT a very tall gray modal extends past bottom of Windows client and doesn't provide the requested useful bounded scroll. Therefore functionality/data recovered but presentation **FAIL**.

Three Replay Preview screenshots show legitimate `TRACE-ONLY · REPLAY_VISUAL_STATES_NOT_AVAILABLE · WIN · 51 steps` linked to real 002 restored run; however summary labels and first step and Previous/Next occupy overlapping tiny top-left area of a gray modal, rendering replay human-unusable. Data route works; actual controls/display fail visual acceptance. No native replay animation asserted.

Owner's last screenshot has white pen outlines of visibly empty left/right/bottom window bands around the currently centered scaled Studio. This is not empty game-world space. Independently read `level_factory/scripts/factory_studio_exact_ui.gd`: `_REFERENCE_SIZE = Vector2(1536,1024)`; `responsive_geometry()` computes uniform `min(width/1536,height/1024)` and centers the content. At a real desktop ~1536x875 client this predicts the large left/right letterbox. The app must reflow to fill usable client, retain actual Windows chrome.

Owner asks direct override: hide `Source:` SHA only in right Details; max five paired-fact rows; then 2 buttons horizontal Replay/Supply, then 3 buttons horizontal Solve Again/Accept/Reject, then one scrollable embedded results zone to lower right edge, no popups for these two functions. Existing three production screens maintained.

## Batch: previous decision independently confirmed

Older `docs/HEADLESS_BATCH_PIPELINE.md`/P3 already support sequential headless imported PNG processing via canonical stage route; `factory_studio_batch_import.gd` supports multi-import but does NOT by itself run entire LF solve. Owner original earlier requirement included 40–150 PNG sequential solver, fail continuation, no final level number consumed on fail, durable Resume, READY to Release Pool. New direct owner reaffirms automatic column mix **3=45%, 4=40%, 5=15%**. Latest `docs/product/FACTORY_STUDIO_OWNER_WORKFLOW_V04.md` and `docs/product/FACTORY_STUDIO_MASTER_CONTROL_BINDINGS_V02.md` explicitly make genuine READY candidates automatically eligible for Release Pool; unlike older P3 review-queue-only behavior, no owner ACCEPT required, although no cloud publication is allowed.

## Implementation handoff

One master `.hiveai/prompts/SB-LFX-018-C001-R02-R05-R09-R02-R04-R02_FULL_WINDOW_DETAILS_INLINE_RESULTS_AND_SEQUENTIAL_BATCH_MASTER_PROMPT.md`; criteria `.hiveai/audit-criteria/SB-LFX-018-C001-R02-R05-R09-R02-R04-R02_STRICT_AUDIT_CRITERIA.md`; new direct authority `docs/decisions/OWNER_FACTORY_STUDIO_LEVEL_FACTORY_COMPACT_BATCH_20261013_V01.md`. All components to be implemented in one batch, without new native solves by Codex. R04-R01 remains **CONDITIONAL NARROW TECH PASS**, now visual pool check confirmed; R04-R02/new UX and batch automation is OPEN. CPX-002 shipping and R05 full regression remain OPEN.
