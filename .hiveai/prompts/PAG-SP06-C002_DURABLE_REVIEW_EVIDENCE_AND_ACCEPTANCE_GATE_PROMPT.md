# PAG-SP06-C002 — Durable Review Evidence & Acceptance Gate
Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`

## Authority

Read completely from GitHub before implementation:

1. root `TASKS.md`;
2. `.hiveai/audits/PAG-SP06-C001_SEMANTIC_RECOGNIZABILITY_GATE_CONTRACT_AND_OFFLINE_REVIEW_FOUNDATION_STRICT_AUDIT.md`;
3. `.hiveai/prompts/PAG-SP06-C001_SEMANTIC_RECOGNIZABILITY_GATE_CONTRACT_AND_OFFLINE_REVIEW_FOUNDATION_PROMPT.md`;
4. current `src/scrubbots_pixel_factory/semantic/quality/core.py`;
5. current `tests/unit/test_sp06_quality.py`;
6. accepted SP05 `level_art.py` and relevant tests only as read-only contract references;
7. `src/scrubbots_pixel_factory/semantic/contracts.py` and normalization provenance contracts;
8. `GOVERNANCE.md` and `AGENTS.md`.

GitHub is authoritative.

Canonical local repository:

`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

Do not use `C:\Users\sekip\Desktop\ScrubBots`.

Do not edit root `TASKS.md`.

Create the matching builder log before product/test edits:

`.hiveai/codex-logs/PAG-SP06-C002_DURABLE_REVIEW_EVIDENCE_AND_ACCEPTANCE_GATE_CODEX_LOG.md`

---

## Mission

Extend the accepted SP06-C001 in-memory quality/review foundation into a durable, deterministic and re-verifiable review-evidence boundary.

C002 must let the project safely persist an explicit recognizability review, reload it later, re-bind it to the exact trusted LEVEL_ART artifact, and answer one narrow downstream question:

**Does this exact artifact have a valid explicit ACCEPT review for this exact structural assessment identity?**

Do not add automatic semantic recognition. Do not add heuristic acceptance thresholds. Do not call a provider or vision model.

SP05 and SP06-C001 architecture are accepted. Preserve them.

---

# 1. Durable evidence record

Add a narrow, versioned evidence representation for one SP06 assessment/review.

A clean design may use a type such as:

- `SemanticQualityEvidenceRecord`
- `SemanticRecognizabilityEvidence`
- equivalent clearly named immutable type.

It must preserve enough canonical information to audit and reconstruct the review without trusting caller assertions.

At minimum the durable evidence must carry or serialize:

- evidence schema/version;
- trusted LEVEL_ART artifact digest;
- final logical-grid digest;
- target width/height;
- final used palette IDs/count;
- diagnostic policy version;
- diagnostics canonical facts or diagnostics canonical digest plus all required facts for strict verification;
- structural assessment identity digest;
- optional semantic-request digest;
- review disposition;
- reviewer;
- reason;
- notes;
- review identity/digest;
- complete assessment identity/digest.

Prefer canonical JSON-compatible dict/bytes and SHA-256 identity consistent with existing semantic contracts.

No nondeterministic timestamps in canonical identity.

---

# 2. Checked export

Provide a canonical export/factory path that accepts an intact `SemanticQualityAssessment` and emits durable evidence.

Required behavior:

- call the assessment's integrity validation;
- derive every exported structural fact from the assessment, not caller assertions;
- preserve `UNREVIEWED`, `ACCEPT`, or `REJECT` exactly;
- export bytes/digest deterministically;
- repeated export of the same assessment must be byte-identical.

Do not permit public construction that can mint arbitrary trusted evidence facts.

---

# 3. Checked reload / re-verification against the exact artifact

Add a strict import/reload function that takes durable evidence plus the trusted `SemanticLevelArtArtifact` being claimed.

The reload path must not trust imported diagnostics or identity strings merely because they are well-formed.

Required process:

1. validate evidence schema/version and canonical field types;
2. validate the supplied LEVEL_ART artifact's own integrity;
3. recompute a fresh SP06 structural assessment from that artifact using the accepted C001 diagnostic policy;
4. if evidence carries a semantic-request digest, bind/recheck the supplied expected semantic request identity when provided;
5. require exact equality for artifact digest, final-grid digest, dimensions, used IDs/count, diagnostic policy, diagnostics identity/facts, and structural assessment identity;
6. reconstruct the review only after structural equality is proven;
7. require the stored review to be bound to the recomputed structural identity;
8. require review/full assessment identities to match the canonical reconstructed values;
9. fail closed on any mismatch.

The successful result should be a fresh trusted `SemanticQualityAssessment` and/or a narrow verified-evidence object. Do not deserialize directly into a trusted object without recomputation.

---

# 4. Strict canonical parser

If C002 accepts JSON bytes/text/dicts, parsing must be strict enough that evidence cannot be ambiguously interpreted.

At minimum reject:

- unsupported schema/version;
- missing required fields;
- wrong field types;
- malformed SHA-256 values;
- unsupported dispositions;
- ACCEPT/REJECT lacking reviewer/reason;
- invalid palette IDs;
- duplicate palette IDs;
- inconsistent used-color count;
- inconsistent dimensions/counts;
- imported diagnostics that disagree with the recomputed artifact diagnostics;
- unknown critical fields if the chosen canonical parser treats schema as closed.

Do not use `eval`, pickle, YAML object construction or unsafe deserialization.

---

# 5. Explicit acceptance gate

Add one narrow helper/facade for downstream callers, for example:

`require_semantic_recognizability_acceptance(...)`

or an equivalent name.

It must:

- validate/reload evidence against the exact supplied trusted LEVEL_ART artifact;
- succeed only when the reconstructed review disposition is explicit `ACCEPT`;
- reject `UNREVIEWED`;
- reject `REJECT`;
- reject evidence for another artifact/grid/assessment;
- return a trusted verified assessment/evidence value, not mutate the LEVEL_ART artifact;
- not create LevelData, start M08, call the solver or integrate gameplay.

Do not add a threshold such as "component count < X means accept".

---

# 6. Semantic intent binding

C001 allows an optional canonical semantic-request identity.

C002 must preserve that exact identity in durable evidence.

If evidence has a non-null semantic-request digest and the caller supplies an expected semantic request object/digest during reload/gating, they must match exactly.

If the project can prove the artifact source provenance already carries the exact generation request digest, you may additionally cross-check it, but do not invent a relationship that the current contracts do not guarantee.

A request digest means only "bound to this canonical intent identity". It is not proof that software understood the subject.

---

# 7. Integrity and immutability

Follow the accepted contract style:

- frozen/immutable public values;
- canonical dict/bytes/digest;
- versioned schemas;
- deterministic ordering;
- private/internal checked constructors if needed;
- fail-closed validation;
- no public assertion-based trust minting.

Do not weaken C001 diagnostics/review seals.

Do not make private C001 helpers part of the public API merely for convenience.

---

# 8. Required adversarial tests

Add focused tests proving at minimum:

1. ACCEPT assessment exports deterministically and reloads to the same trusted canonical assessment identity;
2. REJECT exports/reloads but the acceptance gate rejects it;
3. UNREVIEWED exports/reloads but the acceptance gate rejects it;
4. same assessment exported twice produces identical canonical bytes and digest;
5. artifact digest tamper is rejected;
6. final-grid digest tamper is rejected;
7. target dimension tamper is rejected;
8. used palette ID/count tamper is rejected;
9. diagnostic policy/digest/fact tamper is rejected;
10. structural assessment identity tamper is rejected;
11. review disposition tamper is rejected unless all canonical review/full identities are legitimately reconstructed, and even then gate semantics follow the explicit disposition;
12. reviewer/reason tamper causes identity mismatch or evidence rejection;
13. review identity tamper is rejected;
14. full assessment identity tamper is rejected;
15. evidence for artifact A cannot validate against artifact B;
16. expected semantic-request digest mismatch is rejected when intent binding is present;
17. malformed/unsupported schema/version is rejected;
18. public construction/replace cannot mint trusted evidence if the public type exposes constructor-like fields;
19. accepted SP06-C001 tests remain green;
20. accepted SP05 tests remain green.

Use only offline legal fixtures. No provider calls.

---

# 9. Documentation and exports

Export only the intended durable-evidence and gate surface.

Append a concise SP06-C002 section to `src/scrubbots_pixel_factory/semantic/README.md` explaining:

- persisted evidence is re-verified against the exact trusted artifact;
- reload recomputes structural diagnostics instead of trusting serialized claims;
- only explicit ACCEPT passes the acceptance gate;
- the gate is not computer vision and does not infer recognizability;
- no provider/vision model is called.

Do not rewrite historical sections unnecessarily.

---

# 10. Verification

Run and record at minimum:

1. SP06-C002 focused tests;
2. all SP06-C001 quality tests;
3. SP05 LEVEL_ART focused tests;
4. relevant semantic contract/normalization/qualification tests;
5. full `python -m pytest -q`;
6. `python -m compileall -q src tests`;
7. package import smoke for new public names;
8. module CLI smoke;
9. installed CLI smoke if installed;
10. `git diff --check`;
11. scoped network/credential/provider/unsafe-deserialization scan over changed production/tests;
12. `git diff -- TASKS.md` must be empty.

Record failures and corrections truthfully.

No Magnific call. No PixelLab call. Zero provider credits.

---

# 11. Scope prohibitions

Do not begin or modify:

- automatic image/subject recognizers;
- CLIP/OCR/external vision APIs/downloaded ML models;
- provider execution/model qualification;
- SP07 reference/style generation;
- SP08 edit/inpaint;
- SP09 Studio UI;
- SP10 batching;
- SP11+ asset production/animation;
- M08/LevelData bridge;
- solver;
- Challenge Score;
- Session Load;
- Frustration Risk;
- M11;
- main-game source;
- root `TASKS.md`.

Do not modify accepted SP05 compiler behavior.

---

# Builder log requirements

H1 exactly:

`# PAG-SP06-C002 — Durable Review Evidence & Acceptance Gate`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record:

- start timestamp;
- repository/local root/branch/remote;
- starting HEAD/origin/main/divergence;
- pre-existing dirt;
- authorities read;
- exact files changed;
- durable evidence schema and canonical representation;
- export behavior;
- reload/recomputation behavior;
- acceptance gate behavior;
- semantic-request binding behavior;
- all adversarial tests added;
- every materially relevant failed/final test result;
- regression results;
- offline/network/provider/unsafe-deserialization scan;
- zero provider calls and credits;
- implementation commit SHA and implementation push result;
- truthful main-game access/write statement;
- root `TASKS.md` non-edit statement.

Stop after final push for independent ChatGPT strict audit.

---

# Acceptance criteria

C002 is eligible for PASS only if all are true:

- [ ] durable evidence is deterministic, versioned and immutable;
- [ ] trusted export derives facts from an intact C001 assessment;
- [ ] reload validates the supplied trusted LEVEL_ART artifact;
- [ ] reload recomputes C001 diagnostics rather than trusting serialized diagnostic assertions;
- [ ] artifact/grid/dimension/used-ID/policy/diagnostic/structural identity all cross-bind exactly;
- [ ] review identity is reconstructed against the recomputed structural identity;
- [ ] full assessment identity is reverified;
- [ ] malformed or tampered evidence fails closed;
- [ ] artifact A evidence cannot validate against artifact B;
- [ ] semantic-request identity is preserved and checked when present;
- [ ] explicit ACCEPT is the only disposition that passes the gate;
- [ ] UNREVIEWED and REJECT never pass;
- [ ] no heuristic structural threshold becomes semantic recognition;
- [ ] no public trust-minting/deserialization shortcut is added;
- [ ] accepted SP06-C001 behavior remains green;
- [ ] accepted SP05 behavior remains green;
- [ ] zero provider calls / zero credits;
- [ ] no root `TASKS.md` builder edit;
- [ ] no main-game writes;
- [ ] builder log is complete and truthful.
