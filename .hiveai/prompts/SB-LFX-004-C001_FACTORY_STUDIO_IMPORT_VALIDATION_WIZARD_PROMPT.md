# SB-LFX-004-C001 — Factory Studio Import Validation Wizard

Document role: CODEX IMPLEMENTATION PROMPT

Work only on SB-LFX-004 during this task cycle.

Builder log:
`.hiveai/codex-logs/SB-LFX-004-C001_IMPORT_VALIDATION_WIZARD_CODEX_LOG.md`

Create the builder log before edits.

## Read first

Read root TASKS.md, owner operations spec, SB-LFX-004 audit criteria, LFX-002 OWNER_UPLOAD contract, LFX-003 implementation/log if present, canonical palette/dimension/PNG/quality contracts, and existing Import/Library/Gateway code.

In batch mode, prior task logs are implementation context only. Do not claim prior tasks are audited unless a strict audit file actually says so.

## Implement

Add a canonical Python import-validation operation and a real Studio wizard.

Validation must be bound to exact OWNER_UPLOAD source identity and must report:
- strict format/media status;
- width/height and logical-dimension legality;
- exact C01..C16 mapping facts;
- foreign-color count;
- semi-alpha/alpha facts;
- used-color IDs/count;
- canonical structural disposition/rejection codes only when an exact logical grid is valid.

For an exact logical source, interpret source pixels without changing them.

For a source requiring resize/palette conversion, report `DERIVED_ARTIFACT_REQUIRED` and reasons. Show the applicable locked policy identities, but do not silently transform.

Persist validation evidence separately from source truth using a versioned schema and source hash binding.

## UI

Make Import validation operator-visible:
- Run/Re-run;
- facts and rejection reasons;
- source immutable notice;
- explicit “derived artifact required” state;
- solver/difficulty/owner acceptance unavailable.

## Forbidden

No source mutation, no silent normalization, no candidate promotion, no owner acceptance, no solver/difficulty fiction, no network/provider work, no LFX-005+ work, no TASKS edit.

## Tests

Use real Studio scene and canonical Python. Cover valid logical art, foreign color, semi-alpha/alpha violation, illegal/non-logical dimensions, source immutability, deterministic revalidation, tamper fail-closed, and cleanup.

Keep the full repository green.

## Publication

Commit implementation/tests, push, then make exactly one task-final builder-log-only commit. Record implementation SHA and final log SHA in the task log, then continue only when invoked by the authorized SB-LFX batch master.
