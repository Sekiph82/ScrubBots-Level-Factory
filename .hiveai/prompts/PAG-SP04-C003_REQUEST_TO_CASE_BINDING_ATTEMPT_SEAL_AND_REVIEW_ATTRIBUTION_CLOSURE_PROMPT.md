# PAG-SP04-C003 — Request-to-Case Binding, Attempt Seal & Review Attribution Closure
Document role: CODEX REMEDIATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`

## Authority

Read from GitHub before any source/test edit:

1. root `TASKS.md` — ONLY current project-status tracker;
2. `.hiveai/audits/PAG-SP04-C002_QUALIFICATION_PROVENANCE_CAPABILITY_AND_BLIND_REVIEW_BINDING_REMEDIATION_STRICT_AUDIT.md`;
3. `.hiveai/prompts/PAG-SP04-C002_QUALIFICATION_PROVENANCE_CAPABILITY_AND_BLIND_REVIEW_BINDING_REMEDIATION_PROMPT.md`;
4. `.hiveai/codex-logs/PAG-SP04-C002_QUALIFICATION_PROVENANCE_CAPABILITY_AND_BLIND_REVIEW_BINDING_REMEDIATION_CODEX_LOG.md`;
5. accepted SP01 semantic request/provider contracts;
6. accepted SP02 Magnific/PixelLab bridge contracts;
7. accepted SP03 raw/normalization/seal contracts;
8. current SP04 qualification implementation/tests;
9. `AGENTS.md`, `GOVERNANCE.md`, `CLAUDE.md`.

Do not use legacy hidden `.hiveai` tracker/control-plane files as current authority.

Do not edit root `TASKS.md`.

Create the C003 builder log **before any C003 source/test/doc edit**.

## Mission

Close exactly the C002 residual findings:

- `F-PAG-SP04-C002-001` — an unsealed direct PLANNED attempt can mint a sealed advanced attempt through public helper methods;
- `F-PAG-SP04-C002-002` — benchmark case and actual typed semantic request are not cross-bound;
- `F-PAG-SP04-C002-003` — explicit provider matrix model/engine can be bypassed by `model_id=None`;
- `F-PAG-SP04-C002-004` — lifecycle and owner disposition are not monotonic/coherent;
- `F-PAG-SP04-C002-005` — summary and visible review metadata are not fully cross-bound to the exact plan/hidden attempt;
- `F-PAG-SP04-C002-006` — process-only final-log truthfulness issue; comply correctly this cycle.

This remains an **offline contract-remediation cycle**.

Do not call Magnific or PixelLab. Do not spend credits. Do not begin live qualification, SP05, SP06, Studio UI or M11.

---

# 1. Add a checked request-to-case/provider binding

The qualification harness must prove that the actual typed `SemanticGenerationRequest` used for one attempt belongs to the exact benchmark case and provider matrix cell selected by the plan.

Add a small immutable/sealed concept such as:

`QualificationRequestBinding`

Exact name may differ.

It must be constructible only from:

- a validated `QualificationPlan`;
- an exact `QualificationPlanEntry` member of that plan;
- the actual typed `SemanticGenerationRequest`.

The checked binding must retain/prove at minimum:

- plan digest;
- plan entry ID;
- benchmark case ID + case digest;
- provider matrix ID;
- provider ID;
- provider version/config version where the existing request/provider contracts expose them;
- explicit provider model/engine;
- provider workflow version;
- semantic request digest;
- output class;
- requested logical target width/height;
- canonical benchmark semantic description/negative intent relationship;
- required REFERENCE / STYLE semantics.

## Required request truth

For SP04 qualification C003, fail closed unless the actual request is demonstrably the request for the selected benchmark cell.

At minimum require:

1. `request.output_class == ASSET_ART`;
2. resolved request dimensions equal the benchmark/plan target;
3. request provider ID exactly equals the selected matrix provider;
4. request provider model/engine is non-null and exactly equals the selected matrix model/engine;
5. request workflow version exactly equals the selected matrix workflow version;
6. request provider config version is compatible with the accepted provider adapter/matrix contract;
7. positive semantic description is deterministically bound to the benchmark case intent;
8. negative description is deterministically bound to the benchmark case negative intent when present;
9. if `case.requires_reference=True`, the actual request must carry the required accepted reference-role input;
10. if `case.requires_style=True`, the actual request must carry the accepted STYLE input/path for that provider cell;
11. unsupported or extra substitutions fail closed rather than being silently normalized away.

A deterministic request builder derived from `(case, provider spec, seed, approved inputs)` is acceptable and preferred if it makes exact equality easier to prove.

Do not redesign SP01 `SemanticGenerationRequest`; build a qualification-layer binding around the accepted typed request.

The raw evidence's `request_digest` must exactly equal the checked request binding's request digest.

The qualification attempt must carry the sealed request binding, not merely a copied free-form digest.

---

# 2. Eliminate unsealed-attempt seal minting

Current C002 helpers can promote a directly constructed unsealed PLANNED record into a sealed advanced record.

Close this completely.

Preferred solution:

- make `QualificationAttemptRecord` checked-construction-only for **all** lifecycle states, including PLANNED; or
- otherwise make every mutation/transition helper reject unsealed records and make it impossible for `_copy_bound()` or equivalent to install a valid construction token onto an untrusted public record.

Required invariants:

- ordinary direct constructor cannot produce a trusted attempt used by review/summary;
- `dataclasses.replace()` cannot reset/reissue the seal;
- no public helper may mint a seal from an unsealed object;
- every trusted attempt must originate from the exact validated plan entry and checked request binding;
- attempt fingerprint must include the request binding identity in addition to plan/provider/raw/normalized identity.

Do not use the construction token as a secret credential. This remains local invariant protection only.

---

# 3. Exact model/engine binding

For any attempt at `RAW_PROVIDER_CAPTURED` or later that represents a real approved provider matrix cell:

- raw provider model identity must be present;
- it must exactly equal the selected matrix model/engine;
- `None`/unknown must fail closed;
- provider ID/version/workflow/request digest must also remain exact.

If a specific provider requires a typed translation between request engine and raw model identity, encode that translation explicitly and test it. Do not use `if model_id is not None` as a bypass.

---

# 4. Monotonic lifecycle and owner-disposition state machine

Define an explicit allowed lifecycle transition policy.

Minimum order:

```text
PLANNED
  -> RAW_PROVIDER_CAPTURED
  -> RAW_IMPORT_VERIFIED
  -> NORMALIZED
  -> READY_FOR_BLIND_REVIEW
  -> OWNER_ACCEPTED | OWNER_REJECTED
```

You may allow safe forward skipping only if every skipped prerequisite is already present and validated, but **backward transitions are forbidden** and terminal states cannot transition to another technical state.

Owner disposition rules:

- PLANNED → PENDING_OWNER_REVIEW only;
- RAW_PROVIDER_CAPTURED → PENDING_OWNER_REVIEW only;
- RAW_IMPORT_VERIFIED → PENDING_OWNER_REVIEW only;
- NORMALIZED → PENDING_OWNER_REVIEW only;
- READY_FOR_BLIND_REVIEW → PENDING_OWNER_REVIEW only;
- OWNER_ACCEPTED → OWNER_ACCEPTED only;
- OWNER_REJECTED → OWNER_REJECTED only.

Terminal owner states must require:

- exact validated plan + request binding;
- checked raw evidence;
- checked normalization evidence;
- an existing deterministic review binding/item ID proving the candidate entered the metadata-blind review protocol;
- matching owner disposition.

Do not permit direct terminal construction that bypasses the review binding.

---

# 5. Summary must consume only trusted attempts from the supplied plan

Harden `summarize_qualification(plan, attempts)`.

Before counting anything it must fail closed unless every attempt:

- passes its construction-integrity assertion;
- is bound to `plan.digest()`;
- references an exact existing plan entry;
- matches that entry's case/provider matrix/request binding identity;
- has a lifecycle/disposition combination allowed by the state machine.

A sealed attempt from another qualification plan must be rejected.

An unsealed direct PLANNED object must be rejected.

Do not let owner-disposition fields alone create an OWNER_ACCEPTED / OWNER_REJECTED summary.

Summary still must not mutate tracker/default-provider state.

---

# 6. Complete visible↔hidden review attribution

Keep metadata-blind review.

Strengthen direct `MetadataBlindReviewPack` construction so each visible item is fully derived/bound to its exact hidden attempt, not only by `hidden_attempt_id + review_id`.

At minimum validate:

- `hidden_attempt_id` exists exactly once;
- `review_id` equals the deterministic ID expected from review seed + hidden attempt review-binding digest;
- hidden attempt carries the same review ID;
- visible subject label equals the canonical blind-review subject label derived from the bound benchmark case;
- visible target dimensions equal the hidden attempt normalized target;
- sequence values are unique, contiguous and match the deterministic review ordering for that seed;
- each hidden attempt is represented exactly once.

Prefer a useful neutral subject label such as the benchmark subject (`wizard`, `warrior`, etc.) rather than leaking provider/model metadata. Case ID may remain hidden metadata.

Add a coordinated-swap test:

- take two valid review items;
- swap both `hidden_attempt_id` and `review_id` so the ID pair is internally valid;
- leave the original subject/target metadata in place;
- direct pack construction must reject the stale/misattributed visible metadata.

Reordering the hidden tuple alone must remain safe because attribution is ID-based.

---

# 7. Preserve accepted C002 typed evidence

Do not discard or weaken:

- `RawImportEvidence.from_sp03()` sealed typed evidence;
- `NormalizationEvidence.from_sp03()` sealed typed evidence;
- raw SHA + raw-artifact digest binding;
- normalized source/raw/request/report/RGBA binding;
- provider capability checks;
- Cartesian plan validation;
- finite plan limits;
- cost/usage separation;
- positive/negative public evidence references;
- 24x24 ASSET_ART baseline;
- provider-neutral Magnific/PixelLab architecture.

Do not modify accepted SP03 algorithms/seals unless a compile-only compatibility fix is unavoidable.

---

# 8. Required adversarial tests

At minimum prove all of the following.

## Request-to-case/provider

1. exact wizard case + exact wizard request binding succeeds;
2. wizard case + warrior/robot request intent fails;
3. request target dimensions differing from plan target fail;
4. request provider ID mismatch fails;
5. request model/engine mismatch or `None` fails;
6. request workflow/config mismatch fails;
7. request digest mismatch between checked request binding and raw evidence fails;
8. required STYLE missing from actual request fails;
9. required REFERENCE missing from actual request fails;
10. eligible BITFORGE STYLE request succeeds when exact accepted input is present.

## Attempt seal/state machine

11. direct public PLANNED attempt cannot be promoted through `with_lifecycle()` or any copy helper;
12. `dataclasses.replace()` cannot mint/reset attempt seal;
13. checked PLANNED attempt from exact plan+request works;
14. forward valid transition works;
15. backward transition fails;
16. terminal→technical transition fails;
17. non-terminal lifecycle + OWNER_ACCEPTED disposition fails;
18. non-terminal lifecycle + OWNER_REJECTED disposition fails;
19. terminal owner state without review binding fails;
20. OWNER_ACCEPTED from exact review-bound ready record succeeds;
21. OWNER_REJECTED from exact review-bound ready record succeeds.

## Exact model/provenance

22. raw `model_id=None` against explicit provider matrix model fails;
23. wrong raw model fails;
24. wrong provider/version/workflow fails;
25. wrong request binding/raw request digest fails;
26. wrong raw/normalized source chain still fails.

## Summary

27. unsealed attempt in summary fails;
28. attempt from another plan fails;
29. attempt referencing unknown/wrong entry fails;
30. pending-only summary remains pending;
31. accepted-only summary is accepted;
32. rejected-only summary is rejected;
33. mixed state follows deterministic documented rule.

## Review attribution

34. visible provider/model/seed/cost/private URL remains absent;
35. visible subject/target are derived from exact hidden attempt;
36. coordinated hidden-id + review-id swap with stale label/target fails;
37. duplicate/orphan visible/hidden records fail;
38. deterministic sequence validation fails on altered sequence;
39. hidden tuple reorder remains attribution-safe;
40. repeated review-pack construction remains idempotent;
41. changing cost does not change review ID;
42. changing exact artifact/request identity changes review ID.

## Regression/security

43. C001/C002 corpus/provider/cost/evidence tests remain green;
44. SP01-SP04 focused suite green;
45. full repository regression green;
46. compileall/import/CLI/diff check green;
47. no provider/network/credential/browser execution;
48. no Magnific/PixelLab credits spent.

---

# 9. Scope exclusions

Do NOT:

- edit root `TASKS.md`;
- call Magnific;
- call PixelLab;
- spend credits;
- start live provider qualification;
- choose a default provider/model/workflow;
- begin SP05/SP06;
- build Studio UI;
- begin weekly batches;
- alter owner-locked LEVEL_ART dimensions/palette/color bands;
- force C01..C16 onto ASSET_ART;
- rewrite accepted SP01-SP03 architecture;
- begin M11;
- self-audit or mark SP04 accepted.

---

# 10. Builder log

Create BEFORE any C003 implementation edit:

`.hiveai/codex-logs/PAG-SP04-C003_REQUEST_TO_CASE_BINDING_ATTEMPT_SEAL_AND_REVIEW_ATTRIBUTION_CLOSURE_CODEX_LOG.md`

Exact H1:

`# PAG-SP04-C003 — Request-to-Case Binding, Attempt Seal & Review Attribution Closure`

Role line:

`Document role: CODEX BUILDER LOG`

Record chronologically:

- repository/branch/start HEAD/origin HEAD/divergence after fetch;
- preserved user-owned dirt;
- authority files read;
- proof log existed before C003 source/test edits;
- request-binding design;
- attempt construction-seal design;
- lifecycle transition table;
- model/engine exact-binding design;
- summary plan-membership validation;
- review visible↔hidden attribution design;
- every focused failure/correction;
- focused SP04 result;
- SP01-SP04 focused regression;
- full regression;
- compile/import/CLI/offline/network/secret checks;
- exact files changed;
- implementation commit/push;
- final publication state.

For final-log publication, do not create an endless self-referential SHA loop. It is sufficient to record the last **pre-log-only** source/test terminal SHA and explicitly state that any later commit is log-only, while the builder response verifies current remote `main` equality. Do not claim a stale SHA is the product/source terminal state.

---

# 11. Stop rule

After implementation and verification:

1. complete the C003 builder log;
2. commit/push all C003 work to `main`;
3. fetch origin and verify local HEAD == origin/main, divergence `0 0`;
4. STOP for independent ChatGPT audit.

Do not perform live qualification. Do not begin SP05/SP06/M11.
