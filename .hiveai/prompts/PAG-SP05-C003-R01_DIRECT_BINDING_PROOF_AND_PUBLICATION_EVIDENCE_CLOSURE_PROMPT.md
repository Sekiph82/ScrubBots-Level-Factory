# PAG-SP05-C003-R01 — Direct Binding Proof & Publication Evidence Closure
Document role: CODEX REMEDIATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`

## Authority

Read completely from GitHub before editing:

1. root `TASKS.md`;
2. `.hiveai/audits/PAG-SP05-C003_TRUSTED_REPORT_BINDING_AND_ACCEPTANCE_EVIDENCE_CLOSURE_STRICT_AUDIT.md`;
3. `.hiveai/prompts/PAG-SP05-C003_TRUSTED_REPORT_BINDING_AND_ACCEPTANCE_EVIDENCE_CLOSURE_PROMPT.md`;
4. `.hiveai/codex-logs/PAG-SP05-C003_TRUSTED_REPORT_BINDING_AND_ACCEPTANCE_EVIDENCE_CLOSURE_CODEX_LOG.md`;
5. current `src/scrubbots_pixel_factory/semantic/normalization/level_art.py`;
6. current `tests/unit/test_sp05_level_art.py`;
7. `docs/LEVEL_ART_SEMANTIC_NORMALIZATION_OWNER_DECISION_V02.md`;
8. `GOVERNANCE.md` and `AGENTS.md`.

GitHub is authoritative.

Canonical local mirror:

`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

Do not use `C:\Users\sekip\Desktop\ScrubBots` as the implementation repository.

Do not edit root `TASKS.md`.

Do not modify the separate `Sekiph82/Scrubbots` repository. If its owner-decision document is read as authority, record that truthfully as read-only access rather than claiming the repository was not accessed.

Create the matching remediation log before test edits:

`.hiveai/codex-logs/PAG-SP05-C003-R01_DIRECT_BINDING_PROOF_AND_PUBLICATION_EVIDENCE_CLOSURE_CODEX_LOG.md`

---

## Mission

Close only the two acceptance-evidence defects from the C003 strict audit.

C003 product code is retained. Do not redesign or refactor the LEVEL_ART compiler.

The current explicit invariant must remain:

`report.raw_sha256 == artifact.raw_sha256 == source_provenance.raw_sha256`

No provider call is authorized. Spend zero Magnific/PixelLab credits.

---

# 1. Directly prove the raw-SHA artifact-binding invariant

The current C003 tamper test changes a field on an already sealed report. That proves fingerprint tamper detection, but the fingerprint failure masks the new artifact/report raw-SHA equality check.

Add a focused test that reaches the binding check directly.

Required proof pattern:

1. compile a legitimate LEVEL_ART artifact from a legitimate `SemanticRawArtifact` + `SemanticLevelArtRequest`;
2. obtain the legitimate report stage values;
3. using test-only/internal access only, create a report whose token/fingerprint are valid but whose `raw_sha256` is deliberately different from the legitimate raw SHA;
4. all other report fields must remain coherent with the legitimate artifact;
5. prove the forged report passes its own report integrity/fingerprint validation before artifact construction;
6. pass the forged report through the canonical internal artifact construction/validation boundary using the legitimate raw artifact, request, logical cells, majority digest and snapped digest;
7. assert construction fails closed with `SemanticLevelArtError` and the artifact binding failure code (`INVALID_ARTIFACT`).

The preferred narrow test approach is to import the private module-level `_build_report` and `_build_artifact` helpers directly in the test module. Private test-only imports are allowed for this adversarial proof.

Do not expose a new production/public forging or sealing API.

Do not weaken the token/fingerprint model.

Do not change production code unless this direct test unexpectedly reveals that the current one-line equality check does not fail closed as expected. If product code must change, keep the fix minimal and document why.

---

# 2. Make 13..16 repeat determinism literal

The existing C003 test already proves EASY/VERY_HARD lane-equivalent results for 13, 14, 15 and 16 used colors.

While touching this focused test, add an explicit same-lane repeated execution for every parametrized color count and assert:

- first same-lane result == repeated same-lane result;
- first same-lane details == repeated same-lane details;
- lane-equivalent result/details remain identical;
- final distinct count remains exactly 12;
- final IDs remain a subset of snapped input IDs;
- no new C-ID is introduced.

Do not change the weighted subset/remap algorithm.

---

# 3. Publication evidence must be complete and truthful

The original C003 builder log remains historical evidence. Do not rewrite it.

The C003-R01 builder log must explicitly record:

- start timestamp;
- canonical repo/local root/branch/remote;
- starting local HEAD;
- starting `origin/main`;
- starting divergence;
- pre-existing dirt;
- authorities read;
- exact files changed;
- direct raw-SHA binding proof design and result;
- exact 13/14/15/16 repeat/lane evidence change;
- every relevant failed and final test result;
- focused regression;
- combined relevant regression;
- full repository regression;
- compileall;
- package import smoke;
- CLI smoke;
- `git diff --check`;
- scoped network/credential/provider scan;
- zero provider calls and zero provider credits;
- explicit statement that root `TASKS.md` was not edited;
- explicit statement that `Sekiph82/Scrubbots` received no writes;
- truthful wording for any read-only main-game authority access;
- implementation commit SHA;
- implementation push result.

Publication sequence to avoid the C003 placeholder problem:

1. create the R01 log locally before edits;
2. implement the test-only remediation;
3. run verification;
4. commit the test/evidence implementation and push it;
5. capture that implementation commit SHA and push result;
6. append those facts to the R01 log;
7. make a final log-only publication commit and push it;
8. stop for ChatGPT audit.

The log cannot contain the SHA of the commit that contains the log’s final bytes without creating a self-reference loop. That final log-publication SHA may be reported in the handoff. The log itself must at least contain the prior implementation commit SHA and its successful push result.

Do not claim ChatGPT acceptance.

---

# 4. Preserve accepted architecture exactly

Do not alter:

- CELL_MAJORITY_V1;
- PALETTE_SNAP_V1;
- C01..C16 palette values/order;
- production dimensions 20..59 per axis;
- rectangle legality;
- production used-color envelope 3..12;
- <3 fail-closed behavior;
- >12 exact weighted subset/remap behavior;
- source provenance semantics;
- public `SemanticLevelArtArtifact.from_compilation()` recomputation behavior;
- ASSET_ART;
- strict PNG;
- provider adapters.

Do not begin or modify:

- M08/LevelData bridge;
- solver;
- Challenge Score;
- Session Load;
- Frustration Risk;
- SP06;
- Studio feature work;
- publishing/control-plane implementation;
- weekly generation;
- M11;
- main-game source;
- root `TASKS.md`.

---

# 5. Verification

Run and record at minimum:

1. `python -m pytest -q tests/unit/test_sp05_level_art.py`;
2. corrected combined SP01-SP05 + canonical palette/color/difficulty/production + SP03 + accepted SP04 PNG/qualification regression set using only files that actually exist in the repository;
3. `python -m pytest -q`;
4. `python -m compileall -q src tests`;
5. package import smoke;
6. module CLI help smoke;
7. installed CLI help smoke if installed in the canonical environment;
8. `git diff --check`;
9. scoped offline/network/credential scan over changed production/test files;
10. `git diff -- TASKS.md` must be empty.

If any command is initially wrong, record it truthfully and correct the command without hiding the failure.

---

# Acceptance criteria

C003-R01 is eligible for PASS only if all are true:

- [ ] a fingerprint-valid wrong-raw-SHA report is constructed only through test-only/internal access;
- [ ] that report passes its own integrity check before artifact construction;
- [ ] artifact construction rejects it specifically at the report/artifact/source raw-SHA binding boundary;
- [ ] no public trust-minting API is added;
- [ ] same-lane repeated 13/14/15/16 reductions are identical;
- [ ] EASY/VERY_HARD lane-equivalent 13/14/15/16 reductions remain identical;
- [ ] every 13..16 case finishes with exactly 12 used colors;
- [ ] no new C-ID is introduced;
- [ ] C003 product architecture remains unchanged unless the direct test exposes a real defect;
- [ ] focused and full regressions are green;
- [ ] zero provider calls / zero credits;
- [ ] root `TASKS.md` is untouched by Codex;
- [ ] no main-game writes occur;
- [ ] the C003-R01 builder log contains the implementation commit SHA and implementation push result;
- [ ] builder log wording is internally consistent and truthful;
- [ ] Codex stops after final push for independent ChatGPT strict audit.
