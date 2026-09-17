# SB-LF06-010-C001 — Factory Studio Editor Presentation / Truth Separation — Strict Audit

Document role: INDEPENDENT CHATGPT STRICT AUDIT

## Verdict

**PASS / CLOSED**

Severity summary:
- BLOCKER: 0
- MAJOR: 0
- MINOR: 0
- NOTE: 1

## Audited publication chain

- Starting accepted frontier: `98924e16e7dd624a32b92da8085bde18b5d3686b`
- Implementation commit: `6972a7b6d360b7d73380ff9f04b1cef42e07360e`
- Terminal builder-log-only publication: `4e6effb5455440b5e9a694646c5c4d19b89db931`

The implementation range is exactly one commit. Changed implementation files are limited to the LF06-010 builder log, one committed Godot truth-separation integration suite, one focused LF06-010 Python regression file, and one narrow project-boundary allowlist entry for the new committed runner. No product script, canonical Python Core semantic file, tracker, provider, persistence, promotion, main-game, or Content Platform file changed.

The terminal publication commit changes only the finalized LF06-010 builder log.

## Acceptance findings

### 1. Real A/B divergence proves domain separation

The committed Godot suite executes the real Studio and canonical local Python bridge. It generates canonical candidate A, loads A explicitly into the editor, paints a real canonical logical cell, and proves the editor is DIRTY and source-bound to A.

Draft-only changes then leave latest action evidence, retained successful Core evidence, canonical preview/evidence, editor source identity, working pixels and dirty count unchanged.

A distinct candidate B is then generated while editor A is still DIRTY. Canonical preview/evidence move together to B while the editor remains source-bound to A with the exact DIRTY working pixels retained.

### 2. Candidate presentation remains presentation-only

The runtime suite proves the presentation label does not become candidate identity and does not cross the Core process boundary. Static guards retain the absence of candidate-presentation data from canonical gateway candidate-ID arguments.

### 3. Manual revalidation remains bound to editor truth, not latest action truth

With canonical preview/evidence already showing B, real manual structural revalidation still binds to the retained editor source candidate A and its exact DIRTY working grid. Revalidation does not move canonical preview/evidence and source bundle bytes remain unchanged.

### 4. Reproduce moves canonical surfaces without replacing DIRTY editor source

Real Reproduce moves preview and evidence together to the reproduction bundle. Editor A remains DIRTY/source=A while separately exposing the latest successful reproduction identity. Manual revalidation source identity remains A.

### 5. Failed/unavailable action remains separate from retained success

The suite invokes dependency-gated Validate and proves the latest action attempt is UNAVAILABLE while the previous successful Reproduce evidence remains retained. Canonical preview/evidence retain the previous successful bundle with retained-last-success semantics. DIRTY editor A and its revalidation identity are unchanged.

### 6. Explicit replacement is the only editor-source crossing boundary

Only the explicit `load_current_canonical_artwork(true)` operator-equivalent call moves editor source from A to the latest successful canonical reproduction. The editor then becomes CLEAN, dirty count becomes zero, working buffer matches source and manual revalidation becomes NOT_REQUIRED.

### 7. No second truth store or canonical mutation was introduced

No new product-side master/singleton/database/file authority was added. The cycle is intentionally regression/evidence focused. Canonical A bundle bytes are checked across divergence, revalidation, later successful actions, unavailable action handling and explicit replacement.

### 8. Retained regressions and publication evidence

Builder reported:
- focused LF06-010: 5 passed;
- retained relevant regression set: 211 passed;
- full pytest: 727 passed, 1 pre-existing cache warning;
- compileall: PASS;
- Godot headless boot: exit 0;
- committed real LF06-010 Godot integration: exit 0 with PASS marker;
- `git diff --check`: PASS;
- `git diff -- TASKS.md`: empty.

These execution counts are builder-reported. The independent audit verified committed test semantics, changed-file scope, publication topology and the real runtime assertions in source.

## NOTE-001

The A/B integration does not take a standalone `last_successful_core_evidence_snapshot()` assertion immediately after Generate B; however, the same runtime sequence proves B as the successful canonical action across action/preview/evidence/editor-latest-success domains and later proves last-success retention after real Reproduce followed by UNAVAILABLE Validate. This is not an acceptance gap and does not alter the PASS verdict.

## Closure

`SB-LF06-010 — Keep editor presentation separate from truth` is independently accepted as **PASS / CLOSED**.
