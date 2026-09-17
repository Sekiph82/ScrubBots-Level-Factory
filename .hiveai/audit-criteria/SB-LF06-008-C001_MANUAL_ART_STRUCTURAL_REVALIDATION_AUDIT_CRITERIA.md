# SB-LF06-008-C001 — Manual Artwork Structural Revalidation — Strict Audit Criteria

Document role: INDEPENDENT CHATGPT AUDIT CRITERIA

Target requirement:

`SB-LF06-008 — Revalidate after manual changes. [PARTIAL]`

## 1. Current capability truth

This audit must judge the implementation against current repository authority, not future M03/M04/M05 plans.

Current canonical capabilities support deterministic structural/art QA through Python `QualityPolicy` + `evaluate_grid()` and fail-closed source-bundle validation through `read_bundle()`.

Current repository does **not** yet provide authoritative:
- gameplay solver validation;
- measured Difficulty V1 validation;
- load/risk validation;
- unified M05 validation;
- production promotion after manual edits.

Therefore LF06-008 may close only as bounded **manual artwork structural revalidation**. It must not claim full candidate validation.

## 2. Severity model

### BLOCKER
Any of the following is an automatic FAIL:
- canonical source bundle/artwork/metadata is modified in place;
- edited working art is silently persisted/promoted as canonical or production content;
- Studio/GDScript reimplements structural QA rules instead of invoking canonical Python quality code;
- the existing `Validate` action is enabled or relabeled as full validation without a real standalone M05 authority;
- solver, measured difficulty, load/risk or owner acceptance is fabricated;
- GenerationRequest difficulty is presented as measured difficulty;
- builder edits root `TASKS.md`.

### MAJOR
Examples:
- revalidation uses a new/default quality policy instead of the exact policy bound to the source bundle;
- source bundle is not fail-closed validated through canonical bundle authority before revalidation;
- result is not bound to both source candidate identity and exact working-grid hash;
- result remains current after the working edit changes;
- dirty edit is replaced/reset as a side effect of revalidation;
- process bridge permits arbitrary command/shell execution;
- only grep/static evidence exists and no real Studio→Python canonical-quality boundary is executed;
- rejected/error result is shown as accepted/valid.

### MINOR
Examples:
- truthful capability exists but operator labels are ambiguous;
- evidence/result presentation omits useful provenance fields while underlying binding is correct;
- narrow regression/documentation gap that does not compromise truth or source immutability.

## 3. Required architecture

PASS requires a narrow revalidation path over the LF06-006 **memory-only DIRTY working copy**.

Expected responsibility split:
- GDScript/editor owns UI state and exact working logical pixels only;
- a bounded Studio/Core bridge transports revalidation input;
- Python canonical quality code owns policy parsing, structural analysis and decision;
- canonical source bundle remains immutable;
- no second validator or second persistent truth store is created.

A repository-local launcher/helper is acceptable only as transport/orchestration around existing canonical Python contracts. It must not become a second quality engine.

## 4. Source binding gate

Before revalidation, audit must prove:
- editor is `DIRTY` with one or more exact source-vs-working pixel differences;
- working dimensions exactly match the immutable editor source artwork;
- every working logical cell maps exactly to C01..C16;
- source candidate/bundle identity comes from the editor's retained source, not merely the latest action result;
- canonical source bundle is read through `read_bundle()` or an equivalently authoritative existing fail-closed bundle contract;
- source bundle candidate ID/grid hash/dimensions agree with editor source identity.

If any binding fails, result must be ERROR/UNAVAILABLE, never structural accept.

## 5. Exact quality-policy reuse

The revalidation must reuse the **exact canonical quality policy recorded in the source bundle metadata**.

Audit must reject implementations that:
- instantiate a fresh default policy;
- derive policy from current draft controls;
- derive policy from candidate presentation labels;
- reinterpret difficulty or board size;
- silently change thresholds.

The source policy must be parsed through canonical `QualityPolicy` semantics and then supplied to canonical `evaluate_grid()`.

## 6. Working-copy evaluation

Canonical Python must evaluate the exact current working logical grid and return a structured result containing at least:
- explicit scope such as `STRUCTURAL_ART_QA_ONLY`;
- source candidate ID;
- source grid hash;
- working grid hash;
- width/height;
- dirty-cell count or equivalent edit evidence;
- quality schema/version;
- policy identity/version;
- accepted/rejected decision;
- rejection codes;
- safe error text for failures.

The working-grid hash must use the existing canonical logical-grid hash contract, not a Studio-specific ad hoc digest.

## 7. Truthful Studio state

The UI must distinguish at minimum:
- no manual changes / revalidation not required;
- revalidation available;
- running;
- structural ACCEPT;
- structural REJECT;
- ERROR/UNAVAILABLE;
- STALE after later edits.

Required truth labels:
- `STRUCTURAL ART QA ONLY` or equivalent;
- `NOT FULL GAMEPLAY VALIDATION`;
- solver unavailable pending M03;
- measured difficulty unavailable pending M04;
- unified validation unavailable pending M05;
- `QA PASS != OWNER ACCEPT`;
- structural accept does not promote the edited working copy.

Do not call a structural ACCEPT result simply `VALID` without scope qualification.

## 8. Staleness / edit lifecycle

After a successful or rejected revalidation:
- editing any pixel so the working-grid hash changes must make the previous result STALE immediately or on the next deterministic refresh;
- stale evidence must never remain presented as current;
- restoring/resetting to canonical source must move the workflow to no-manual-change/not-required state;
- revalidation must not clear DIRTY state by itself;
- failed/newer Core actions must not silently erase or relabel a retained DIRTY edit/revalidation result.

## 9. Source immutability

Runtime evidence must hash/compare the source bundle before and after revalidation and prove no byte changes to at least:
- `artwork.png`;
- `artwork.json`;
- `metadata.json`.

No durable edited candidate, metadata replacement, revision or production artifact may be created in this task.

Transient transport files are permitted only if:
- bounded to a safe temp/cache location;
- contain no secret data;
- are deleted deterministically;
- are not treated as canonical artifacts.

## 10. Process safety

Any process bridge must:
- use executable + discrete argument array;
- never use `cmd /c`, PowerShell, Bash or shell interpolation;
- expose only a fixed revalidation operation;
- reject arbitrary command/executable fields;
- preserve exit code/stdout/stderr truthfully;
- fail closed when Python/Core is unavailable;
- avoid absolute owner-specific hard-coded paths.

## 11. Required real tests

PASS eligibility requires committed tests that execute the real path, not only source markers.

At minimum prove:
1. CLEAN/no-change editor cannot masquerade as revalidated manual edit;
2. DIRTY working art can invoke the canonical Python structural revalidation path;
3. source bundle is validated and exact source policy is reused;
4. result working-grid hash equals the exact edited grid;
5. at least one deterministic structural ACCEPT or direct canonical parity case is covered;
6. a deliberately bad edited grid produces structural REJECT with real canonical rejection code(s);
7. source bundle bytes remain unchanged;
8. further editing makes previous result STALE;
9. reset/source restoration removes current-manual-edit validation status;
10. no solver/difficulty/load/risk/full-validation claim appears;
11. existing LF06-001..007 regressions remain green.

## 12. Regression / scope gates

Audit must confirm:
- LF06-003 `Validate` action remains dependency-gated/unavailable;
- LF06-004 canonical preview truth remains unchanged;
- LF06-005 canonical evidence panel remains source-bundle truth, not manual-edit truth;
- LF06-006 editor remains non-destructive and source-bound;
- LF06-007 puzzle-config gate remains UNAVAILABLE until an approved contract exists;
- no provider/network/persistence/revision-history/production-promotion work is introduced;
- no SB-LF06-009+ or SB-LFX scope is started.

## 13. Verification evidence expected in builder log

Audit expects builder evidence for:
- focused LF06-008 tests;
- retained LF06-001..007 tests;
- relevant canonical quality/output contract tests;
- committed real Godot revalidation integration;
- Python bridge/launcher integration if added;
- full `python -m pytest -q`;
- compileall;
- Godot headless boot;
- `git diff --check`;
- exact changed-file review;
- `git diff -- TASKS.md` empty.

Builder test claims are evidence only; independent audit still inspects committed code, tests, changed-file scope and commit topology.

## 14. Publication discipline

Expected topology:
1. synchronized start from current `main`;
2. implementation/test commit(s);
3. final implementation equality checkpoint;
4. exactly one terminal builder-log-only publication commit.

Any product/test change after the claimed final implementation checkpoint reopens audit scope.

## PASS closure rule

`SB-LF06-008` may be marked complete for the current repository snapshot if manual artwork changes receive real canonical structural/art QA revalidation with exact source-policy reuse, immutable source truth, hash-bound/stale-safe evidence and explicit dependency limitations.

This closure does **not** imply M03 solver completion, M04 Difficulty V1 completion or M05 unified validation completion.