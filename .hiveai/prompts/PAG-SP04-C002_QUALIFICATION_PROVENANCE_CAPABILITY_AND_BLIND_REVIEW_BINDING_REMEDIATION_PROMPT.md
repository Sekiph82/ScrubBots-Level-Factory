# PAG-SP04-C002 — Qualification Provenance, Capability & Blind-Review Binding Remediation
Document role: CODEX REMEDIATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`

## Authority

Read from GitHub before any source/test edit:

1. root `TASKS.md` — ONLY current project-status tracker;
2. `.hiveai/audits/PAG-SP04-C001_SEMANTIC_QUALIFICATION_HARNESS_BENCHMARK_CORPUS_AND_COST_SAFE_PROVIDER_MATRIX_STRICT_AUDIT.md`;
3. `.hiveai/prompts/PAG-SP04-C001_SEMANTIC_QUALIFICATION_HARNESS_BENCHMARK_CORPUS_AND_COST_SAFE_PROVIDER_MATRIX_PROMPT.md`;
4. `.hiveai/codex-logs/PAG-SP04-C001_SEMANTIC_QUALIFICATION_HARNESS_BENCHMARK_CORPUS_AND_COST_SAFE_PROVIDER_MATRIX_CODEX_LOG.md`;
5. `.hiveai/audits/PAG-SP03-C003_PROVENANCE_SEAL_AND_CONSTRUCTION_INTEGRITY_CLOSURE_STRICT_AUDIT.md`;
6. `src/scrubbots_pixel_factory/semantic/normalization/core.py` accepted SP03 typed/sealed contracts;
7. accepted SP01/SP02 provider contracts;
8. `AGENTS.md`, `GOVERNANCE.md`, `CLAUDE.md`.

Do not use legacy hidden `.hiveai` tracker/control-plane files as current authority.

Do not edit root `TASKS.md`.

Create the matching C002 builder log **before any C002 source/test/doc edit**. Do not repeat the C001 chronology violation.

## Mission

Close exactly the C001 findings:

- `F-PAG-SP04-C001-001` — plan capability requirements are not fail-closed;
- `F-PAG-SP04-C001-002` — PASS compatibility evidence is caller/self-asserted rather than checked from SP03 typed artifacts;
- `F-PAG-SP04-C001-003` — attempt lifecycle and exact cross-provenance binding are incomplete;
- `F-PAG-SP04-C001-004` — blind-review stable-ID binding is not enforced as an invariant;
- `F-PAG-SP04-C001-005` — terminal qualification summary semantics are incorrect;
- `F-PAG-SP04-C001-006` — process-only chronology issue; comply correctly this cycle.

This remains an **offline remediation cycle**.

Do not call Magnific or PixelLab. Do not spend credits. Do not begin live qualification, SP05, SP06, Studio UI or M11.

---

# 1. Plan capability fail-closed enforcement

`BenchmarkCase.requires_reference` and `BenchmarkCase.requires_style` already exist.

`ProviderWorkflowSpec.supports_reference` and `ProviderWorkflowSpec.supports_style` already exist.

`build_qualification_plan()` must reject a selected case/provider matrix combination when the case requires a capability the selected matrix cell does not support.

At minimum:

- `requires_reference=True` + `supports_reference=False` → fail closed with `SemanticContractError`;
- `requires_style=True` + `supports_style=False` → fail closed;
- a STYLE-required PIXFLUX plan → fail closed;
- an eligible STYLE-required BITFORGE plan → construct successfully and retain the STYLE requirement in deterministic plan identity;
- unsupported combinations must never be silently omitted or silently downgraded.

Also harden `QualificationPlan`/`QualificationPlanEntry` integrity so a directly constructed or reconstructed plan cannot pass merely because the entry count is correct.

Every entry must be exactly bound to:

- one existing case ID/digest;
- one existing provider matrix ID;
- the exact provider ID/model-or-engine/workflow from that matrix cell;
- the plan target dimensions;
- an attempt index in the exact expected domain;
- no missing/duplicate Cartesian cell/attempt combination.

Equivalent deterministic validation is acceptable. Do not rely only on tuple position.

---

# 2. Consume SP03 typed/sealed evidence instead of free-form PASS strings

The qualification layer must not create a second weaker provenance system above accepted SP03.

Use the existing typed objects:

- `SemanticRawArtifact`;
- `SemanticNormalizationRequest`;
- `SemanticNormalizedArtifact`;
- their accepted digest/provenance/report identities.

Implement checked construction/factory paths for raw-import and normalization qualification evidence.

A PASS/verified qualification evidence record must be derivable only from typed SP03 objects whose own invariants already pass.

A plain caller must not be able to create an arbitrary review-ready PASS chain by supplying fake 64-hex strings and `compatibility=PASS`.

Acceptable designs include:

- checked classmethods with non-caller-resettable `init=False` construction seals similar to SP03;
- internal factories that create sealed evidence from typed SP03 artifacts;
- a separate verified-evidence type that cannot be forged through ordinary public dataclass constructor/`dataclasses.replace()` paths.

Do not weaken SP03 seals.

Do not use secrets/tokens as security credentials. This is local construction-integrity, not cryptographic authentication.

## Required exact evidence binding

Verified raw evidence must derive, where available, from the exact `SemanticRawArtifact`:

- raw SHA-256;
- media type;
- returned dimensions;
- local raw-artifact digest;
- provider candidate/result digest/identity used by the local raw artifact;
- provider ID;
- provider version;
- workflow version;
- model identity;
- semantic request digest.

Verified normalization evidence must derive from the exact `SemanticNormalizedArtifact` and bind:

- `source_raw_artifact_digest` == verified local raw-artifact digest;
- input raw SHA == verified raw SHA;
- normalization request digest;
- normalized artifact digest;
- target dimensions;
- policy version;
- resampler / exact-size facts from the accepted normalization report;
- normalized RGBA identity/hash where useful for technical comparison.

Raw SHA equality alone is **not sufficient** because the same bytes can exist under different provider/source provenance.

---

# 3. Exact plan-entry → attempt → raw → normalized provenance chain

Harden `QualificationAttemptRecord` so advanced lifecycle states cannot be assembled from duplicated free-form strings that merely look consistent.

Prefer a checked creation path from an actual `QualificationPlan`/`QualificationPlanEntry`, then typed transition/update paths.

The attempt must preserve an immutable binding to the exact plan entry/case/provider matrix identity.

At minimum prove exact equality for:

- plan/entry identity;
- case identity;
- provider matrix identity;
- provider ID;
- provider version;
- model/engine;
- workflow version;
- target dimensions;
- raw provider candidate/result identity;
- raw artifact digest;
- raw SHA;
- semantic request digest;
- normalization request digest;
- normalized artifact digest.

No silent provider/model/workflow substitution.

If a provider-specific operational ID is not part of the accepted deterministic raw artifact identity, do not invent one. Use the accepted local provider-candidate/result identity from SP02/SP03 and keep mutable UI/account IDs separate.

---

# 4. Lifecycle prerequisite closure

Make lifecycle prerequisites monotonic and fail closed.

Required minimum semantics:

- `PLANNED`: no raw/normalization evidence required;
- `RAW_PROVIDER_CAPTURED`: may record provider capture state, but cannot imply local compatibility;
- `RAW_IMPORT_VERIFIED`: requires checked raw-import compatibility PASS;
- `NORMALIZED`: requires checked raw-import PASS + checked normalization PASS bound to the same raw artifact;
- `READY_FOR_BLIND_REVIEW`: requires all NORMALIZED prerequisites + pending owner disposition;
- `OWNER_ACCEPTED`: requires all review-ready technical prerequisites + `OWNER_ACCEPTED` disposition;
- `OWNER_REJECTED`: requires all review-ready technical prerequisites + `OWNER_REJECTED` disposition.

It must be impossible to construct `OWNER_ACCEPTED` or `OWNER_REJECTED` with raw compatibility FAIL/NOT_ATTEMPTED.

Do not require project tracker mutation from these local data states.

---

# 5. Blind-review stable binding closure

The owner-facing review package must remain metadata-blind while its hidden mapping becomes invariant-safe.

## Stable mapping

`MetadataBlindReviewPack` validation must prove by stable identifiers, not list position, that:

- every visible review item references exactly one hidden attempt;
- every hidden attempt in the pack is referenced exactly once;
- `item.hidden_attempt_id` exists in hidden attempts;
- `item.review_id` matches the review binding recorded for that hidden attempt;
- duplicate or orphan visible/hidden records fail closed;
- reversing/reordering hidden attempt tuples cannot corrupt attribution because joins are ID-based.

Direct construction and `dataclasses.replace()` sensitivity must be covered, not only the happy-path factory.

## Stable review identity

Do not derive a review ID from an identity that changes when `review_item_id` is subsequently installed.

Create an immutable pre-review/binding identity, for example `review_binding_digest()`, that excludes:

- `review_item_id` itself;
- cost/usage;
- owner disposition;
- mutable audit/timestamp/UI metadata.

It should include the exact deterministic plan/provider/raw/normalized identity needed to bind the image being reviewed.

Derive deterministic ordering/shuffle and review IDs from that stable identity + explicit review seed.

Repeated construction from equivalent records, including records already carrying the same review binding, must be idempotent.

---

# 6. Qualification summary semantics

Correct `summarize_qualification()` so terminal owner states are represented coherently.

At minimum:

- one or more pending `READY_FOR_BLIND_REVIEW` candidates must produce a pending-review status unless a deliberately documented terminal policy says otherwise;
- accepted terminal records must never summarize as `NO_READY_CANDIDATES`;
- rejected terminal records must never summarize as `NO_READY_CANDIDATES` merely because they are no longer in READY lifecycle;
- accepted/rejected/pending counts must remain internally consistent;
- no summary state may mark a project milestone/default provider accepted by itself.

A small explicit `MIXED` state is acceptable if needed, but keep semantics deterministic and tested.

---

# 7. Required adversarial tests

Add focused tests that prove all of the following.

### Plan/capability

1. default 15-case × 3-cell plan remains deterministic and finite;
2. STYLE-required PIXFLUX plan fails closed;
3. STYLE-required BITFORGE plan succeeds and retains requirement semantics;
4. REFERENCE-required unsupported matrix cell fails closed;
5. direct/reconstructed plan with wrong case ID/provider matrix ID/provider/model/workflow/attempt index fails;
6. duplicate or missing plan cell/attempt fails.

### Typed SP03 evidence

7. a real synthetic `SemanticRawArtifact` + successful SP03 normalization can create verified qualification evidence;
8. arbitrary free-form hex strings cannot mint verified PASS evidence through ordinary constructor/replace paths;
9. changed raw-artifact digest with same raw SHA fails;
10. changed raw SHA fails;
11. changed provider ID/version/workflow/model/request digest fails;
12. changed normalization request digest/artifact digest fails;
13. raw workflow mismatch against attempt fails;
14. model mismatch against attempt fails;
15. plan-entry/provider-matrix mismatch against attempt fails.

### Lifecycle

16. `RAW_IMPORT_VERIFIED` with NOT_ATTEMPTED/FAIL raw compatibility fails;
17. `NORMALIZED` without verified raw+normalization chain fails;
18. `READY_FOR_BLIND_REVIEW` without verified chain fails;
19. `OWNER_ACCEPTED` with raw compatibility FAIL/NOT_ATTEMPTED fails;
20. `OWNER_REJECTED` with raw compatibility FAIL/NOT_ATTEMPTED fails.

### Blind review

21. visible item exposes no provider/model/seed/cost/private URL;
22. hidden manifest retains exact provider/workflow/raw/normalized identity;
23. stable review ID is reproducible and idempotent;
24. changing cost/usage does not change review binding identity;
25. changing exact normalized/raw/provider identity does change review binding identity;
26. malformed item.hidden_attempt_id fails direct pack construction;
27. mismatched item.review_id ↔ hidden attempt review binding fails;
28. duplicate/orphan visible or hidden records fail;
29. reordering hidden attempts does not change correct ID-based attribution.

### Summary

30. pending-only summary is pending;
31. accepted-only summary is owner accepted, never NO_READY;
32. rejected-only summary is owner rejected, never NO_READY;
33. mixed states follow the documented deterministic rule.

### Regression/security

34. existing C001 corpus/cost/evidence-reference tests remain green;
35. SP01-SP04 focused suite green;
36. full repository regression green;
37. compileall/import/CLI/diff check green;
38. no provider/network/credential/browser execution;
39. no Magnific/PixelLab credits spent.

---

# 8. Preserve accepted C001 work

Do not discard the useful C001 foundation.

Preserve unless a finding requires a narrow compatible change:

- 15-subject benchmark corpus and stable IDs;
- ASSET_ART 24x24 baseline;
- explicit Magnific/PIXFLUX/BITFORGE matrix concept;
- provider-neutral architecture;
- finite plan limit;
- cost/usage separation from deterministic identity;
- public positive/negative evidence references;
- no automatic recognizability oracle;
- no LEVEL_ART rule leakage into ASSET_ART.

Do not rewrite SP01-SP03 accepted architecture.

---

# 9. Security / scope rules

Forbidden in C002:

- live Magnific call;
- live PixelLab call;
- credit spend;
- browser automation;
- private/undocumented provider endpoints;
- reading or logging secrets;
- selecting a default production provider/model/workflow;
- starting SP04 live benchmark generation;
- starting SP05/SP06;
- Studio UI;
- weekly paid batches;
- M11;
- editing root `TASKS.md`;
- writing the independent audit.

No new dependency is required unless strictly necessary. Prefer stdlib + existing project types.

---

# 10. Builder log

Create **before any C002 source/test/doc edit**:

`.hiveai/codex-logs/PAG-SP04-C002_QUALIFICATION_PROVENANCE_CAPABILITY_AND_BLIND_REVIEW_BINDING_REMEDIATION_CODEX_LOG.md`

Exact H1:

`# PAG-SP04-C002 — Qualification Provenance, Capability & Blind-Review Binding Remediation`

Role line:

`Document role: CODEX BUILDER LOG`

Record chronologically:

- start timestamp;
- repository/branch/start HEAD/origin HEAD/divergence after `git fetch origin`;
- preserved user-owned dirt;
- authority files read;
- confirmation that the log exists before implementation edits;
- exact design for checked SP03-derived evidence;
- exact plan capability enforcement;
- exact plan-entry/attempt provenance binding;
- exact lifecycle prerequisite rules;
- exact blind-review stable-ID design;
- summary semantics;
- all focused failures/corrections;
- focused SP04 result;
- SP01-SP04 focused regression;
- full repository regression;
- compile/import/CLI/offline/network/secret checks;
- exact files changed;
- implementation commit/push;
- final local HEAD/origin/main equality and divergence `0 0` after final log publication.

If a final log commit necessarily advances HEAD after a prior checkpoint, explicitly record the final log commit SHA in a subsequent closure line/commit or otherwise make the terminal publication state truthful. Do not leave the log claiming a pre-log-commit SHA is the repository terminal HEAD.

---

# 11. Stop rule

After implementation and verification:

1. complete and commit the builder log;
2. commit/push all C002 work to `main`;
3. fetch `origin` and verify local HEAD == `origin/main` with divergence `0 0`;
4. STOP for independent ChatGPT audit.

Do not begin SP04 live qualification or any later milestone.