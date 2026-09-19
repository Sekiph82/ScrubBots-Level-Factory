# SB-LFX-001-C001 — Factory Operations Dashboard Canonical Derived View — Strict Audit Criteria

Document role: INDEPENDENT CHATGPT AUDIT CRITERIA

Target extension:

`SB-LFX-001 — Build Factory Operations Dashboard from canonical job/artifact/evidence truth without creating a second tracker or production truth store. [EXTENSION]`

Authoritative product contract:
`docs/product/FACTORY_STUDIO_OWNER_OPERATIONS_EXTENSIONS_V01.md`

## 1. Purpose

Implement the first real Factory Studio Dashboard as a read-only operational view over existing canonical records.

The Dashboard is NOT:
- a project/task tracker;
- a new job database;
- a replacement for canonical batch manifests;
- an owner-acceptance system;
- a solver/difficulty authority;
- a provider accounting system.

Current canonical persisted operational truth includes the versioned `scrubbots-batch-manifest` contract, whose authoritative fields include:
- batch_id;
- requested_count;
- max_attempts;
- root_seed;
- request_template;
- next_attempt_index;
- attempts;
- accepted;
- accepted_count;
- terminal_state;
- quality policy/exemplar identity evidence.

Current Studio runtime also has separate latest action-attempt and retained successful Core evidence.

## 2. Severity model

### BLOCKER

Automatic FAIL if:
- Dashboard creates or persists a second task/job/production truth store;
- Dashboard writes or mutates canonical batch manifests/candidate bundles;
- Dashboard copies canonical batch semantics into an incompatible schema and then treats that copy as authority;
- root `TASKS.md` is read as Dashboard production data or rendered as an operations tracker;
- generated/QA/accepted/review/solver/difficulty/timing/provider values are fabricated when canonical evidence is absent;
- QA PASS is presented as owner acceptance or production-ready;
- builder modifies root `TASKS.md`;
- provider/network/credential integration is added.

### MAJOR

Examples:
- Dashboard does not validate the canonical manifest before presentation;
- malformed/unsupported manifests are partially rendered as trusted data instead of ERROR;
- counts shown by Dashboard disagree with manifest/attempt evidence;
- rejection-reason aggregation is lossy or invents counts;
- current Studio candidate is conflated with batch current/latest attempt;
- missing owner-review/timing/solver/difficulty evidence is shown as zero, PASS, READY or estimated fact rather than NOT AVAILABLE/UNKNOWN;
- Dashboard remains a static placeholder and never renders a real canonical manifest;
- no real Godot integration proves the Dashboard from a canonical manifest;
- Dashboard reads arbitrary filesystem paths outside the approved Factory output boundary.

### MINOR

Examples:
- truthful values are present but one useful canonical field is omitted;
- correct derived view but labels are mildly ambiguous;
- refresh/presentation ergonomics are rough without affecting truth.

## 3. Canonical manifest authority

Do not hand-roll a permissive manifest interpretation.

Preferred boundary:
- add a narrow canonical Python read/inspect operation that reuses the existing authoritative batch-manifest validation path, OR
- reuse an already public canonical validation/inspection API if one exists.

Godot must not become the canonical manifest validator.

The returned Dashboard payload may be a read-only derived projection, but it must:
- identify the source manifest path and batch_id;
- fail closed when the source manifest is malformed/unsupported;
- be derived fresh from canonical source on refresh;
- never be persisted as new truth.

## 4. Approved input boundary

Dashboard may inspect canonical batch manifests only inside the approved Factory output area.

No arbitrary absolute-path browsing.

A bounded operator path field/selector is acceptable if it resolves only within `level_factory/output/`.

If no manifest is selected/present:
- Dashboard shows EMPTY / NO CANONICAL BATCH SELECTED;
- it does not synthesize a demo batch.

## 5. Required batch-derived presentation

For a valid canonical batch manifest, display at least:

### Identity/state
- batch ID;
- terminal state: IN_PROGRESS / COMPLETE / EXHAUSTED;
- requested target count;
- max attempts;
- attempts/generated count derived from canonical attempts/next_attempt_index;
- accepted count.

### Request context
- difficulty target from request_template;
- width × height;
- generator mode;
- source classification as canonical batch/procedural only where supported by the manifest. Do not invent provider identity.

### Attempt dispositions
Truthfully derive and show counts for applicable canonical statuses:
- ACCEPTED;
- QUALITY_REJECTED;
- GENERATOR_FAILURE;
- DUPLICATE.

If a concept such as generic “QA pass count” is displayed, its derivation must be explicit and consistent with canonical attempt fields. Do not silently equate ACCEPTED with owner acceptance.

### Rejection reasons
Aggregate exact canonical `rejection_codes` with counts from attempts.
Do not replace them with generic invented wording.

### Current/latest batch attempt
Where attempts exist, show a clearly labeled latest batch attempt using canonical attempt_index/status and any present candidate/grid/dimension evidence.
Do not call it “current canonical candidate” unless the canonical record supports that meaning.

## 6. Studio current-action evidence

Dashboard may additionally show a separate “Studio latest action / retained successful Core evidence” section derived from existing TargetControls snapshots.

It must remain visibly separate from persisted batch state.

Examples:
- latest action attempt;
- retained successful candidate ID;
- retained output/metadata path;
- dimensions/mode/grid hash where already exposed.

A Studio Generate result must not rewrite or masquerade as batch-manifest state.

## 7. Explicit unavailable domains

For product-spec fields whose canonical source is not connected yet, render truthfully as NOT AVAILABLE / UNKNOWN with reason.

At minimum evaluate:
- owner-review queue/count;
- measured solver state;
- measured Difficulty V1;
- elapsed timing / average timing unless a canonical record actually contains it;
- provider credits/cost.

Do not derive timing from filesystem mtimes.
Do not infer owner review from QA acceptance.

## 8. UI / navigation

The existing Dashboard navigation surface must become real rather than the current static placeholder.

Keep the owner-approved navigation model.

Dashboard should be readable at normal desktop size and expose:
- state/error/empty status;
- refresh/load action;
- identity/count summary;
- request context;
- disposition/rejection summary;
- current/latest attempt;
- separate Studio action evidence;
- unavailable domains.

Do not redesign unrelated Generate surfaces.

## 9. No mutation / no second truth

Dashboard actions are read-only:
- refresh;
- select/load approved manifest path;
- possibly navigate to existing surfaces.

No retry, accept, reject, promote, mutate, delete, edit or publish action belongs in SB-LFX-001.

No JSON cache/database/session file may become Dashboard authority.

## 10. Required runtime tests

PASS requires committed real tests.

At minimum one Godot integration must:

1. create or obtain a real canonical batch manifest using existing canonical Python batch generation in a bounded test output;
2. open real Factory Studio Dashboard;
3. point Dashboard to that canonical manifest through the approved boundary;
4. refresh/load it;
5. prove displayed batch identity/counts/request context/status/rejection aggregation equal canonical manifest truth;
6. prove Studio latest-action evidence, if exercised, is presented separately;
7. prove missing owner-review/timing/solver/difficulty/provider fields are NOT AVAILABLE rather than fabricated;
8. mutate/corrupt a test manifest copy and prove Dashboard becomes ERROR/fail-closed without retaining corrupted values as current truth;
9. prove source manifest bytes are unchanged by Dashboard;
10. clean bounded test artifacts.

Also include focused static guards proving:
- no TASKS parser/import;
- no manifest write path;
- no provider/network dependency;
- no persistent Dashboard truth file/database;
- canonical validation remains Python-owned.

## 11. Retained regressions / publication

Builder must record:
- focused SB-LFX-001 tests;
- real Dashboard Godot integration;
- relevant LF06-001..012 regressions;
- full `python -m pytest -q`;
- compileall;
- Godot headless boot;
- `git diff --check`;
- `git diff -- TASKS.md` empty;
- exact changed-file review;
- exactly one terminal builder-log-only publication commit.

## 12. Scope limits

Do not implement:
- SB-LFX-002+;
- import/library/review queue mutations;
- batch start/retry controls;
- solver/M03;
- Difficulty V1/M04;
- unified M05 validation;
- owner acceptance;
- production promotion;
- provider cost center;
- Content Platform/main-game work.

## PASS closure rule

`SB-LFX-001` may close when the Dashboard is a real, read-only, fail-closed Factory Studio view over canonical batch/action evidence, exposes unavailable domains truthfully, introduces no second truth store or tracker, and is proven by real runtime integration against canonical records.
