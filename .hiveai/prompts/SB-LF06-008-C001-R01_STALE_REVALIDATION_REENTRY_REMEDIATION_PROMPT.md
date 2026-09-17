# SB-LF06-008-C001-R01 — Stale Revalidation Re-entry Remediation

Document role: CODEX REMEDIATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`
Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Mission

Work only on:

`SB-LF06-008-C001-R01`

Retain the accepted LF06-008 manual structural revalidation architecture and fix only the stale-result lifecycle defect documented by the strict audit.

Read first:
- root `TASKS.md`;
- `.hiveai/audits/SB-LF06-008-C001_FACTORY_STUDIO_MANUAL_ART_STRUCTURAL_REVALIDATION_STRICT_AUDIT.md`;
- `.hiveai/audit-criteria/SB-LF06-008-C001_MANUAL_ART_STRUCTURAL_REVALIDATION_AUDIT_CRITERIA.md`;
- original LF06-008 prompt;
- current `factory_studio_art_revalidation.gd`;
- current real LF06-008 Godot integration suite.

Create/finalize this builder log:

`.hiveai/codex-logs/SB-LF06-008-C001-R01_STALE_REVALIDATION_REENTRY_REMEDIATION_CODEX_LOG.md`

Do not modify root `TASKS.md`.

## Defect to fix

Current behavior correctly marks an earlier result `STALE` after another pixel edit, but leaves `_result_current=true` internally and disables the Revalidate button because only `AVAILABLE` enables it.

This dead-ends the workflow:

`edit -> revalidate -> edit -> STALE -> cannot revalidate again`

The operator must not be forced to Reset and lose edits just to re-run structural QA.

## Required behavior

Preserve the retained LF06-008 result as stale evidence if useful, but make the current DIRTY grid revalidatable again.

Required lifecycle:

1. CLEAN source -> `NOT_REQUIRED`.
2. First edit -> `AVAILABLE`.
3. First revalidation -> current qualified `STRUCTURAL ACCEPT` or `STRUCTURAL REJECT`.
4. Any later edit that changes the working grid -> prior result becomes `STALE` and not current.
5. While the editor remains DIRTY, the current changed grid must expose an enabled fresh revalidation action without Reset.
6. Second revalidation must call the real canonical Python revalidation bridge again and bind new current evidence to the exact new working-grid hash.
7. If the new grid differs, result B's working hash must differ from result A's.
8. A third edit must be able to stale result B, and another fresh revalidation must still be possible. The lifecycle must be repeatable.
9. Reset to immutable source -> `NOT_REQUIRED` and no current manual-edit result.
10. Returning exactly to an older previously validated dirty grid must not silently resurrect old evidence. Require a fresh canonical revalidation unless the implementation explicitly reruns/rechecks the canonical path.

Implementation options are open as long as truth remains clear. For example:
- STALE may itself permit revalidation; or
- stale evidence may be retained separately while the active state becomes AVAILABLE.

Do not present stale evidence as current.

## Preserve accepted architecture

Do not change unless required by this narrow lifecycle fix:
- canonical `read_bundle()` source authority;
- exact source `QualityPolicy` reuse;
- canonical `evaluate_grid()`;
- canonical `logical_grid_hash()`;
- fixed bounded launcher operation;
- source candidate/source byte binding;
- transient request cleanup;
- immutable source bundle;
- memory-only DIRTY editor;
- explicit `STRUCTURAL ART QA ONLY — NOT FULL GAMEPLAY VALIDATION` scope;
- LF06-003 Validate=UNAVAILABLE;
- M03/M04/M05 limitations;
- LF06-007 puzzle-config gate=UNAVAILABLE.

## Required test remediation

Extend the real committed Godot integration. Do not satisfy this cycle with string/grep-only tests.

Without Reset between the following steps, prove:

1. edit A -> DIRTY;
2. real revalidation -> current result A;
3. edit B -> STALE;
4. stale result A is not current;
5. revalidation action is enabled/available for the current DIRTY grid;
6. invoke real canonical revalidation again;
7. current result B is produced;
8. result B working-grid hash equals the current exact working grid and differs from A when the grid differs;
9. editor remains DIRTY;
10. source `artwork.png`, `artwork.json`, `metadata.json` remain byte-identical;
11. edit C -> result B becomes STALE;
12. prove fresh revalidation is available again and execute it, or otherwise prove repeatable re-entry through the real path;
13. only after that Reset -> `NOT_REQUIRED`.

Retain the existing deliberately bad-grid canonical REJECT evidence.

Add/adjust focused regression assertions so a future implementation cannot restore `STALE` + disabled revalidation deadlock.

## Forbidden scope

Do not:
- redesign or duplicate canonical quality logic;
- change Python Core quality semantics under `src/`;
- enable full Validate;
- implement solver, Difficulty V1, load/risk or unified M05 validation;
- add persistence, revision history, save/export or production promotion;
- start SB-LF06-009+ or SB-LFX work;
- touch sibling repositories;
- modify root `TASKS.md`.

## Verification

Run and record:
- focused LF06-008 R01 tests;
- real LF06-008 Godot integration;
- retained LF06-001..007/LF06-008 regressions;
- relevant quality/output/hash tests;
- full `python -m pytest -q`;
- compileall;
- Godot headless boot;
- `git diff --check`;
- `git diff -- TASKS.md` must be empty;
- exact changed-file review.

## Publication

Expected topology:
1. sync from current GitHub `main`;
2. remediation implementation/test commit(s);
3. push/equality checkpoint;
4. exactly one terminal builder-log-only publication commit;
5. stop.

At completion give only:
1. full GitHub URL of `.hiveai/codex-logs/SB-LF06-008-C001-R01_STALE_REVALIDATION_REENTRY_REMEDIATION_CODEX_LOG.md`;
2. final remediation implementation commit SHA;
3. terminal log-only publication commit SHA.