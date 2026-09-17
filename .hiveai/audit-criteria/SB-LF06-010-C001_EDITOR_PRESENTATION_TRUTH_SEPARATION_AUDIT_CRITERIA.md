# SB-LF06-010-C001 — Factory Studio Editor Presentation / Truth Separation — Strict Audit Criteria

Document role: INDEPENDENT CHATGPT AUDIT CRITERIA

Target requirement:

`SB-LF06-010 — Keep editor presentation separate from truth. [PARTIAL]`

## 1. Purpose

This task closes a cross-surface truth-separation requirement. It must not invent a new canonical truth store.

The current Studio already has distinct domains:
- local Generate draft presentation;
- latest action-attempt result;
- retained last successful Core evidence;
- canonical artwork preview sourced from successful-bundle `artwork.png`;
- canonical evidence panel sourced from successful-bundle `metadata.json`;
- LF06-006 manual editor source + memory-only working copy;
- LF06-008 manual structural revalidation evidence bound to the editor working copy;
- LF06-007 puzzle-config capability gate.

PASS requires these domains to remain explicitly distinct under real runtime transitions.

## 2. Severity model

### BLOCKER
Automatic FAIL if any of the following occurs:
- draft/presentation values mutate canonical artifacts/evidence without a successful Core action;
- manual editor pixels mutate canonical preview/evidence/action truth in place;
- a new successful Core action silently replaces a DIRTY editor working copy;
- manual revalidation is written into canonical source `metadata.json` or treated as canonical bundle truth;
- a combined Studio state becomes a second canonical truth store;
- candidate presentation label is used as canonical candidate identity;
- generated/manual structural QA is presented as owner acceptance or production promotion;
- root `TASKS.md` is modified by the builder.

### MAJOR
Examples:
- failed/unavailable action overwrites last successful canonical preview/evidence;
- canonical preview and canonical evidence silently point at different successful bundle identities without explicit ERROR/retained semantics;
- editor source identity silently follows latest action while DIRTY;
- revalidation uses latest action identity instead of retained editor source identity;
- UI labels imply that draft/editor/revalidation values are canonical when they are not;
- only static string tests exist and no real cross-surface runtime sequence proves separation.

### MINOR
Examples:
- separation is correct but an operator label is ambiguous;
- a read-only diagnostic snapshot omits a useful identity field;
- narrow regression coverage gap that cannot mutate truth.

## 3. No new master truth store

Do not create a new mutable database/file/singleton/record that becomes authoritative over existing components.

A read-only derived diagnostics snapshot is permitted only if:
- it is computed from current component snapshots;
- it is not persisted;
- it cannot mutate any source;
- each domain is named separately rather than flattened into one `current candidate` concept.

## 4. Required truth domains

Audit must be able to distinguish at least:

### Draft presentation
Local target values only. Before Generate they are not canonical request/result evidence.

### Action attempt
The latest Generate/Reproduce/Unavailable/Failed action outcome. A failed attempt must remain a failed attempt and must not masquerade as retained success.

### Last successful Core evidence
A separately retained successful action identity, if one exists.

### Canonical preview
Read-only successful-bundle `artwork.png` presentation. Never rebuilt from draft/manual-editor pixels.

### Canonical evidence
Read-only successful-bundle `metadata.json` presentation. Never rebuilt from draft/manual-editor/revalidation state.

### Manual editor
Explicitly loaded immutable canonical source plus memory-only CLEAN/DIRTY working copy. DIRTY means manual working truth differs from canonical source.

### Manual revalidation
Structural/art QA evidence for the exact editor working grid only. It must remain scoped as `STRUCTURAL ART QA ONLY`, stale-safe, and non-promoting.

## 5. Critical runtime divergence scenario

PASS eligibility requires a real committed Godot integration sequence that proves intentional independent identities.

Minimum scenario:

1. Generate canonical candidate A successfully.
2. Canonical preview/evidence show A.
3. Explicitly load A into the manual editor.
4. Paint at least one real C01..C16 cell so editor A becomes DIRTY.
5. Capture A editor source identity and working-grid evidence.
6. Change only draft controls. Prove action/preview/evidence/editor source do not mutate merely because the draft changed.
7. Generate a distinct canonical candidate B successfully without resetting/replacing the DIRTY editor.
8. Prove latest action, retained successful Core evidence, canonical preview and canonical evidence now point to B.
9. Prove manual editor source is still A, still DIRTY, and working pixels are unchanged.
10. Prove editor snapshot may truthfully expose latest-successful candidate B separately from retained editor source A.
11. Run manual structural revalidation and prove it binds to editor source A + A-derived dirty working grid, not B.
12. Perform a failed or unavailable action and prove it remains a failed/unavailable attempt while B remains retained canonical preview/evidence and editor A remains DIRTY.
13. Only an explicit operator replacement action may replace DIRTY editor A with current canonical B; afterward editor becomes CLEAN on B and manual revalidation becomes NOT_REQUIRED.

Candidate A and B must be distinguishable by actual canonical identity/hash/output evidence.

## 6. Draft/presentation isolation

Changing any of these without executing Generate must not mutate accepted evidence:
- difficulty target;
- width/height;
- seed;
- mode;
- candidate presentation label.

The candidate presentation label remains presentation-only and must not be passed as canonical `candidate_id` or override Core identity.

## 7. Action failure retention

After a successful B exists, invoke at least one truthful unavailable/failed action such as dependency-gated Validate/Solve/Analyze or a bounded failure path.

Audit must prove:
- latest action attempt reports UNAVAILABLE/FAILED;
- last successful Core evidence still identifies B;
- canonical preview/evidence retain B and visibly preserve retained-last-success semantics where applicable;
- editor A DIRTY state is untouched;
- manual revalidation evidence is not rewritten as action truth.

## 8. Preview/evidence pair integrity

For every fresh successful action consumed by both canonical surfaces:
- preview source bundle/artwork identity and evidence metadata bundle identity must refer to the same successful action bundle;
- candidate ID/hash/dimensions must agree where both surfaces expose them;
- Reproduce must switch both to the reproduction bundle rather than silently mixing Generate and Reproduce paths.

If either canonical surface cannot consume a successful bundle, it must fail/retain truthfully rather than fabricate agreement.

## 9. Manual editor identity independence

While DIRTY:
- a later successful Generate/Reproduce may update `latest_successful_action` availability;
- it must not mutate `_source_candidate_id`, source bundle/path/hash, source image, working pixels, or dirty count;
- replacing the DIRTY editor requires an explicit operator action.

This is a core acceptance invariant.

## 10. Manual revalidation identity independence

Revalidation must use editor-retained source + exact editor working pixels.

A newer canonical B elsewhere in Studio must not cause A's DIRTY working-copy revalidation to bind to B.

After B is generated while A is DIRTY, revalidation evidence must still report source candidate A until the operator explicitly replaces editor source.

## 11. Operator labels

UI must not collapse these phrases into ambiguous `current` truth:
- draft target;
- action attempt;
- last successful Core evidence;
- canonical preview/evidence;
- editor source;
- DIRTY working copy;
- structural revalidation.

Existing labels may be retained if already unambiguous. Do not redesign UI merely for cosmetic wording.

## 12. Required tests

PASS requires committed real tests, not grep-only checks.

At minimum:
- one real Godot cross-domain integration covering the full A→DIRTY A→Generate B divergence scenario;
- draft-only change isolation;
- B canonical preview/evidence identity agreement;
- A editor dirty/source identity preservation after B;
- A manual revalidation after B;
- failed/unavailable action retention after B;
- explicit DIRTY replacement to B;
- no source-byte mutation;
- existing LF06-003..008 behavior remains green.

Static guards should also ensure:
- candidate presentation label is not sent as `--candidate-id`;
- preview does not consume editor working pixels/draft;
- evidence panel does not consume editor/revalidation truth;
- editor does not write canonical files;
- revalidation does not write canonical metadata;
- no new persistent truth store is introduced.

## 13. Scope limits

Do not implement:
- solver/M03;
- Difficulty V1/M04;
- unified M05 validator;
- persistence/revision history;
- owner acceptance;
- production promotion;
- Dashboard/Import/Library/providers;
- Content Platform/main-game work;
- SB-LF06-011+;
- any SB-LFX task.

Do not alter canonical Python Core semantics merely for this separation task.

## 14. Builder evidence expected

Builder log should record:
- focused LF06-010 tests;
- real Godot truth-separation integration;
- retained LF06-001..008 tests;
- full pytest;
- compileall;
- Godot headless boot;
- `git diff --check`;
- `git diff -- TASKS.md` empty;
- exact changed-file review;
- publication equality and terminal log-only commit.

## PASS closure rule

`SB-LF06-010` may close when runtime evidence proves that draft/action/canonical-artifact/manual-editor/manual-revalidation domains can intentionally diverge without overwriting, relabeling, or silently promoting one another, and only explicit operator actions cross the manual-editor replacement boundary.
