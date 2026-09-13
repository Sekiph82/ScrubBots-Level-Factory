# PAG-SP03-C003 — Provenance Seal & Construction Integrity Closure
Document role: CODEX REMEDIATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`

## Authority

Read from GitHub before coding:

1. root `TASKS.md` — ONLY current project-status tracker;
2. `.hiveai/audits/PAG-SP03-C002_BOUNDED_DECODE_DEEP_IMMUTABILITY_AND_RAW_TO_NORMALIZED_PROVENANCE_CLOSURE_STRICT_AUDIT.md`;
3. `.hiveai/prompts/PAG-SP03-C002_BOUNDED_DECODE_DEEP_IMMUTABILITY_AND_RAW_TO_NORMALIZED_PROVENANCE_CLOSURE_PROMPT.md`;
4. accepted SP01/SP02 contracts and SP03 C001/C002 implementation;
5. `review/sp02/SP02_MAGNIFIC_LIVE_SMOKE_2026-09-13.md`;
6. M07/M08/M09 provenance/export contracts;
7. `AGENTS.md`, `GOVERNANCE.md`, `CLAUDE.md`.

Do **not** use `.hiveai/PROJECT.json`, `.hiveai/RULES.md`, `.hiveai/TASKS.md`, `.hiveai/EVENTS.jsonl`, `.hiveai/CYCLE_INDEX.md`, `.hiveai/STATE.json`, `.hiveai/HANDOFF.md`, or any other legacy hidden tracker/control-plane projection as current authority.

## Mission

Implement **SP03-C003 only**.

Close exactly:

- `F-PAG-SP03-C002-001` — normalized provenance construction seal can be reset during coordinated dataclass replacement;
- `F-PAG-SP03-C002-002` — builder authority discipline/process correction.

Preserve byte-for-byte accepted normalization behavior:

- exact 24x24 fast path;
- deterministic `AREA_AVERAGE_V1` large-raster baseline;
- `FIT_CENTER_LETTERBOX_V1`;
- bounded PNG decode;
- deep immutable report state;
- `PRESERVE_ALPHA` / `OPAQUE_AS_IS`;
- ASSET_ART `PRESERVE_SOURCE_RGBA`;
- LEVEL_ART normalization request fail-closed;
- no network/provider call;
- no provider credits;
- no SP04/M11.

Do not edit root `TASKS.md`.

---

# 1. Threat model to close

Current C002 code correctly rejects simple tampering, but this coordinated sequence remains possible in ordinary Python dataclass APIs:

1. obtain a valid `SemanticNormalizedArtifact`;
2. produce a modified `SemanticSourceProvenance` that retains source A's `raw_artifact_digest` but changes provider/version/workflow/model/request convenience provenance;
3. use `dataclasses.replace()` on the normalized artifact with that modified source snapshot and matching duplicated provider/request fields;
4. reset `_construction_fingerprint=None` while the valid `_construction_token` is copied from the original object;
5. current `__post_init__()` treats `None` as permission to mint a fresh fingerprint for the forged coordinated state.

The result can be internally consistent while no longer proving that its convenience provenance was derived from the raw artifact identified by the source digest.

C003 must make this impossible through ordinary constructor/`dataclasses.replace()` use.

Do not solve only the exact field names in the example. Close the construction-integrity class of defect.

---

# 2. Source provenance must be sealed to raw-artifact construction

`SemanticSourceProvenance` must not allow an arbitrary caller to claim an existing `raw_artifact_digest` with altered source identity fields.

Use a fail-closed design. Acceptable patterns include:

- an internal construction sentinel that is `init=False`/not caller-settable and only installed by `from_raw_artifact()`;
- a private implementation type with a public read-only projection;
- a checked canonical source-identity payload whose integrity is revalidated and cannot be reissued from arbitrary fields;
- an equivalent architecture with the same property.

Requirements:

- normal `SemanticSourceProvenance.from_raw_artifact(raw)` succeeds;
- direct public construction of a sealed source snapshot either is impossible or produces an object that cannot be accepted as normalized provenance;
- `dataclasses.replace(valid_source_provenance, provider_id="forged")` must not create an accepted sealed source snapshot;
- preserving the original raw-artifact digest while altering provider/version/workflow/model/request provenance must fail closed;
- input/reference provenance remains preserved;
- no path, secret, signed URL or credential enters deterministic identity.

Do not rely on naming a field with a leading underscore as a security boundary.

---

# 3. Normalized artifact seal/fingerprint must not be caller-resettable

Internal construction state such as `_construction_token` and `_construction_fingerprint` must not be ordinary caller-settable `init=True` fields.

Requirements:

- `SemanticNormalizedArtifact.from_raw_artifact()` remains the checked normal construction path;
- direct arbitrary normalized construction remains rejected;
- `dataclasses.replace()` must not carry or reset a valid construction capability in a way that permits coordinated forged state;
- callers must not be able to pass `_construction_fingerprint=None` to request a new seal for modified provenance;
- the seal/fingerprint must be derived unconditionally from accepted construction inputs, not from caller permission;
- if a construction fingerprint exists, it should be `init=False` or equivalent and verified by an internal integrity assertion;
- deterministic serialization/digest should fail closed if internal provenance integrity is invalid.

Recommended defense-in-depth:

- add a private `_assert_integrity()` and call it from `identity_dict()`, `canonical_dict()` and/or `digest()`;
- make the source-provenance seal part of the integrity calculation;
- make normalized artifact internal seal fields non-replaceable through normal dataclass replacement.

---

# 4. Required coordinated-tamper tests

Add explicit tests proving all of the following.

## 4.1 Source snapshot

1. valid `SemanticSourceProvenance.from_raw_artifact(raw)` succeeds;
2. direct/replace attempt changing provider id while retaining the same raw-artifact digest cannot become an accepted sealed source snapshot;
3. same for provider version;
4. same for workflow/model/request digest;
5. reference/input provenance still serializes identically in normal use.

## 4.2 Normalized artifact

Starting from a valid normalized artifact:

6. simple provider-field replacement rejects (preserve existing coverage);
7. simple request-digest replacement rejects;
8. real foreign source snapshot rejects;
9. **coordinated attack:** forged source snapshot with source A digest + forged provider provenance, matching normalized provider fields, and attempted fingerprint reset must reject;
10. coordinated model/workflow/request replacement must reject;
11. attempt to pass/reset internal token/fingerprint through `dataclasses.replace()` must reject or be impossible by signature;
12. deterministic `digest()`/`canonical_bytes()` on a valid object remains stable.

The test must specifically cover the C002 escaped scenario, not only one-field mismatches.

---

# 5. Preserve C002 security and normalization behavior

Do not regress:

- bounded zlib output budget across all decompression lifecycle stages;
- expected-length valid PNG PASS;
- expected+1/truncated/trailing/high-expansion PNG rejection;
- report `crop_pad` deep immutability;
- source bytes/hash immutable;
- exact 24x24 no-resize pixel identity;
- repeated normalization deterministic;
- 2048x2048 -> 24x24 baseline unchanged;
- aspect mismatch letterbox unchanged;
- alpha policy unchanged;
- ASSET_ART palette boundary unchanged;
- all LEVEL_ART normalization requests rejected at construction;
- normalized ASSET_ART cannot masquerade as M08 LEVEL_ART;
- CLI source overwrite protection.

No visual algorithm changes in C003.

---

# 6. Scope exclusions

Do NOT:

- edit root `TASKS.md`;
- begin SP04/SP05/SP06/M11;
- call Magnific/PixelLab;
- spend provider credits;
- alter M00-M10 algorithms;
- alter provider bridges;
- broaden PNG/JPEG/WebP compatibility;
- change 24x24 owner-approved ASSET_ART baseline;
- change resampling/crop/alpha/palette policy;
- implement C01..C16 LEVEL_ART quantization;
- add Studio UI;
- self-audit or mark SP03 accepted.

---

# 7. Builder process requirement

Create BEFORE any C003 source/test/doc edit:

`.hiveai/codex-logs/PAG-SP03-C003_PROVENANCE_SEAL_AND_CONSTRUCTION_INTEGRITY_CLOSURE_CODEX_LOG.md`

Exact H1:

`# PAG-SP03-C003 — Provenance Seal & Construction Integrity Closure`

Role line:

`Document role: CODEX BUILDER LOG`

The builder log must read current GitHub `main` first and record:

- fetched `origin/main`;
- local HEAD;
- divergence `0 0` before implementation;
- root `TASKS.md` and current C003 prompt/audit as authority;
- explicitly state that legacy hidden `.hiveai` tracker/control-plane files were not used as authority;
- exact construction-seal design;
- exact changed paths;
- every focused failure/correction;
- SP03 focused result;
- SP01+SP02+SP03 focused result;
- full repository regression;
- compile/import/CLI/offline checks;
- commit/push;
- final local HEAD == origin/main and divergence `0 0`.

If GitHub advances during implementation, fetch and merge/reconcile without force-push, then rerun the relevant tests before publication.

---

# 8. Required verification

At minimum run:

1. SP03 focused tests including coordinated-tamper sensitivity;
2. SP01+SP02+SP03 focused regression;
3. full repository regression;
4. compileall/import checks;
5. CLI help/safety check;
6. network/provider/secret scan for scoped changes;
7. `git diff --check`;
8. final publication equality check.

No paid or live provider test belongs in this cycle.

---

# 9. Stop rule

After implementation and verification:

1. complete builder log;
2. commit/push `main`;
3. verify final HEAD == origin/main divergence `0 0`;
4. STOP for independent ChatGPT audit.

Do not begin SP04 or any later work.