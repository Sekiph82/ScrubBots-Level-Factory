# PAG-SP04-C004 — Review Entry Proof & Provider Capture Evidence Closure
Document role: CODEX REMEDIATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`

## Authority

Read from GitHub before any source/test edit:

1. root `TASKS.md` — ONLY current project-status tracker;
2. `.hiveai/audits/PAG-SP04-C003_REQUEST_TO_CASE_BINDING_ATTEMPT_SEAL_AND_REVIEW_ATTRIBUTION_CLOSURE_STRICT_AUDIT.md`;
3. `.hiveai/prompts/PAG-SP04-C003_REQUEST_TO_CASE_BINDING_ATTEMPT_SEAL_AND_REVIEW_ATTRIBUTION_CLOSURE_PROMPT.md`;
4. `.hiveai/codex-logs/PAG-SP04-C003_REQUEST_TO_CASE_BINDING_ATTEMPT_SEAL_AND_REVIEW_ATTRIBUTION_CLOSURE_CODEX_LOG.md`;
5. accepted SP01 semantic request/provider contracts;
6. accepted SP02 typed provider result/candidate contracts;
7. accepted SP03 typed/sealed raw and normalization contracts;
8. current SP04 qualification source/tests;
9. `AGENTS.md`, `GOVERNANCE.md`, `CLAUDE.md`.

Do **not** use legacy hidden `.hiveai` tracker/control-plane files as authority and do not read them merely to reconstruct current task state. Root `TASKS.md` is the tracker.

Do not edit root `TASKS.md`.

Create the matching C004 builder log **before any C004 source/test/doc edit**.

## Mission

Close exactly the remaining C003 findings:

- `F-PAG-SP04-C003-001` — terminal owner disposition can use an arbitrary free-form review string instead of proof of metadata-blind review entry;
- `F-PAG-SP04-C003-002` — `RAW_PROVIDER_CAPTURED` can exist without typed returned-provider model/result evidence;
- `F-PAG-SP04-C003-003` — process-only builder-log chronology issue; comply correctly this cycle.

This is the final bounded offline contract-remediation cycle before SP04 live qualification may be considered.

Do not call Magnific or PixelLab. Do not spend credits. Do not begin live qualification, SP05, SP06, Studio UI, weekly batches or M11.

---

# 1. Replace free-form review proof with checked review-entry evidence

Current `review_item_id: str | None` is useful as a visible identifier but is not sufficient as proof that an attempt actually entered the deterministic metadata-blind review protocol.

Introduce a small immutable/sealed concept such as:

`QualificationReviewBinding`

or

`ReviewEntryEvidence`

Exact name may differ.

It must be checked construction only. Ordinary public constructor/`dataclasses.replace()` must not be able to mint/reissue valid review proof.

The checked review binding must be derived from an exact trusted `READY_FOR_BLIND_REVIEW` attempt plus an explicit review seed/protocol version and must bind at minimum:

- attempt ID;
- stable pre-review attempt binding digest;
- plan digest;
- plan entry ID;
- case ID + case digest;
- canonical blind-review subject label;
- normalized target dimensions;
- normalized artifact identity/hash;
- request binding digest;
- provider/raw/normalized deterministic identity indirectly through the attempt binding digest;
- typed review seed;
- deterministic expected review ID;
- review-pack/protocol version.

Cost, timestamp/UI metadata and owner disposition must remain outside the deterministic review binding identity.

## Required terminal rule

`OWNER_ACCEPTED` and `OWNER_REJECTED` must require checked/sealed review-entry evidence, not merely `review_item_id != None`.

A caller must not be able to do this successfully:

```python
record.with_review_binding("review-fixed").with_lifecycle(OWNER_ACCEPTED, ...)
```

or any equivalent arbitrary-string path.

You may remove/replace the free-form `with_review_binding(str)` API or make it internal/checked. If a public review-binding method remains, it must accept sufficient typed inputs to deterministically derive and validate the expected binding; it must not trust a supplied review ID.

`review_item_id`, if retained, must be derived from the sealed review binding and exact expected review ID.

## Review pack integration

`build_metadata_blind_review_pack()` must construct or consume the checked review-entry evidence for each candidate.

`MetadataBlindReviewPack` direct construction must continue to prove:

- one-to-one visible↔hidden mapping;
- deterministic sequence;
- exact expected review ID;
- subject label;
- target dimensions;
- hidden attempt integrity.

The hidden attempts emitted by a valid review pack must carry valid sealed review-entry evidence so a later owner disposition can be applied without free-form reconstruction.

Repeated pack construction with the same ready attempts + review seed must remain idempotent.

---

# 2. Add truthful provider-capture evidence for RAW_PROVIDER_CAPTURED

C003 request binding proves the model/engine we **asked for**. It does not prove the provider result that was actually captured.

Add a typed/sealed provider-capture evidence concept, for example:

`ProviderCaptureEvidence`

Exact name may differ.

Preferred source: the accepted typed `SemanticImageCandidate` / provider result object representing a successful provider return before local SP03 import.

The checked capture evidence must bind, at minimum where exposed by the accepted candidate contract:

- provider candidate/result deterministic identity/digest;
- semantic request digest;
- provider ID;
- provider version;
- workflow version;
- non-null model/engine identity;
- returned width/height;
- raw image SHA-256 / immutable image-byte identity;
- candidate SUCCESS status;
- relevant reference/style/init/color provenance already carried by the accepted provider candidate.

Construction must fail if model/engine is missing for a provider qualification cell.

Do not invent mutable provider UI/account IDs.

## RAW_PROVIDER_CAPTURED state rule

A trusted attempt at `RAW_PROVIDER_CAPTURED` must require checked provider-capture evidence whose:

- request digest equals the attempt's sealed `QualificationRequestBinding.request_digest`;
- provider ID/version/workflow/model exactly equal the selected provider matrix cell;
- returned result identity is valid and internally bound.

A request binding by itself is not capture evidence.

If implementing a separate capture evidence type would require modifying accepted SP02/SP03 contracts, keep those contracts unchanged and implement the wrapper entirely in SP04 from their public typed objects.

---

# 3. Cross-bind capture evidence to local raw import

For `RAW_IMPORT_VERIFIED` and every later state:

- checked `RawImportEvidence` remains mandatory;
- if provider capture evidence is present, it must match the local raw import exactly on provider candidate/result identity, request digest, provider ID/version/workflow/model, raw image SHA and returned dimensions;
- if the workflow safely skips storing an intermediate `RAW_PROVIDER_CAPTURED` record and constructs `RAW_IMPORT_VERIFIED` directly from a typed SP03 raw artifact, the qualification layer may derive equivalent capture evidence from the accepted typed source chain so provenance is not weakened.

No same-bytes/different-provider-provenance substitution.

No model `None` bypass.

---

# 4. Lifecycle rules after C004

Preserve C003 monotonic lifecycle and disposition rules.

Minimum truth:

```text
PLANNED
  -> RAW_PROVIDER_CAPTURED   requires checked provider-capture evidence
  -> RAW_IMPORT_VERIFIED     requires checked capture + raw import, exactly cross-bound
  -> NORMALIZED              + checked normalization
  -> READY_FOR_BLIND_REVIEW  + pending owner state
  -> OWNER_ACCEPTED | OWNER_REJECTED
       requires sealed deterministic review-entry evidence
```

Safe forward skipping is allowed only when all skipped evidence already exists and validates. For example direct construction at RAW_IMPORT_VERIFIED may derive/check capture evidence from the typed raw source chain, but it must not erase the conceptual capture proof.

Backward transitions remain forbidden. Terminal transitions remain final.

---

# 5. Preserve accepted C003 work

Do not weaken or discard:

- `QualificationRequestBinding` exact case/provider/request binding;
- exact semantic description/negative/category binding;
- explicit provider model/engine requirement;
- request digest→raw binding;
- `RawImportEvidence.from_sp03()`;
- `NormalizationEvidence.from_sp03()`;
- attempt construction seal;
- monotonic lifecycle checks;
- non-terminal pending owner-disposition requirement;
- summary exact plan membership validation;
- metadata-blind visible subject/target attribution;
- deterministic review ordering;
- cost/usage separation;
- 24x24 ASSET_ART baseline;
- Magnific/PixelLab provider-neutral architecture.

Do not rewrite SP01-SP03.

---

# 6. Required adversarial tests

At minimum add/retain tests proving all of the following.

## Review-entry proof

1. exact READY attempt + review seed can create checked review-entry evidence;
2. deterministic review ID equals the review pack item ID;
3. repeated equivalent construction is idempotent;
4. arbitrary `review-fixed`/`review-accepted`/random strings cannot mint terminal review proof;
5. ordinary direct review-binding constructor fails;
6. `dataclasses.replace()` cannot reissue/reset review-binding seal;
7. changed attempt/artifact/request identity invalidates review binding;
8. cost/usage changes do not change deterministic review ID;
9. OWNER_ACCEPTED without checked review-entry evidence fails;
10. OWNER_REJECTED without checked review-entry evidence fails;
11. valid review-pack-bound OWNER_ACCEPTED succeeds;
12. valid review-pack-bound OWNER_REJECTED succeeds;
13. visible review package remains provider/model/seed/cost/private-URL blind;
14. existing subject/target/sequence/ID attribution sensitivity remains green.

## Provider capture evidence

15. successful typed provider candidate with exact non-null model can mint checked capture evidence;
16. candidate with model `None` fails for provider qualification;
17. wrong provider ID fails;
18. wrong provider version fails;
19. wrong workflow version fails;
20. wrong model/engine fails;
21. wrong request digest fails;
22. raw SHA/result identity/dimensions are bound to exact candidate bytes/provenance;
23. ordinary free-form constructor cannot mint capture PASS evidence;
24. `dataclasses.replace()` cannot reset/reissue capture seal.

## Lifecycle/cross-binding

25. RAW_PROVIDER_CAPTURED without checked capture evidence fails;
26. RAW_PROVIDER_CAPTURED with exact capture evidence succeeds;
27. RAW_IMPORT_VERIFIED with capture/raw mismatch fails;
28. RAW_IMPORT_VERIFIED exact capture→raw chain succeeds;
29. NORMALIZED/READY still require same exact chain;
30. request binding model and returned capture model must agree;
31. provider capture result identity and SP03 raw candidate identity must agree when both exist;
32. backward and terminal transitions remain rejected.

## Summary/regression/security

33. summary rejects a terminal record lacking valid sealed review-entry evidence;
34. summary accepts exact pack-reviewed terminal records from its plan;
35. C003 request/case/model/summary/review-attribution adversarial tests remain green;
36. SP01-SP04 focused suite green;
37. full repository regression green;
38. compileall/import/CLI/diff checks green;
39. no provider/network/credential/browser execution;
40. no Magnific/PixelLab credits spent.

---

# 7. Scope exclusions

Do NOT:

- edit root `TASKS.md`;
- call Magnific;
- call PixelLab;
- spend credits;
- perform live provider qualification;
- choose a default provider/model/workflow;
- begin SP05/SP06;
- build Studio UI;
- begin weekly batches;
- change owner-locked LEVEL_ART dimensions/palette/color bands;
- force C01..C16 onto ASSET_ART;
- rewrite accepted SP01-SP03 architecture;
- begin M11;
- write the independent audit or self-mark SP04 accepted.

---

# 8. Builder log

Create **before any C004 implementation/source/test/doc edit**:

`.hiveai/codex-logs/PAG-SP04-C004_REVIEW_ENTRY_PROOF_AND_PROVIDER_CAPTURE_EVIDENCE_CLOSURE_CODEX_LOG.md`

Exact H1:

`# PAG-SP04-C004 — Review Entry Proof & Provider Capture Evidence Closure`

Role line:

`Document role: CODEX BUILDER LOG`

Record chronologically:

- start timestamp;
- repository/branch/start HEAD/origin HEAD/divergence after `git fetch origin`;
- preserved unrelated user dirt;
- authority files read, excluding legacy hidden tracker/control-plane files;
- proof the C004 builder log exists before any implementation edit;
- review-entry evidence design;
- provider-capture evidence design;
- capture→raw cross-binding design;
- lifecycle integration;
- exact files changed;
- every focused failure and correction;
- focused SP04 result;
- SP01-SP04 focused regression;
- full regression;
- compile/import/CLI/diff/offline/network/secret scans;
- implementation commit/push;
- final publication state.

For the final log-only publication commit, use the existing no-self-referential-loop rule: record the last source/test terminal SHA, state later publication commit is log-only, then verify current local HEAD == origin/main and divergence `0 0` in the builder response.

---

# 9. Stop rule

After implementation and verification:

1. complete the C004 builder log;
2. commit/push all C004 work to `main`;
3. fetch origin and verify local HEAD == `origin/main` with divergence `0 0`;
4. STOP for independent ChatGPT audit.

Do not run any live qualification. Do not begin SP05/SP06/M11.
