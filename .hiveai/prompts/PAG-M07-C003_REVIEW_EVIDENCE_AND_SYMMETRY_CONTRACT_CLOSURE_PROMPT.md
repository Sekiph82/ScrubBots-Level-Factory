# PAG-M07-C003 — Review Evidence & Symmetry Contract Closure

Document role: CODEX REMEDIATION PROMPT

Status: AUTHORITATIVE / READY_FOR_IMPLEMENTATION  
Builder: Codex  
Independent auditor / tracker owner: ChatGPT  
Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`  
Canonical branch: `main`

Authoritative C002 strict audit:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M07-C002_STRUCTURAL_METRIC_SEMANTICS_AND_ACCEPTANCE_EVIDENCE_REMEDIATION_STRICT_AUDIT.md`

C002 builder log:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/PAG-M07-C002_STRUCTURAL_METRIC_SEMANTICS_AND_ACCEPTANCE_EVIDENCE_REMEDIATION_CODEX_LOG.md`

Original C001 audit:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M07-C001_ARTWORK_QUALITY_AND_DIVERSITY_FILTERS_STRICT_AUDIT.md`

## 1. Mission

Close only the two residual C002 findings:

- `F-PAG-M07-C002-001` - contact-sheet integration evidence is not card-local and can be satisfied by generic tokens rendered on unrelated cards;
- `F-PAG-M07-C002-002` - the geometric reflection convention of the two directional symmetry fields is not explicitly documented.

This is an evidence and contract-documentation closure cycle.

Preserve the accepted C002 implementation, especially:

- occupied isolation/tiny metrics derived from occupied-mask components;
- per-color components kept as separate evidence;
- total occupied color counts and total color dominance semantics;
- enforceable explicit one-color dominance threshold;
- deterministic boundary-majority negative-space inference;
- genuine C002 structural fixtures;
- conservative M03-M06 quality compatibility;
- framed SHA-256 logical-grid identity;
- exact/near duplicate architecture;
- per-card renderer fields already added in C002;
- offline/no-resize/no-cloud architecture;
- all accepted M00-M06 behavior.

Do not redesign `quality/core.py` mathematics unless a new focused test first proves a real contradiction. Do not begin PAG-M08+.

## 2. GitHub-first authority

Before editing, read completely from GitHub `main`:

1. `.hiveai/PROJECT.json`
2. `.hiveai/RULES.md`
3. v3 machine block in `.hiveai/TASKS.md`
4. `.hiveai/EVENTS.jsonl`
5. `tasks.md`
6. `.hiveai/CYCLE_INDEX.md`
7. `AGENTS.md`
8. `GOVERNANCE.md`
9. C001 prompt/audit
10. C002 prompt/builder log/strict audit
11. current `src/scrubbots_pixel_factory/quality/` source/docs
12. current M07 unit/integration tests
13. current `review/m07` builder, manifest and contact sheet
14. this C003 prompt

GitHub `main` is current-state authority.

Authorized local workspace only:
`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

Never substitute or modify:
`C:\Users\sekip\Desktop\ScrubBots`

Use only non-destructive synchronization. No hard reset, force push, blanket restore/clean or silent auto-rebase.

## 3. Matching builder log

Before the first C003 implementation/test/documentation/review edit create:

`.hiveai/codex-logs/PAG-M07-C003_REVIEW_EVIDENCE_AND_SYMMETRY_CONTRACT_CLOSURE_CODEX_LOG.md`

Exact H1:

`# PAG-M07-C003 — Review Evidence & Symmetry Contract Closure`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record chronologically and truthfully:

- timestamp, repository, branch, origin, starting HEAD/status;
- GitHub-first authority reads;
- pre-existing local changes and preservation;
- exact edits;
- focused test failures/corrections;
- review regeneration if any;
- regression tests;
- static/offline checks;
- final diff/status;
- implementation/evidence commit SHA;
- push result;
- final post-log-publication local HEAD and `origin/main` equality.

Do not self-audit and do not edit ChatGPT-owned task/tracker/audit state.

## 4. Close F-PAG-M07-C002-002: explicit symmetry contract

Document the current directional score convention explicitly in the public quality documentation and, where appropriate, public API docstrings/comments.

The current intended convention is:

- `horizontal_symmetry_score`: compare each `(x, y)` cell with `(width - 1 - x, y)`. This is left-right mirror equivalence, geometrically reflection across the vertical centerline.
- `vertical_symmetry_score`: compare each `(x, y)` cell with `(x, height - 1 - y)`. This is top-bottom mirror equivalence, geometrically reflection across the horizontal centerline.

Do not silently rename or invert existing fields in this cycle. Preserve existing serialized field names and behavior unless a focused test proves current implementation contradicts the above convention.

At minimum update:

- `src/scrubbots_pixel_factory/quality/README.md`

The documentation must also state:

- score range is 0..1;
- 1.0 means every logical cell equals its reflected counterpart for that convention;
- scores are computed from the complete logical grid, including the inferred-negative-space C-ID as ordinary cell equality for symmetry comparison;
- these are structural grid metrics, not semantic/artistic judgments.

Retain the existing directional known-answer tests and make their names/comments clearly bind to this documented convention.

## 5. Close F-PAG-M07-C002-001: card-local HTML evidence tests

The current renderer already emits the required evidence. The missing gate is automated card-local binding.

Strengthen `tests/integration/test_m07_review_evidence.py` so representative assertions extract or otherwise isolate the HTML for one exact candidate card before checking its content.

Do not accept whole-document assertions such as only:

- `"exact duplicate group:" in contact`;
- `"near-duplicate partners:" in contact`;
- `"UNAVAILABLE: INVALID_INPUT" in contact`.

A value rendered on a different card must not be able to satisfy another card's test.

### 5.1 Stable card identification

Prefer a deterministic HTML marker such as:

`<article class="card" data-candidate-id="...">`

or an equally explicit stable candidate-local structure.

If renderer markup is changed to add such a marker:

- escape candidate IDs safely;
- add no JavaScript;
- preserve self-contained/offline HTML;
- regenerate the committed contact sheet deterministically.

Do not add a heavyweight HTML parser dependency merely for this test. A small project-test helper using the standard library or deterministic string boundaries is sufficient if robust for the generated markup.

### 5.2 Mandatory representative card assertions

At minimum prove all of the following against isolated card HTML:

#### A. Normal generated card

For `generated-01-mask` or another deterministic generated card:

- candidate ID belongs to that card;
- expected exact grid SHA-256 from the committed manifest appears in that same card;
- its expected mode, seed, dimensions, decision and representative core metric text appear in that same card.

#### B. Exact duplicate card

For `bad-09-exact-duplicate-a`:

- isolate only that card;
- assert its exact grid hash equals the corresponding manifest value;
- assert its exact duplicate group includes both `bad-09-exact-duplicate-a` and `bad-10-exact-duplicate-b` in that same card;
- assert unrelated candidate IDs are not used as a substitute for the required duplicate partner.

#### C. Near-duplicate card

For the committed near-duplicate fixture, for example `bad-11-near-duplicate`:

- isolate only that card;
- obtain expected near-duplicate partner evidence from the committed manifest;
- assert at least one expected partner ID appears in that same card;
- assert that partner's exact displayed occupancy-mask and color-layout similarity values, using the renderer's deterministic formatting, appear in that card.

Do not merely assert the label `near-duplicate partners:` exists.

#### D. Invalid-input card

For at least one exact invalid fixture such as `bad-08-dimension-mismatch` and preferably also `bad-07-off-palette`:

- isolate only that card;
- assert `UNAVAILABLE: INVALID_INPUT` in that card;
- assert the exact stable rejection code for that fixture, such as `DIMENSION_MISMATCH` or `OFF_PALETTE`, in that card;
- prove a valid grid hash is not falsely shown for that invalid card.

### 5.3 Negative binding proof

Add at least one assertion/test proving evidence cannot float across cards. Examples:

- a card helper for candidate A must not return candidate B's card body;
- an expected duplicate partner present only in another card must not satisfy A unless it is explicitly rendered inside A's evidence;
- mutate a generated HTML string in a focused test by moving/removing A's required evidence while leaving the same token elsewhere, and prove the card-local assertion fails.

The purpose is to bind evidence to the candidate, not just increase assertion count.

## 6. Review manifest/contact sheet preservation

Do not redesign the accepted C002 review data model.

Preserve:

- deterministic candidate ordering;
- per-entry grid hash;
- exact duplicate group evidence;
- near-duplicate partner IDs and similarity scores;
- invalid-input explicit hash unavailability;
- stable decision/rejection codes;
- blank `human_review` until actual owner review;
- no timestamps or machine paths;
- no external assets/scripts/fonts/network;
- pixelated presentation-only scaling.

If markup changes only to support stable card selection, regenerate:

- `review/m07/M07_QUALITY_CONTACT_SHEET.html`

Regenerate the manifest only if the source builder deterministically changes manifest content. Do not create meaningless artifact diffs.

## 7. Source scope

Expected C003 changes should be narrow, primarily among:

- `src/scrubbots_pixel_factory/quality/README.md`;
- `src/scrubbots_pixel_factory/quality/review.py` only if a stable card marker is needed;
- `tests/integration/test_m07_review_evidence.py`;
- `tests/unit/test_m07_quality.py` only if comments/names or a focused symmetry contract assertion need strengthening;
- `review/m07/M07_QUALITY_CONTACT_SHEET.html` only if regenerated because markup changed;
- matching C003 builder log.

Do not change metric formulas, rejection thresholds, duplicate algorithms, generator production code, M02 contracts, dependencies or owner-locked palette/dimension rules unless a new focused failing test establishes a real defect and the log explains it.

Do not begin M08, M09, M10 or M11.

## 8. Required verification

At minimum run and record:

1. all M07 focused tests;
2. direct card-local evidence tests described above;
3. directional symmetry known-answer tests;
4. review manifest/contact-sheet deterministic regeneration comparison;
5. cross-process/hash-seed determinism test(s);
6. representative M03-M06 compatibility tests;
7. M06 router/hybrid/replay/AUTO regression tests;
8. full repository `pytest`;
9. standalone import;
10. offline/network source-policy scan;
11. resize/resample/interpolation scan;
12. M08+ implementation-scope scan;
13. `git diff --check`;
14. `python -m pip check`.

The known environment-only `pytest-asyncio 0.24.0` versus pytest `9.1.1` mismatch may remain documented if unchanged. Do not modify unrelated dependencies merely to hide it.

## 9. Acceptance gates

C003 is ready for independent audit only when:

- symmetry field conventions are explicitly documented as required;
- directional tests match that documented convention;
- contact cards remain self-contained and render all C002-required evidence;
- representative contact-sheet tests isolate exact candidate cards;
- generated card hash/metadata is card-local verified;
- exact duplicate group is card-local verified;
- near-duplicate partner ID plus exact displayed similarity values are card-local verified;
- invalid-input hash unavailability plus stable rejection code is card-local verified;
- a negative binding test proves generic evidence elsewhere cannot satisfy the intended card;
- review artifacts are deterministic;
- C002 metric semantics remain unchanged and green;
- representative M03-M06 quality compatibility remains green;
- full repository regression is green except any unchanged documented environment-only `pip check` mismatch;
- no M08+ implementation exists;
- matching builder log is committed and pushed;
- final post-log-publication local HEAD equals `origin/main` and the actual equality is recorded in the log.

## 10. Stop boundary

After pushing C003 implementation/evidence and matching builder log to canonical `main`:

- verify final local HEAD / `origin/main` equality;
- record the result in the log;
- stop;
- return the C003 builder log to ChatGPT for independent strict audit.

Do not declare M07 passed. Do not edit task checkboxes, `.hiveai/TASKS.md`, `.hiveai/EVENTS.jsonl`, `.hiveai/CYCLE_INDEX.md` or `.hiveai/audits/**`. Do not begin M08+.