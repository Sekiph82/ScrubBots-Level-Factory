# PAG-SP06-C001 — Semantic Recognizability Gate Contract & Offline Review Foundation
Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`

## Authority

Read completely from GitHub before implementation:

1. root `TASKS.md`;
2. `.hiveai/audits/PAG-SP05-C003-R01_DIRECT_BINDING_PROOF_AND_PUBLICATION_EVIDENCE_CLOSURE_STRICT_AUDIT.md`;
3. `docs/LEVEL_ART_SEMANTIC_NORMALIZATION_OWNER_DECISION_V02.md`;
4. current `src/scrubbots_pixel_factory/semantic/contracts.py`;
5. current `src/scrubbots_pixel_factory/semantic/normalization/level_art.py`;
6. current `src/scrubbots_pixel_factory/semantic/normalization/core.py`;
7. current semantic qualification code/tests;
8. `GOVERNANCE.md` and `AGENTS.md`.

GitHub is authoritative.

Canonical local repository:

`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

Do not use `C:\Users\sekip\Desktop\ScrubBots`.

Do not edit root `TASKS.md`.

Create the matching builder log before product/test edits:

`.hiveai/codex-logs/PAG-SP06-C001_SEMANTIC_RECOGNIZABILITY_GATE_CONTRACT_AND_OFFLINE_REVIEW_FOUNDATION_CODEX_LOG.md`

---

## Mission

Create the first SP06 semantic-quality / recognizability gate foundation without pretending that simple structural metrics can automatically understand the depicted subject.

SP05 is accepted and closed. Treat the trusted `SemanticLevelArtArtifact` as immutable input truth. Do not reopen or redesign CELL_MAJORITY_V1, PALETTE_SNAP_V1, production dimensions, the 3..12 color envelope, weighted reduction, provenance, or trust sealing.

C001 must establish two clearly separated layers:

1. deterministic structural diagnostics derived from a trusted LEVEL_ART artifact;
2. an explicit recognizability review/disposition that is not fabricated from those diagnostics.

The system may compute objective image/grid structure. It must not claim that fragmentation, component count, symmetry, color balance, or any similar proxy proves that an image is semantically recognizable.

No provider execution is authorized in this cycle. Spend zero Magnific and PixelLab credits.

---

# 1. Add a dedicated semantic-quality package

Preferred location:

`src/scrubbots_pixel_factory/semantic/quality/`

Keep the new API narrow and typed. A clean design may use names such as:

- `SemanticQualityDiagnostics`
- `SemanticRecognizabilityReview`
- `SemanticQualityAssessment`
- `RecognizabilityDisposition`

Equivalent names are acceptable if clearer.

Do not put SP06 logic into the SP05 compiler module.

---

# 2. Trusted input binding

Every SP06 assessment must bind to the exact accepted LEVEL_ART artifact it evaluates.

At minimum record and validate:

- trusted artifact digest;
- final logical-grid digest;
- target width and height;
- final used palette IDs/count;
- SP06 diagnostic policy version;
- assessment schema/version.

If semantic intent is supplied, bind it by canonical identity rather than loose caller text. Prefer an optional `SemanticGenerationRequest.digest()` or another existing canonical request identity when available.

Do not mutate or reseal the LEVEL_ART artifact.

Fail closed when the supplied trusted artifact fails its own integrity checks or when carried artifact/grid facts disagree.

---

# 3. Deterministic structural diagnostics

Implement deterministic, dependency-free diagnostics over row-major logical C-ID cells.

At minimum include:

- horizontal adjacent-cell transition count;
- vertical adjacent-cell transition count;
- total adjacency edge count;
- transition density represented canonically without floating-point instability where practical (for example numerator/denominator plus an optional derived display value);
- 4-neighbour connected-component count per used C-ID;
- total connected-component count;
- singleton-component count;
- largest connected-component size per used C-ID;
- largest-component share per used C-ID represented deterministically;
- per-C-ID cell counts;
- total logical cell count.

Requirements:

- row-major deterministic;
- no randomness;
- no network;
- no image libraries required;
- no dependence on EASY/MEDIUM/HARD/VERY_HARD transforms;
- same artifact must always produce byte-identical canonical diagnostics;
- diagnostics must derive from cells rather than caller assertions.

These are diagnostic facts only. Do not create arbitrary pass/fail thresholds in C001.

---

# 4. Recognizability disposition contract

Add an explicit review disposition with at least:

- `UNREVIEWED`
- `ACCEPT`
- `REJECT`

The review must be bound to the exact artifact/assessment identity.

For ACCEPT or REJECT, require a non-empty reviewer/reason record suitable for audit. Keep human-readable notes separate from deterministic structural metrics.

A useful canonical model may include:

- reviewer identity/role label;
- reason code;
- optional notes;
- disposition;
- artifact/assessment digest being reviewed.

Do not add timestamps to canonical identity unless the project already has a deterministic timestamp policy. Avoid nondeterministic current-time values in hashes.

Critical rule:

**Structural diagnostics alone must never silently promote `UNREVIEWED` to `ACCEPT`.**

C001 is a trustworthy review/evidence foundation, not a fake computer-vision recognizer.

---

# 5. Assessment state

Expose an assessment object/report that makes these states unambiguous:

- structurally evaluated but recognizability unreviewed;
- explicitly accepted;
- explicitly rejected.

If you expose a convenience `passes`/`accepted` property, it may be true only for an explicit ACCEPT review bound to the same assessment/artifact identity.

Do not let a caller supply diagnostic values and have them trusted as computed evidence.

Prefer canonical constructors/factories that compute diagnostics internally from the trusted artifact.

---

# 6. Integrity and immutability

Follow the accepted semantic contract style:

- frozen typed values;
- canonical dict/bytes/digest;
- stable schema and policy constants;
- immutable nested mappings/tuples;
- fail-closed validation;
- no public assertion-based trust minting.

You do not need to clone SP05's private-token model automatically. Use it only if necessary and keep the implementation proportionate. The essential requirement is that trusted diagnostic facts are computed from the artifact and cannot be replaced by unchecked caller assertions.

---

# 7. Required tests

Add focused tests proving at least:

1. same trusted artifact produces identical diagnostics, canonical bytes and digest across repeated runs;
2. exact hand-computed horizontal/vertical transition counts on a small legal fixture;
3. exact 4-neighbour component counts on a fixture containing multiple components of the same C-ID;
4. singleton count is correct;
5. largest component sizes/shares are correct;
6. per-color counts sum to total cell count;
7. all diagnostic palette IDs match actual artifact used IDs;
8. diagnostics cannot be minted by supplying false counts if the public API supports any constructor-like surface;
9. assessment rejects mismatched artifact/grid identity;
10. `UNREVIEWED` does not pass;
11. explicit ACCEPT bound to the same assessment passes;
12. explicit REJECT does not pass;
13. ACCEPT/REJECT requires non-empty review evidence;
14. changing review disposition changes review/assessment identity while leaving structural diagnostics identity unchanged;
15. public SP05 artifact behavior remains unchanged;
16. SP05 focused tests remain green.

Use legal production LEVEL_ART fixtures: each axis 20..59 and 3..12 used canonical colors. Do not weaken production contracts simply to make tiny fixtures easier. If hand-computation is easier on a small matrix, test a private pure diagnostic helper on the small matrix while separately proving the public assessment only accepts legal trusted artifacts.

---

# 8. Exports and documentation

Export only the intended public SP06 surface from appropriate package `__init__.py` files.

Update `src/scrubbots_pixel_factory/semantic/README.md` with a short SP06 section explaining:

- structural diagnostics are deterministic facts;
- semantic recognizability remains an explicit review disposition in C001;
- no provider/vision model is called by the gate;
- SP05 compiler output remains unchanged.

Do not rewrite historical SP01-SP05 descriptions unnecessarily.

---

# 9. Verification

Run and record at minimum:

1. new SP06 focused tests;
2. `tests/unit/test_sp05_level_art.py`;
3. relevant semantic contract/normalization/qualification tests;
4. full `python -m pytest -q`;
5. `python -m compileall -q src tests`;
6. package import smoke for the new public SP06 types/functions;
7. module CLI smoke;
8. installed CLI smoke if installed;
9. `git diff --check`;
10. scoped network/credential/provider scan over changed production/tests;
11. `git diff -- TASKS.md` must be empty.

Record failed commands truthfully and correct them rather than hiding them.

---

# 10. Scope prohibitions

Do not begin or modify:

- provider execution/model qualification;
- live Magnific or PixelLab calls;
- CLIP, OCR, external vision APIs or downloaded ML models;
- automated semantic subject recognition claims;
- SP07 reference/style generation;
- SP08 edit/inpaint;
- SP09 Studio UI;
- SP10 weekly batching;
- SP11+ asset production/animation;
- M08/LevelData bridge;
- solver;
- Challenge Score;
- Session Load;
- Frustration Risk;
- M11;
- main-game source;
- root `TASKS.md`.

---

# Builder log requirements

H1 exactly:

`# PAG-SP06-C001 — Semantic Recognizability Gate Contract & Offline Review Foundation`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record:

- start timestamp;
- repository/local root/branch/remote;
- start HEAD/origin/main/divergence;
- pre-existing dirt;
- authorities read;
- exact files changed;
- public contract introduced;
- diagnostic formulas/definitions;
- trust/binding behavior;
- review/disposition behavior;
- every relevant failed/final test result;
- regression results;
- offline/network/provider scan;
- zero provider calls and credits;
- implementation commit SHA and push result;
- truthful main-game access/write statement;
- root `TASKS.md` non-edit statement.

Stop after final push for independent ChatGPT strict audit.

---

# Acceptance criteria

C001 is eligible for PASS only if all are true:

- [ ] SP06 lives outside the SP05 compiler module;
- [ ] assessments bind to exact trusted LEVEL_ART artifact identity;
- [ ] structural diagnostics are computed, deterministic and canonical;
- [ ] transition counts/density are correct;
- [ ] connected-component diagnostics are correct;
- [ ] per-color counts and largest-component evidence are correct;
- [ ] caller assertions cannot mint trusted diagnostic facts;
- [ ] UNREVIEWED never silently passes;
- [ ] ACCEPT/REJECT are explicit and audit-evidenced;
- [ ] review identity is bound to the evaluated assessment/artifact;
- [ ] no heuristic metric is falsely presented as semantic recognition;
- [ ] SP05 product behavior is unchanged;
- [ ] focused and full regressions are green;
- [ ] zero provider calls / zero credits;
- [ ] no root `TASKS.md` edit by builder;
- [ ] no main-game writes;
- [ ] builder log is complete and truthful.
