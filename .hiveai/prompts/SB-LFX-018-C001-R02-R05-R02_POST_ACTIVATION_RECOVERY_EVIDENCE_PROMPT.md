# SB-LFX-018-C001-R02-R05-R02 | Production History Crash Recovery + Remaining-Gate Evidence

**CODEX:** implement only the NEW unmet R05-R01 post-activation recovery boundary in `Sekiph82/ScrubBots-Level-Factory`; record results in the SAME R05 builder log.
**GPT:** independent audit and root TASKS.md lifecycle only.
**Parent:** `.hiveai/audits/SB-LFX-018-C001-R02-R05-R01_DESKTOP_HISTORY_RESUME_STRICT_AUDIT_V01.md`.
**Matching criteria:** `.hiveai/audit-criteria/SB-LFX-018-C001-R02-R05-R02_POST_ACTIVATION_RECOVERY_EVIDENCE_AUDIT_CRITERIA.md`.
**Log:** `.hiveai/codex-logs/SB-LFX-018-C001-R02-R05_PRODUCTION_HISTORY_FULL_REGRESSION_EVIDENCE_CODEX_LOG.md`.

## Owner-locked execution

1. Work **ONLY** in existing `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`; canonical LF `origin/main`. No TEMP/AppData worktrees, clones, archives, duplicate project folders, Godot copy, oversized basetemp, disk-forensics rounds or R2 production mutation.
2. **All 57 owner-untracked paths STAY AS THEY ARE**, including `Release/`, ICO, `level_factory/addons/`, 52 `.gd.uid` and two earlier M17 test scratch directories. No cleanup, delete, move, add, stage, modify, blanket ignore or inventory task. Protect owner local edits with non-destructive Git sync; STOP on real overlap instead of forcibly reconciling.
3. **Reuse all existing builder evidence** without repeating: prior R05-R01 **4 PASS** (three newly added tests plus one directly affected), M17 7/63 and F02 3 PASS, R04 native UI/A-C/2 solver outputs. No rerun of already completed tests, 150 PNG import/solver batch, native screenshot loop, full pytest, LF19, Godot, install or release. No unapproved remote production. For genuinely modified R02 behavior run only NEW targeted in-memory tests once, with `PYTHONDONTWRITEBYTECODE=1`, `-p no:cacheprovider`; do not write further scratch.
4. Code/tests commit first, builder log append-only evidence commit separately, normal safe fast-forward `git push origin HEAD:main`, fetch/parity 0/0. Codex must NEVER edit root TASKS or `.hiveai/audits/**`.

## R02 exact new problem

R01 delivered canonical M13 history read/CAS after the CP03-009 production manifest activation (published commit **`6b68ce456dd174db2c9ac7a9509d60585b5bbf16`**, note prior R05 log incorrectly printed a different full SHA). On a post-activation M13 write/readback failure it correctly reports `ACTIVATED_HISTORY_INCOMPLETE` but a later `_read_production_manifest_history` sees history tip N with live manifest N+1 and blocks every next promotion. No safe repair/recovery path was established; the old fixture manually switched the live object and never executed a complete CP03 publish.

## Single bounded implementation objective

**G1: Design and implement smallest truly safe post-activation history-gap recovery or fail-closed operator reconciliation**, reusing canonical CP03/M11 events, actual M13 history, existing exact current provider manifest and unaltered owner approval/current-game replay authority. Do NOT invent another history store/publisher or blindly synthesize records.

- Inspect the exact existing CP03-008/009, M11 event and M13 record fields to determine which verified immutable records are available after an interrupted M13 history write.
- Accept repair **only** when exact live manifest bytes/hash/version, a matching canonical *verified* activation/release event, exact previous M13 tip, immutable pack identities and scoped owner approval/replay evidence exist; make all outcomes deterministic and require separate explicit owner authorization for any live repair. If these authorities are insufficient, implement a **read-only diagnostic/repair-plan** returning `OPERATOR_AUTHORITY_REQUIRED` rather than forging history.
- Model in small in-memory S3-shaped fixture: (i) N→N+1 activation succeeded, M13 write failed; (ii) exact proof recovered, append missing M13 record via conditional write and readback ONLY if authorized in the fixture; (iii) lost acknowledgment after successful M13 write, retry idempotently resolves; (iv) stale or corrupted event, pack SHA, version, prior tip, missing approval/replay or concurrent update refuses. Do not promote any second real manifest merely to repair first.
- An existing M13 history already at N+1 must succeed only if exact expected bytes/lineage match. Never roll back to N silently or overwrite N+1. Preserve the truthful `mutation_performed=true` status of uncertain post-write conditions until verified.
- If repairs must be deferred to a live/provider-approval stage, still publish any genuinely completed pure validation/diagnostic code with tests and accurately mark `LIVE_RECOVERY_NOT_RUN`.

**G2: Narrow original R05 missing-evidence matrix (read-only)**. Compare existing actual source/log evidence for native Windows `FILE_MODE_OPEN_FILES` chooser, original full-suite hang, prior R04 2/150 solved A/C, final Release installer/screenshots and Alpix. Do not run another test/capture to recreate prior PASS. Record precisely what is **PREVIOUS PASS REUSED**, **SOURCE-ONLY**, **NOT VERIFIED**, **NOT RUN** and **OWNER APPROVAL REQUIRED**; link real evidence only. **148 remaining solver runs are not automatically required or authorized** and are not a reason to run a 148-image batch. No clean full regression claim without a real completed run. Do not falsely close the final R05 milestone.

**G3: Documentation identity correction**. Correct the previously inaccurate *expanded* implementation SHA in the EXISTING R05 builder log to `6b68ce456dd174db2c9ac7a9509d60585b5bbf16`, while preserving original log chronology and explicit correction note. This is log-only, not a reason to redo code/tests.

## Handoff

When bounded R02 work is completed, publish its actual modified code/tests and the updated SINGLE R05 log to LF GitHub `main`. Return the real GitHub log URL and genuinely still-open gates. Stop only the gates that require owner approval, live R2 credentials/production, irreversible install, disk-heavy new regression or unknown provider behavior; do not invent another process or perform unrelated work. GPT will independently audit and update root TASKS.
