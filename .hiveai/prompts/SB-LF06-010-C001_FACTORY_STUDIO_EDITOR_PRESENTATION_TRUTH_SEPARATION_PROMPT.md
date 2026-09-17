# SB-LF06-010-C001 — Factory Studio Editor Presentation / Truth Separation

Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`
Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Mission

Work only on:

`SB-LF06-010 — Keep editor presentation separate from truth. [PARTIAL]`

This is primarily a **truth-separation consolidation and runtime-regression task**, not permission to create another truth model.

The accepted LF06-002..008 chain already provides distinct surfaces. Your job is to prove and, only where genuinely necessary, minimally harden their separation.

Create/finalize builder log:

`.hiveai/codex-logs/SB-LF06-010-C001_FACTORY_STUDIO_EDITOR_PRESENTATION_TRUTH_SEPARATION_CODEX_LOG.md`

Do not modify root `TASKS.md`.

## Required reads

Read fully before edits:
- root `TASKS.md`;
- `.hiveai/audits/SB-LF06-008-C001-R01_STALE_REVALIDATION_REENTRY_REMEDIATION_STRICT_AUDIT.md`;
- `.hiveai/audit-criteria/SB-LF06-010-C001_EDITOR_PRESENTATION_TRUTH_SEPARATION_AUDIT_CRITERIA.md`;
- accepted LF06-002..008 prompts/audits as needed;
- `level_factory/scripts/factory_studio_target_controls.gd`;
- `factory_studio_art_preview.gd`;
- `factory_studio_evidence_panel.gd`;
- `factory_studio_art_editor.gd`;
- `factory_studio_art_revalidation.gd`;
- `factory_studio_puzzle_config_gate.gd`;
- `factory_core_gateway.gd`;
- existing Studio runtime/action/preview/evidence/editor/revalidation Godot suites;
- Factory project-boundary/governance tests.

## 1. Do not create a new master truth

Do not add a mutable `current candidate`, global singleton, JSON truth file, cache database, or other authority that flattens existing domains.

If a helper snapshot is useful for tests, it must be:
- read-only;
- derived on demand from existing component snapshots;
- non-persistent;
- explicitly partitioned by domain.

Prefer direct component snapshots in the runtime test if that is sufficient.

## 2. Preserve the existing truth domains

Keep these concepts separate:

1. **Draft presentation** — local target controls only.
2. **Latest action attempt** — SUCCESS/FAILED/UNAVAILABLE for the latest pressed action.
3. **Last successful Core evidence** — retained independently of later failed/unavailable attempts.
4. **Canonical preview** — successful-bundle `artwork.png` only.
5. **Canonical evidence** — successful-bundle `metadata.json` only.
6. **Manual editor** — explicitly loaded canonical source + memory-only working pixels.
7. **Manual structural revalidation** — exact working-grid structural QA only.

Do not collapse them into one state.

## 3. Product changes should be minimal

If the current accepted implementation already behaves correctly, it is acceptable for LF06-010 product changes to be very small or even test-only plus narrowly improved labels.

Do not refactor accepted LF06-003..008 code merely for style.

Only make a product change when the real integration exposes an actual truth-separation gap or when a current label is materially ambiguous.

## 4. Required real A/B divergence integration

Add one committed Godot integration suite dedicated to LF06-010, or extend an appropriate committed suite if that remains clearer and bounded.

The test must execute the real Studio scene and real canonical Python Core boundary.

### Candidate A

1. Generate real canonical candidate A.
2. Record:
   - action result A;
   - last-successful Core evidence A;
   - preview A identity/path;
   - evidence A candidate/hash/metadata path.
3. Explicitly load canonical A into the manual editor.
4. Paint at least one real logical C01..C16 cell.
5. Prove editor source=A, state=DIRTY, and capture exact working pixels/dirty count.

### Draft-only mutation

6. Change one or more local draft controls, including the presentation label if practical, **without Generate**.
7. Prove no canonical/action/editor source identity changes merely because the draft changed.
8. Prove candidate presentation text is still presentation-only and never becomes canonical candidate ID.

### Candidate B while editor A is DIRTY

9. Generate a distinct real canonical candidate B with an intentionally different deterministic seed/request.
10. Assert B is actually distinguishable from A by candidate ID and/or canonical grid hash/output identity.
11. Without resetting/replacing editor A, prove:
   - latest action attempt=B SUCCESS;
   - last successful Core evidence=B;
   - canonical preview=B;
   - canonical evidence=B;
   - preview/evidence refer to the same B successful bundle identity;
   - editor source is still A;
   - editor remains DIRTY;
   - A working pixels and dirty count are unchanged;
   - editor may separately expose latest successful candidate B, but that does not replace source A.

### Revalidate DIRTY A after B exists

12. Run the real LF06-008 manual structural revalidation while canonical surfaces elsewhere show B.
13. Prove revalidation binds to editor source candidate A and A's exact current dirty working grid, not B.
14. Prove canonical preview/evidence remain B and canonical source bytes remain unchanged.

### Reproduce / action retention

15. Execute real Reproduce for the current successful canonical B if the existing action contract permits it cleanly in this scenario.
16. Prove preview and evidence move together to the reproduction bundle while editor A remains DIRTY/source=A.
17. Invoke one dependency-gated action such as Validate/Solve/Analyze.
18. Prove latest action attempt is truthfully UNAVAILABLE while retained successful Core evidence and canonical preview/evidence remain the previous successful B/Reproduce evidence.
19. Prove editor A DIRTY and its manual revalidation evidence are not rewritten as action truth.

### Explicit replacement boundary

20. Only now perform the explicit operator-equivalent editor replacement with the latest successful canonical artwork.
21. Prove editor source changes from A to the latest successful B identity only because of this explicit replacement.
22. Prove editor becomes CLEAN and exact working pixels equal the newly loaded immutable source.
23. Prove manual revalidation becomes NOT_REQUIRED for the CLEAN editor.

## 5. Candidate presentation must remain presentation-only

Static and runtime evidence must prove the optional candidate presentation label:
- is bounded UI text only;
- is not passed as `--candidate-id`;
- does not replace Core-returned candidate ID;
- cannot alter existing canonical preview/evidence/editor source simply by editing the field.

## 6. Canonical preview/evidence pairing

For fresh successful Generate/Reproduce results consumed by both surfaces:
- preview bundle/artwork path and evidence metadata path must come from the same successful action output;
- candidate identity/hash/dimensions must agree where exposed;
- either surface failing to consume a bundle must remain ERROR/retained truthfully rather than synthesizing agreement.

Do not merge the two components into one authority.

## 7. Manual editor boundary

While editor state is DIRTY:
- later SUCCESS actions may update `latest_successful_action` availability;
- they must not auto-replace the loaded source/working copy;
- replacement requires explicit operator action;
- no canonical file may be overwritten.

Preserve LF06-006 state reconciliation exactly.

## 8. Manual revalidation boundary

Preserve LF06-008/R01:
- source authority is the editor-retained source, not latest action;
- exact source policy reuse;
- canonical Python structural QA;
- working-grid hash binding;
- STALE/re-entry lifecycle;
- source immutability;
- structural-only semantics.

Do not write revalidation results into canonical metadata/evidence.

## 9. Required static guards

Add focused tests proving at least:
- target draft is labeled presentation-only;
- candidate presentation is absent from Core `--candidate-id` arguments;
- preview never consumes editor working pixels/draft;
- evidence panel never consumes editor/revalidation state;
- editor has no canonical source write path;
- revalidation has no canonical metadata write path;
- no new persistent/master truth store was added;
- LF06-003 Validate remains unavailable;
- LF06-007 puzzle-config gate remains unavailable until a real contract exists.

Do not rely on static guards alone.

## 10. Preserve previous accepted work

Must remain green:
- LF06-001..008;
- LF01 dimension contracts;
- canonical palette/source immutability;
- real Generate/Reproduce bridge;
- canonical preview and evidence panels;
- non-destructive editor;
- repeated stale revalidation re-entry.

## 11. Forbidden scope

Do not implement:
- M03 solver;
- M04 Difficulty V1;
- M05 full unified validation;
- persistence/revision history;
- save/export of manual edits;
- owner acceptance;
- production promotion;
- Dashboard/Import/Library/provider work;
- Content Platform/main-game work;
- SB-LF06-011+;
- any SB-LFX task.

Do not modify canonical Python Core semantics unless a genuine existing defect is independently demonstrated and documented. This task should normally require no `src/` semantic changes.

Do not modify root `TASKS.md`.

## 12. Verification

Run and record:
- focused LF06-010 tests;
- committed real LF06-010 Godot truth-separation integration;
- retained LF06-001..008 tests;
- relevant canonical output/quality tests where touched;
- full `python -m pytest -q`;
- compileall;
- `godot --headless --path level_factory --quit`;
- `git diff --check`;
- `git diff -- TASKS.md` must be empty;
- exact changed-file/scope review.

Record failed iterations and corrections honestly.

## Acceptance criteria

PASS eligibility requires:
- real runtime A→DIRTY A→Generate B divergence without silent editor replacement;
- draft-only mutation leaves truth untouched;
- canonical preview/evidence move together to B;
- editor remains A DIRTY until explicit replacement;
- manual revalidation after B still binds to A working truth;
- failed/unavailable action remains separate from retained successful B evidence;
- explicit replacement is the only boundary that moves editor source to current canonical B;
- no new master truth store;
- no canonical source mutation;
- prior LF06 contracts remain intact;
- root `TASKS.md` untouched;
- exactly one terminal builder-log-only publication commit follows implementation.

## Publication

Push implementation/tests/finalized builder log to `main`.

At completion give only:
1. full GitHub URL of `.hiveai/codex-logs/SB-LF06-010-C001_FACTORY_STUDIO_EDITOR_PRESENTATION_TRUTH_SEPARATION_CODEX_LOG.md`;
2. final implementation commit SHA;
3. terminal log-only publication commit SHA.

Then stop for independent ChatGPT strict audit.
