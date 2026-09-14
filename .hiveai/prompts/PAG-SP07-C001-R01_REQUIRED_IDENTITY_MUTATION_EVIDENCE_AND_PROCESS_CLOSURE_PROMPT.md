# PAG-SP07-C001-R01 — Required Identity-Mutation Evidence & Process Closure
Document role: CODEX REMEDIATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`

## Authority

Read completely from GitHub before any R01 edit:

1. root `TASKS.md`;
2. `.hiveai/audits/PAG-SP07-C001_REFERENCE_STYLE_GENERATION_CONTRACT_AND_DETERMINISTIC_PLAN_FOUNDATION_STRICT_AUDIT.md`;
3. `.hiveai/prompts/PAG-SP07-C001_REFERENCE_STYLE_GENERATION_CONTRACT_AND_DETERMINISTIC_PLAN_FOUNDATION_PROMPT.md`;
4. `.hiveai/codex-logs/PAG-SP07-C001_REFERENCE_STYLE_GENERATION_CONTRACT_AND_DETERMINISTIC_PLAN_FOUNDATION_CODEX_LOG.md`;
5. current `src/scrubbots_pixel_factory/semantic/generation/plan.py`;
6. current `tests/unit/test_sp07_generation_plan.py`;
7. current canonical `SemanticGenerationRequest` and `ImageInputDescriptor` contracts;
8. `GOVERNANCE.md` and `AGENTS.md`.

GitHub is authoritative.

Canonical local repository:

`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

Do not use `C:\Users\sekip\Desktop\ScrubBots`.

Do not edit root `TASKS.md`.

Before any R01 source/test edit, create and verify this matching remediation log:

`.hiveai/codex-logs/PAG-SP07-C001-R01_REQUIRED_IDENTITY_MUTATION_EVIDENCE_AND_PROCESS_CLOSURE_CODEX_LOG.md`

The original C001 builder log is historical evidence. Do not rewrite it or conceal its recorded process-ordering incident.

---

## Mission

Close only the two missing acceptance tests from the SP07-C001 strict audit and demonstrate correct R01 process chronology.

The C001 product implementation is retained. Do not redesign or refactor `semantic/generation/plan.py` unless one of the literal new tests unexpectedly proves the current product behavior is wrong.

No provider execution is authorized. Spend zero Magnific/PixelLab credits.

---

# 1. Explicit REFERENCE content-SHA mutation proof

Add a focused test using the existing legal canonical request fixture.

Required proof:

1. build the baseline canonical request and plan;
2. replace exactly one `REFERENCE` descriptor with a descriptor that preserves its REFERENCE role and the same relevant metadata but has a different valid `content_sha256`;
3. preserve request seed, candidate count, provider selection and all unrelated fields;
4. assert the changed request digest differs from the baseline request digest;
5. assert the changed plan digest and canonical bytes differ from baseline;
6. assert the changed REFERENCE input-binding digest/content identity differs;
7. preferably assert the deterministic candidate IDs differ because they bind request identity;
8. do not require variant seed values to differ when the request seed itself is unchanged.

Do not weaken or alter local-path exclusion behavior.

---

# 2. Explicit INIT-strength mutation proof

Add a focused test using a request that already has a valid INIT descriptor.

Required proof:

1. build baseline request/plan;
2. change only `init_strength` to another legal value while keeping the same INIT descriptor and all other canonical request fields unchanged;
3. assert baseline and changed request digests differ;
4. assert baseline and changed plan digests/canonical bytes differ;
5. assert the plan preserves the changed `init_strength` exactly;
6. do not assert the derived variant seeds must change when the canonical request seed remains unchanged.

No product code change is expected.

---

# 3. Process chronology closure

The original C001 cycle violated the prompt ordering by creating its builder log after initial source/test edits. That historical fact must remain visible.

For R01:

- create the R01 builder log before any R01 edit;
- record timestamp, canonical repository/local root/branch/remote;
- record starting local HEAD and `origin/main`;
- record starting divergence;
- record pre-existing worktree dirt;
- record authorities read;
- only then edit tests/source if necessary.

Do not claim the original C001 ordering was compliant.

---

# 4. Preserve accepted C001 implementation

Do not alter unless a new literal test exposes a genuine defect:

- canonical `SemanticGenerationRequest` source-truth binding;
- content-addressed REFERENCE / STYLE / INIT / COLOR_REFERENCE bindings;
- local-path exclusion from canonical descriptor identity;
- deterministic input ordering;
- duplicate-reference rejection;
- deterministic project-RNG variant seed derivation;
- deterministic candidate IDs;
- provider/model/workflow/config identity;
- LEVEL_ART / ASSET_ART separation;
- private sealing/fingerprints;
- zero-execution provider-neutral plan semantics.

Do not begin live provider generation, SP08+, Studio, batching, M08, solver, M11 or main-game work.

---

# 5. Verification

Run and record at minimum:

1. `python -m pytest -q tests/unit/test_sp07_generation_plan.py`;
2. combined SP07 + accepted SP06 quality/evidence + SP05 LEVEL_ART + relevant SP01/SP02/SP03/SP04 semantic/provider regression using only files that exist;
3. `python -m pytest -q`;
4. `python -m compileall -q src tests`;
5. package import smoke for SP07 public names;
6. module CLI help smoke;
7. installed CLI help smoke if installed;
8. `git diff --check`;
9. scoped provider/network/credential/generation-runtime scan over changed files;
10. `git diff -- TASKS.md` must be empty.

If any command fails or is initially wrong, record it truthfully and correct it rather than hiding it.

No Magnific call. No PixelLab call. No image generation. Zero provider credits.

---

# 6. Publication

The R01 builder log must record:

- exact files changed;
- both literal identity-mutation tests and their assertions;
- whether production code changed and why;
- all materially relevant failed/final test results;
- focused/combined/full regression results;
- compile/import/CLI/diff/scoped-scan results;
- zero provider calls / zero credits;
- root `TASKS.md` non-edit statement;
- no main-game writes;
- implementation/test-evidence commit SHA;
- successful implementation push result.

Preferred publication sequence:

1. create/verify R01 log first;
2. add tests;
3. run verification;
4. commit and push test/evidence implementation;
5. capture implementation commit SHA/push result;
6. append those facts to R01 log;
7. publish final log-only commit and push;
8. stop for independent ChatGPT strict audit.

Do not claim ChatGPT acceptance.

---

# Acceptance criteria

C001-R01 is eligible for PASS only if all are true:

- [ ] R01 log existed before R01 edits;
- [ ] one REFERENCE content-SHA mutation explicitly changes request identity;
- [ ] the REFERENCE content-SHA mutation explicitly changes plan identity/canonical bytes;
- [ ] changed REFERENCE binding identity is directly proven;
- [ ] one INIT-strength-only mutation explicitly changes request identity;
- [ ] the INIT-strength-only mutation explicitly changes plan identity/canonical bytes;
- [ ] changed INIT strength is preserved exactly in the plan;
- [ ] tests do not incorrectly require non-seed request changes to alter project-RNG variant seeds;
- [ ] current C001 product architecture remains unchanged unless a literal test exposes a real defect;
- [ ] focused and full regressions are green;
- [ ] zero provider calls / zero credits;
- [ ] no root `TASKS.md` builder edit;
- [ ] no main-game writes;
- [ ] finalized R01 builder log contains implementation commit SHA and push result;
- [ ] Codex stops after final push for ChatGPT strict audit.
