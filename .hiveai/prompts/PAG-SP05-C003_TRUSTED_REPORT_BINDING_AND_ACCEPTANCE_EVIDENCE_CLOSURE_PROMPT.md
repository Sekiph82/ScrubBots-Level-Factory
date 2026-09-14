# PAG-SP05-C003 — Trusted Report Binding & Acceptance Evidence Closure
Document role: CODEX REMEDIATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`

## Authority

Read completely from GitHub before implementation:

1. root `TASKS.md` — current tracker state;
2. `.hiveai/audits/PAG-SP05-C002_DIFFICULTY_V1_CONTRACT_CONVERGENCE_AND_TRUSTED_COMPILATION_EVIDENCE_CLOSURE_STRICT_AUDIT.md`;
3. `.hiveai/prompts/PAG-SP05-C002_DIFFICULTY_V1_CONTRACT_CONVERGENCE_AND_TRUSTED_COMPILATION_EVIDENCE_CLOSURE_PROMPT.md`;
4. `docs/LEVEL_ART_SEMANTIC_NORMALIZATION_OWNER_DECISION_V02.md`;
5. current `src/scrubbots_pixel_factory/semantic/normalization/level_art.py`;
6. current `src/scrubbots_pixel_factory/contracts/production.py`;
7. current `tests/unit/test_sp05_level_art.py`;
8. `GOVERNANCE.md` and `AGENTS.md` for builder/auditor ownership boundaries;
9. main-game owner Difficulty V1 authority, read-only only: `https://github.com/Sekiph82/Scrubbots/blob/main/coordination/OWNER_DIFFICULTY_PROGRESSION_DECISION_V01.md`.

GitHub is authoritative. The canonical local mirror is:

`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

Do not use `C:\Users\sekip\Desktop\ScrubBots` as the implementation repository.

Do not modify `Sekiph82/Scrubbots`.

Do not edit root `TASKS.md`.

Create the matching builder log before product/test edits:

`.hiveai/codex-logs/PAG-SP05-C003_TRUSTED_REPORT_BINDING_AND_ACCEPTANCE_EVIDENCE_CLOSURE_CODEX_LOG.md`

---

## Mission

Close only the remaining SP05-C002 trusted-evidence and acceptance-proof defects identified by the independent C002 strict audit.

C002’s corrected production architecture is retained as accepted technical direction:

```text
RAW SEMANTIC IMAGE
  → CELL_MAJORITY_V1
  → PALETTE_SNAP_V1
  → C01..C16
  → production dimensions: each axis 20..59, rectangles legal
  → production used-color envelope: 3..12 independent of lane/class
  → trusted immutable logical art + exact provenance
```

Do not redesign this flow.

---

# 1. Required fix: bind report raw SHA to the actual source

Finding:

`F-PAG-SP05-C002-001 — Trusted report raw SHA is not bound to actual source raw SHA`

Current artifact validation already binds many fields but does not explicitly require:

`report.raw_sha256 == artifact.raw_sha256 == source_provenance.raw_sha256`

Required behavior:

- every trusted report carried by a trusted artifact must have the exact raw SHA of the bound `SemanticRawArtifact`;
- any mismatch must fail closed before trusted artifact acceptance, serialization, digesting, or downstream use;
- do not rely only on the fact that the current compiler happens to pass the right value;
- encode the invariant in the trust boundary itself.

Preferred minimal implementation:

- add the missing equality check inside `SemanticLevelArtArtifact.__post_init__()` and/or the narrowest canonical trust-validation helper used by artifact construction;
- preserve existing source digest, request digest, majority digest, snapped digest, final-grid digest and provenance checks;
- do not broaden public constructors;
- do not expose a new caller-assertion-based sealing API.

If a helper is added, keep it private/internal and deterministic.

---

# 2. Required trust-adversarial tests

Add explicit focused tests proving that trusted evidence cannot remain valid after each material report fact is falsified.

At minimum cover:

1. `report.raw_sha256` mismatch;
2. `report.majority_rgba_sha256` mismatch;
3. `report.snapped_grid_digest` mismatch;
4. original snapped used-ID/count evidence mismatch;
5. retained subset mismatch;
6. weighted subset cost mismatch;
7. final used-ID/count mismatch where applicable;
8. `report.final_logical_grid_digest` mismatch.

Use a legitimate compiler-produced artifact/report as the starting point.

For adversarial testing, test-only/internal mutation may be used specifically to prove the seal/binding rejects tampering. Do not create a production API whose purpose is to forge reports.

Required outcomes:

- report integrity/digest validation fails for a mutated sealed report;
- artifact validation/trusted use fails when a carried report is inconsistent;
- the public historical `SemanticLevelArtArtifact.from_compilation()` remains non-minting and recomputes from raw artifact + request rather than trusting supplied stage assertions.

Do not weaken the private-token/fingerprint model.

---

# 3. Required lane non-transformative evidence

For the **same raw artifact** and **same target width/height**, compile at least EASY and VERY_HARD metadata and assert all of the following are identical:

- `majority_rgba_sha256`;
- `snapped_grid_digest`;
- final logical cells;
- `final_logical_grid_digest`;
- original/final used palette IDs and counts;
- retained subset and weighted objective when the same >12 fixture is used.

Request/artifact identity may differ if lane metadata intentionally participates in lineage identity. Transformation-stage output must not differ.

Do not add Challenge Score, Session Load, Frustration Risk, solver logic, or class-specific transforms.

---

# 4. Required 13..16 envelope closure

C002 focused tests explicitly cover 13 and 16-color cases but not 14 and 15 as required by the C002 prompt.

Add explicit deterministic fixtures for:

- 13 used canonical colors → exactly 12;
- 14 → exactly 12;
- 15 → exactly 12;
- 16 → exactly 12.

For every case assert:

- final distinct count is exactly 12;
- final IDs are a subset of the snapped input used IDs;
- no new C-ID is introduced;
- repeated runs are identical.

Do not change the weighted subset algorithm merely to satisfy tests.

---

# 5. Preserve accepted behavior exactly

C003 must not alter:

- CELL_MAJORITY half-open footprint math;
- majority frequency/tie behavior;
- source-smaller fail-closed behavior;
- non-opaque winner fail-closed behavior;
- PALETTE_SNAP squared RGB-distance behavior;
- canonical-index tie-break;
- C01..C16 palette values/order;
- production dimension envelope 20..59 per axis;
- rectangle legality;
- production used-color envelope 3..12;
- <3 fail-closed behavior;
- >12 exact weighted subset selection/remap behavior;
- ASSET_ART behavior;
- strict PNG decoder behavior;
- provider adapters;
- source raw bytes/provenance semantics.

Legacy class-specific compatibility validators remain available for historical behavior. Do not convert them into current production truth.

---

# 6. Optional hardening allowed only if needed by the tests

The C002 audit noted two non-blocking opportunities:

- `SemanticLevelArtReport.canonical_dict()` may assert report integrity before returning trusted serialized data;
- `DIFFICULTY_BUDGET_POLICY_VERSION` may be documented as a deprecated compatibility name now pointing to `PRODUCTION_COLOR_ENVELOPE_V1`.

You may implement the first only if it is the minimal clean way to make report tamper tests unambiguous.

Do not turn C003 into a naming/refactor cycle. Do not change schema versions unless strictly required to correct a real ambiguity introduced by C003.

---

# 7. Verification

Run and record at minimum:

1. `python -m pytest -q tests/unit/test_sp05_level_art.py`;
2. canonical palette/color/difficulty/production contract tests;
3. SP03 normalization tests;
4. SP04 C005/C006 PNG tests;
5. SP04 qualification tests relevant to accepted semantic normalization;
6. combined semantic SP01-SP05 focused regression;
7. full repository Python test suite;
8. `python -m compileall -q src tests`;
9. package import smoke;
10. CLI smoke;
11. `git diff --check`;
12. scoped offline/network/credential scan over changed production source/tests.

Record initial failures and final corrected results truthfully.

No Magnific call. No PixelLab call. Zero provider credits.

---

# 8. Scope prohibitions

Do not begin or modify:

- M08/LevelData bridge;
- gameplay solver;
- Challenge Score;
- Session Load;
- Frustration Risk;
- SP06 semantic recognizability;
- Studio feature implementation;
- publishing/control-plane implementation;
- weekly generation/batching;
- M11;
- main-game source;
- provider execution/model qualification;
- root `TASKS.md`.

Do not rewrite C001/C002 prompts, logs, or audits.

---

# 9. Builder log requirements

Matching H1 exactly:

`# PAG-SP05-C003 — Trusted Report Binding & Acceptance Evidence Closure`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record chronologically:

- start timestamp;
- repository/branch/remote verification;
- starting HEAD, origin/main and divergence;
- initial dirt;
- authorities read;
- exact files changed;
- exact trust-binding change;
- tests added for each required adversarial case;
- every materially relevant failed/final test outcome;
- regression commands/results;
- offline/network/credential checks;
- proof of zero provider calls/credits;
- implementation commit SHA(s);
- push result;
- terminal local HEAD/origin/main state in handoff if self-reference prevents storing final SHA in the same commit.

Do not claim ChatGPT acceptance.

Stop after push for independent strict audit.

---

# Acceptance criteria

C003 is eligible for PASS only if all are true:

- [ ] report raw SHA is explicitly bound to artifact/source raw SHA;
- [ ] wrong report raw SHA fails trusted validation;
- [ ] forged majority digest fails trusted validation;
- [ ] forged snapped digest/used evidence fails trusted validation;
- [ ] forged retained subset/weighted cost fails trusted validation;
- [ ] forged final evidence fails trusted validation;
- [ ] public `from_compilation()` remains non-minting;
- [ ] EASY vs VERY_HARD same raw+target produces identical majority/snapped/final transform digests/cells;
- [ ] 13, 14, 15 and 16 used colors all reduce deterministically to exactly 12;
- [ ] no envelope reduction introduces a new C-ID;
- [ ] CELL_MAJORITY_V1 remains unchanged;
- [ ] PALETTE_SNAP_V1 remains unchanged;
- [ ] production 20..59 dimension semantics remain unchanged;
- [ ] production 3..12 envelope semantics remain unchanged;
- [ ] legacy compatibility remains green;
- [ ] ASSET_ART and strict PNG behavior remain green;
- [ ] focused and full regressions are green;
- [ ] zero provider calls / zero credits;
- [ ] builder does not edit root `TASKS.md`;
- [ ] no main-game writes;
- [ ] builder log is truthful and complete.
