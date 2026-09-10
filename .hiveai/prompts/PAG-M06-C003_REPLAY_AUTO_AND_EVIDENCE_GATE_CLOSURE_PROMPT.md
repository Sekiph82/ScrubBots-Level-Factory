# PAG-M06-C003 — Replay, AUTO & Evidence Gate Closure

Document role: CODEX REMEDIATION PROMPT

Status: AUTHORITATIVE / READY_FOR_IMPLEMENTATION  
Builder: Codex  
Independent auditor / tracker owner: ChatGPT  
Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`  
Canonical branch: `main`

Authoritative C002 strict audit:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M06-C002_WFC_REMAP_STAGE_REPLAY_AND_ROUTER_EVIDENCE_REMEDIATION_STRICT_AUDIT.md`

C002 builder log:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/PAG-M06-C002_WFC_REMAP_STAGE_REPLAY_AND_ROUTER_EVIDENCE_REMEDIATION_CODEX_LOG.md`

C002 implementation prompt:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/PAG-M06-C002_WFC_REMAP_STAGE_REPLAY_AND_ROUTER_EVIDENCE_REMEDIATION_PROMPT.md`

Canonical repository:
`https://github.com/Sekiph82/ScrubBots-Level-Factory`

## 1. Scope

This is a **bounded M06 evidence-closure remediation** for exactly these C002 findings:

- `F-PAG-M06-C002-001` — required WFC-detail golden/review evidence is incomplete.
- `F-PAG-M06-C002-002` — required AUTO acceptance evidence is incomplete.

Preserve the accepted C002 functional changes:

- WFC-detail must continue to let M05 perform canonical source→target mapping when no explicit mapping is supplied;
- caller-supplied valid WFC mapping must remain unchanged;
- `replay_candidate()` / `reproduce_hybrid()` must remain metadata-driven stage replay;
- composition stages remain explicit `COMPOSITION` stages;
- topology evidence remains actual before/after/final occupancy evidence;
- explicit router behavior and deterministic AUTO implementation remain intact.

Do **not** rewrite production router/hybrid logic unless a newly added focused test exposes a real contradiction.

Do not begin PAG-M07+.

## 2. GitHub-first v3 authority

GitHub `main` is the sole current-state authority.

Before work, read completely from GitHub:

1. `.hiveai/PROJECT.json`
2. `.hiveai/RULES.md`
3. the v3 machine block in `.hiveai/TASKS.md`
4. `.hiveai/EVENTS.jsonl`
5. `tasks.md`
6. `.hiveai/CYCLE_INDEX.md`
7. `AGENTS.md`
8. `GOVERNANCE.md`
9. C002 prompt
10. C002 builder log
11. C002 strict audit
12. current M06 source/tests/review/golden files
13. this C003 prompt

Do not use removed legacy projections as authority. Do not search sibling local repositories.

## 3. Matching builder log

Before the first implementation/test/evidence edit create:

`.hiveai/codex-logs/PAG-M06-C003_REPLAY_AUTO_AND_EVIDENCE_GATE_CLOSURE_CODEX_LOG.md`

Exact H1:

`# PAG-M06-C003 — Replay, AUTO & Evidence Gate Closure`

Immediately below:

`Document role: CODEX BUILDER LOG`

Log chronologically:

- authority URLs;
- starting branch/HEAD/origin/status;
- synchronization;
- mandatory reads;
- each finding and exact change;
- commands, failed attempts and corrections;
- focused tests;
- full regression;
- final changed-file summary;
- implementation commit SHA(s);
- push result;
- final local HEAD / `origin/main` equality.

Do not self-audit and do not edit ChatGPT-owned acceptance state.

## 4. Finding F-PAG-M06-C002-001 — complete WFC-detail golden/review evidence

### 4.1 WFC-detail golden schema

The existing synthetic WFC-detail golden is valid but incomplete.

Update `tests/golden/m06_hybrid_goldens.json` and `tests/golden/test_m06_hybrid_golden.py` so at least one accepted WFC-detail golden records **and validates** all of the following:

- strategy;
- complete outer request/config required to reconstruct the case;
- exemplar ID;
- exemplar ownership = `SYNTHETIC_TEST_ONLY`;
- stage seeds;
- stage engine/helper IDs and versions;
- child request digests;
- child result/output digests;
- **stage geometry/topology digests** for every stage where applicable;
- **WFC `pattern_table_digest`**;
- WFC attempt if it is part of recorded WFC stage evidence;
- actual palette mapping;
- final topology digest;
- final logical-grid digest;
- final `GenerationResult` digest.

The test must compare these fields against the newly generated `HybridCandidate` / stage metadata. Merely storing fields in JSON is insufficient.

Do not fabricate owner-approved art. Continue using a synthetic test-only exemplar whose source IDs differ from the outer target palette.

### 4.2 Review topology validation

Strengthen `tests/integration/test_m06_review_evidence.py` so it explicitly proves:

- every `before`, `after`, and `final` row-major topology array has exactly `width * height` cells;
- every topology cell is exactly 0 or 1;
- final topology array digest equals `final_topology_digest`;
- `MASK_GEOMETRY_RULE_COLOR_REGIONS`: before == final and the source MASK topology digest is bound to the relevant recorded stage evidence;
- `RULE_BASE_WFC_DETAIL`: before == final;
- `MASK_BASE_WFC_DETAIL`: before == final;
- both WFC-detail cases bind the base topology and final topology to the relevant recorded stage/final digest evidence;
- `RULE_GEOMETRY_MASK_SYMMETRY`: before and after are bound to the composition stage's recorded `before_topology_digest` / `after_topology_digest`, and after == final;
- the contact sheet still contains no network/CDN/script dependency and renders the required topology panels.

If the current review manifest lacks a specific digest needed for an unambiguous binding, extend the review builder/manifest minimally and regenerate the committed review artifacts. Do not derive a fake “before” topology from the final colored grid.

## 5. Finding F-PAG-M06-C002-002 — complete exact AUTO acceptance evidence

Production AUTO source should remain unchanged unless these tests expose a real bug.

Add/strengthen focused tests in `tests/integration/test_m06_router.py`.

### 5.1 Same-seed repeatability

For the exact same AUTO `GenerationRequest` and seed, call the router at least twice and assert:

- identical initial selection;
- identical candidate order;
- identical attempt sequence where applicable;
- byte-identical final result for a deterministic successful case.

Keep the existing fixed-seed diversity test proving both default modes can be selected.

### 5.2 `fallback_on_failure=false` with a real alternative present

This test must configure **at least two candidates**.

Arrange the deterministic initial selection so the first selected engine fails. Use call-recording/spies/sentinels for both selected and next candidate.

Assert:

- selected failing engine called exactly once;
- next configured candidate called zero times;
- only one attempt is made;
- no hidden mode switch occurs;
- returned failure retains the original AUTO request/mode/master seed;
- failure reason stably identifies the selected engine failure;
- repeated identical request produces byte-identical failure.

A single-candidate list does not satisfy this acceptance case.

### 5.3 `fallback_on_failure=true` success

Use an ordered candidate list where deterministic initial selection fails and the next cyclic candidate succeeds.

Assert explicitly:

- exact global attempt order;
- first failed attempt retained with stable failure code;
- successful attempt engine ID and version recorded;
- `AutoCandidate.selected_mode` equals the successful mode;
- final result retains the original AUTO request;
- final `generator_mode == AUTO`;
- final/master seed equals outer request seed;
- final width and height equal the outer request dimensions;
- final used palette equals the exact outer resolved palette;
- repeated identical request is byte-identical.

### 5.4 `fallback_on_failure=true` all fail

Use one shared global call recorder across all sentinel engines.

Assert for one run:

- every configured candidate is attempted exactly once;
- complete global order equals deterministic cyclic order starting from initial selection;
- no candidate is retried;
- returned failure is bounded `RETRY_EXHAUSTED`;
- exhaustion summary is stable.

Repeat the same request with a fresh recorder/router and assert byte-identical failure **and the same global order**.

### 5.5 Explicit HYBRID

Retain the existing direct HybridGenerator vs explicit router canonical-byte equality test and ensure no AUTO fallback path is involved.

## 6. Replay corruption test-strength hardening

This is not a new C002 blocker, but C003 should strengthen the existing replay corruption tests if it can be done without production redesign.

Current tests mutate the serialized `candidate.metadata["stages"]` while the separate `candidate.stages` copy remains original. That may trigger the duplicate-consistency guard before the intended field-specific verifier.

Preferred test helper:

- reconstruct a candidate whose two mirrored stage representations are mutually consistent;
- corrupt exactly one semantic field in both representations where necessary to pass the mirror guard;
- prove replay then fails at the semantic verifier for representative fields such as seed, engine version, result digest, geometry digest, WFC pattern-table digest;
- retain a separate test proving a mismatch between the two copies is rejected.

Do not weaken or remove the mirror-consistency guard.

## 7. Preserve validated behavior

Do not regress:

- M03/M04/M05 engines;
- default and explicit non-identity WFC mapping behavior from C002;
- exact outer dimensions/palette;
- topology rejection;
- composition stage truthfulness;
- metadata-driven replay;
- deterministic RNG/root-stream rules;
- explicit route equality;
- offline-only runtime;
- no interpolation/resizing.

No new runtime dependency is authorized.

## 8. Required verification

At minimum run:

- focused M06 router/AUTO tests;
- replay/corruption tests;
- WFC-detail mapping tests;
- M06 review evidence tests;
- M06 golden tests;
- M06 acceptance matrix;
- cross-process determinism checks already present;
- M00-M05 regression suites;
- full repository pytest;
- standalone import;
- offline/network source-policy checks;
- `pip check`;
- `git diff --check`;
- M07+ source-scope scan.

C002 builder baseline was:

- full suite: `247 passed, 1 warning`;
- robust hybrid matrix: 24 accepted cases;
- review set: >=12 cases.

The test count should grow unless an existing test is legitimately strengthened in place.

The pre-existing pytest/pytest-asyncio `pip check` mismatch may be recorded as an unchanged environment issue. Do not modify unrelated dependencies merely to make this bounded cycle green.

## 9. Prohibited shortcuts

Do not:

- remove required golden fields to make tests simpler;
- populate golden digest fields without independently comparing them in tests;
- use only a one-candidate AUTO list for fallback=false acceptance;
- infer global cyclic order from per-engine call totals;
- suppress failed AUTO attempts;
- change deterministic selection to satisfy one fixture;
- weaken replay checks;
- bypass M05 WFC validation;
- synthesize before-topology from final art;
- alter task/audit acceptance files;
- rewrite C001/C002 history;
- begin PAG-M07+;
- self-audit.

## 10. Builder exit criteria

Builder may stop as implementation/evidence complete and pending independent audit only when:

- WFC-detail golden records **and test-validates** stage geometry/topology digests and WFC pattern-table digest plus all prior required fields;
- review tests explicitly cover both WFC-detail before==final relationships and all applicable digest bindings;
- same-seed AUTO repeatability has an explicit test;
- fallback=false is proven with at least two configured candidates and next-engine call count zero;
- fallback=true success asserts exact outer dimensions/palette and selected engine/version provenance;
- all-fail proves the full global deterministic cyclic order with one attempt per candidate;
- replay corruption test-strength hardening is complete or the log explains precisely why no change was required;
- full focused/regression suite is green except any unchanged documented environment-only `pip check` issue;
- no M07+ implementation exists;
- matching C003 builder log is committed and pushed;
- final local HEAD equals `origin/main`;
- Codex does not declare M06 accepted.

Return to ChatGPT for independent strict re-audit.
