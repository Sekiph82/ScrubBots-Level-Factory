# SB-LFX-001-C001 — Factory Operations Dashboard Canonical Derived View

Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`
Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Mission

Work only on:

`SB-LFX-001 — Build Factory Operations Dashboard from canonical job/artifact/evidence truth without creating a second tracker or production truth store. [EXTENSION]`

This is the first owner-approved post-cutover Factory Studio extension.

Create/finalize builder log:

`.hiveai/codex-logs/SB-LFX-001-C001_FACTORY_OPERATIONS_DASHBOARD_CANONICAL_DERIVED_VIEW_CODEX_LOG.md`

Do not modify root `TASKS.md`.

## Required reads

Read fully:
- root `TASKS.md`;
- LF06-012 closing strict audit;
- `docs/product/FACTORY_STUDIO_OWNER_OPERATIONS_EXTENSIONS_V01.md`;
- `.hiveai/audit-criteria/SB-LFX-001-C001_FACTORY_OPERATIONS_DASHBOARD_CANONICAL_DERIVED_VIEW_AUDIT_CRITERIA.md`;
- current Studio navigation/workspace/shell;
- target controls/action evidence;
- canonical batch manifest generation/validation in `src/scrubbots_pixel_factory/cli/main.py`;
- existing M08/M09 batch-manifest tests/audits;
- project-boundary/clean-checkout tests.

## 1. Make Dashboard real, but read-only

Replace only the current Dashboard placeholder with a real Factory Operations Dashboard.

It must be a derived view over canonical records.

Do NOT create:
- Dashboard database;
- Dashboard manifest;
- duplicate job store;
- project/task tracker;
- owner-acceptance store.

## 2. Canonical batch inspection must remain Python-owned

Do not parse/validate the canonical batch manifest permissively in GDScript.

Add/reuse a narrow canonical Python inspection boundary that:
- accepts only an approved `level_factory/output/` manifest path;
- reuses authoritative existing batch-manifest validation;
- emits a bounded read-only Dashboard projection;
- fails closed on malformed/unsupported manifests;
- does not mutate the manifest.

Do not change canonical batch generation semantics.

## 3. Dashboard source selection

Provide a bounded operator mechanism to load/refresh one canonical `batch-manifest.json` under `level_factory/output/`.

No arbitrary absolute path.

No selected manifest:
`EMPTY — no canonical batch selected`.

Invalid/corrupt manifest:
`ERROR`, with no corrupted values presented as trusted current state.

## 4. Required dashboard information

For a valid manifest show, from canonical evidence:

- batch ID;
- terminal state;
- target/requested count;
- max attempts;
- generated/attempt count;
- accepted count;
- difficulty target;
- dimensions;
- generator mode;
- counts for ACCEPTED / QUALITY_REJECTED / GENERATOR_FAILURE / DUPLICATE;
- exact rejection-code aggregation;
- latest batch attempt identity/status/details where present.

Keep labels explicit. ACCEPTED/QA must not imply owner acceptance or production-ready.

## 5. Separate Studio action evidence

Add a visually separate section for existing Studio action truth if available:
- latest action attempt;
- retained successful candidate evidence.

Do not merge it with batch state.

A Generate/Reproduce action in Studio must not rewrite batch-manifest values.

## 6. Truthful unavailable fields

Show these as NOT AVAILABLE / UNKNOWN unless a real canonical record exists:
- owner review queue/count;
- gameplay solver;
- measured Difficulty V1;
- elapsed/average timing;
- provider credits/cost.

Never estimate timing from file timestamps.
Never infer owner approval from QA.

## 7. Read-only scope

Allowed actions:
- load/refresh approved manifest;
- read existing Studio evidence.

Forbidden:
- accept/reject;
- retry;
- regenerate;
- edit;
- promote;
- publish;
- delete;
- mutate batch/candidate files.

Those belong to later tasks.

## 8. Required real tests

Add focused tests plus one real Godot Dashboard integration that:
- creates a real canonical batch manifest in bounded test output using existing canonical Python;
- loads it in real Dashboard;
- proves displayed values equal manifest truth;
- proves unavailable domains remain unavailable;
- proves Studio evidence stays separate;
- corrupts a test manifest copy and proves fail-closed ERROR;
- proves source bytes unchanged;
- cleans test output.

Add static guards for:
- no root TASKS consumption;
- no manifest writes;
- no Dashboard persistence;
- no provider/network/credentials;
- canonical validation Python-owned.

## 9. Preserve accepted work

Keep LF06-001..012 green.
Do not refactor Generate/editor/revalidation/reproduce product code for style.

## 10. Forbidden scope

Do not start:
- SB-LFX-002+;
- import/library/review workflows;
- M03/M04/M05;
- batch retry/start controls;
- provider accounting;
- Content Platform;
- main game.

Do not modify `TASKS.md`.

## Verification

Run and record:
- focused SB-LFX-001 tests;
- real Godot Dashboard integration;
- relevant LF06 retained tests;
- full pytest;
- compileall;
- Godot headless boot;
- diff check;
- TASKS diff empty;
- exact changed-file review.

Publication:
- implementation/tests/docs;
- push/equality checkpoint;
- exactly one terminal builder-log-only publication commit;
- stop.

At completion give only:
1. full GitHub URL of `.hiveai/codex-logs/SB-LFX-001-C001_FACTORY_OPERATIONS_DASHBOARD_CANONICAL_DERIVED_VIEW_CODEX_LOG.md`;
2. final implementation commit SHA;
3. terminal log-only publication commit SHA.
