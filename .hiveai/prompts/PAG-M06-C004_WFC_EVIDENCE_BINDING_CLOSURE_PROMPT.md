# PAG-M06-C004 — WFC Evidence Binding Closure

Document role: CODEX REMEDIATION PROMPT

Status: AUTHORITATIVE / READY_FOR_IMPLEMENTATION  
Builder: Codex  
Independent auditor / tracker owner: ChatGPT  
Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`  
Canonical branch: `main`

Authoritative C003 strict audit:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M06-C003_REPLAY_AUTO_AND_EVIDENCE_GATE_CLOSURE_STRICT_AUDIT.md`

C003 builder log:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/PAG-M06-C003_REPLAY_AUTO_AND_EVIDENCE_GATE_CLOSURE_CODEX_LOG.md`

C003 prompt:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/PAG-M06-C003_REPLAY_AUTO_AND_EVIDENCE_GATE_CLOSURE_PROMPT.md`

## 1. Scope

This is an **evidence-only** M06 closure cycle for exactly one finding:

- `F-PAG-M06-C003-001` — WFC-detail golden/review topology and strategy evidence is stored but not fully cross-validated against generated stage metadata.

Do not redesign or refactor the production router/hybrid implementation.

Preserve all accepted C002/C003 behavior:

- M05-driven default WFC source→target mapping;
- explicit caller WFC mapping preservation;
- metadata-driven stage replay;
- explicit COMPOSITION stage semantics;
- AUTO deterministic selection and opt-in cyclic fallback;
- exact outer dimensions/palette;
- topology rejection;
- offline-only operation;
- no interpolation/resizing.

Do not begin PAG-M07+.

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
9. C003 prompt
10. C003 builder log
11. C003 strict audit
12. current M06 golden/review tests and evidence
13. this C004 prompt

GitHub `main` is current-state authority. Do not use removed legacy local projections as authority and do not search sibling repositories.

## 3. Matching builder log

Before the first C004 test/evidence edit create:

`.hiveai/codex-logs/PAG-M06-C004_WFC_EVIDENCE_BINDING_CLOSURE_CODEX_LOG.md`

Exact H1:

`# PAG-M06-C004 — WFC Evidence Binding Closure`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record chronologically:

- authority URLs;
- starting branch/HEAD/origin/status;
- synchronization;
- mandatory reads;
- exact evidence changes;
- commands and any failed attempts;
- focused tests;
- full regression;
- final changed files;
- implementation commit SHA(s);
- push result;
- final local HEAD / `origin/main` equality.

Do not self-audit and do not edit ChatGPT-owned acceptance state.

## 4. Finding F-PAG-M06-C003-001

### 4.1 Golden strategy must be validated, not merely stored

Affected file:

- `tests/golden/test_m06_hybrid_golden.py`

For every WFC-detail golden entry, explicitly assert:

- `golden["strategy"] == candidate.strategy`;
- top-level `golden["strategy"]` equals the strategy inside the reconstructed outer request's hybrid generator options;
- the generated candidate/result still matches all existing final/stage digests.

The test must fail if only the top-level golden strategy field is corrupted while request/config and digests are left unchanged.

Do not remove the redundant strategy field merely to avoid validating it; C003 already committed it as part of the evidence schema.

### 4.2 Golden base topology must be directly tied to generated stage evidence

For the WFC-detail golden, directly prove the applicable base stage topology relationship:

- `golden["stage_topology_digests"][0] == candidate.stages[0].geometry_digest`;
- that same digest equals the recomputed `before` topology digest;
- if the base stage is RULES, bind it to `candidate.stages[0].extra["canvas_digest"]` where recorded;
- if a MASK_BASE WFC-detail golden is added, bind it to `candidate.stages[0].extra["mask_digest"]` where recorded;
- WFC detail stage topology may remain `null` if the stage's `geometry_digest` intentionally describes WFC output rather than preserved base occupancy;
- final topology digest remains bound to `candidate.metadata["final_topology_digest"]`.

A golden-to-golden self-comparison alone is not sufficient.

### 4.3 Review evidence must bind both WFC-detail base stages to recorded stage digests

Affected file:

- `tests/integration/test_m06_review_evidence.py`

For both:

- `RULE_BASE_WFC_DETAIL`
- `MASK_BASE_WFC_DETAIL`

assert directly that:

- `topology["before"] == topology["final"]`;
- `topology_digests["before"] == stages[0]["geometry_digest"]`;
- `topology_digests["final"] == entry["final_topology_digest"]`;
- the first `topology_bindings` entry names the actual base stage and carries that exact base-stage digest;
- the final binding names `FINAL` and carries `final_topology_digest`;
- for RULE base, `stages[0]["extra"]["canvas_digest"] == topology_digests["before"]`;
- for MASK base, `stages[0]["extra"]["mask_digest"] == topology_digests["before"]`.

This is the central C004 acceptance gate.

If existing manifest data already contains everything necessary, do **not** change `review/m06/build_review.py` or regenerate large artifacts unnecessarily. Modify only tests if the current evidence is sufficient.

If an unambiguous binding field is genuinely missing, extend the review builder/manifest minimally and regenerate only the affected evidence.

## 5. Negative evidence tests

Add a focused negative test or parameterized assertion proving the evidence checks are meaningful.

At minimum demonstrate that one of the following causes the evidence validation to fail:

- corrupt WFC golden top-level `strategy` only;
- corrupt a WFC-detail base topology binding digest while leaving topology arrays unchanged;
- corrupt the recorded base-stage geometry digest while leaving the binding/topology arrays unchanged.

Do not mutate production code to manufacture this failure.

## 6. Preserve C003 AUTO and replay tests

Do not weaken, delete, or replace the C003 tests that now prove:

- same-seed AUTO repeatability;
- default seed diversity;
- multi-candidate fallback=false with next-engine zero calls;
- successful cyclic fallback outer contract and engine/version provenance;
- all-fail exact global cyclic order;
- direct HYBRID route equality;
- semantic replay corruption rejection;
- mirror-consistency rejection.

No new AUTO production change is authorized.

## 7. Required verification

At minimum run:

- `tests/golden/test_m06_hybrid_golden.py`;
- `tests/integration/test_m06_review_evidence.py`;
- `tests/integration/test_m06_router.py`;
- `tests/acceptance/test_m06_hybrid_acceptance.py`;
- full M06 focused suite;
- M00-M05 regression suites;
- full repository pytest;
- standalone import;
- offline/network source-policy scan;
- no-resize/interpolation scan;
- `pip check`;
- `git diff --check`;
- M07+ source-scope scan.

C003 builder baseline:

- full repository: `249 passed, 1 warning`;
- M06 focused + acceptance matrix: `19 passed`;
- review candidates: `14`.

The unchanged pytest/pytest-asyncio environment mismatch may remain documented. Do not alter unrelated dependencies.

## 8. Prohibited shortcuts

Do not:

- remove evidence fields instead of validating them;
- validate WFC base topology only by stage name;
- compare a binding only to another derived binding field without anchoring it to generated stage metadata;
- regenerate production output or change routing logic merely to satisfy evidence assertions;
- weaken C003 AUTO/replay tests;
- bypass M05 WFC validation;
- resize/interpolate evidence;
- edit `.hiveai/TASKS.md`, `.hiveai/EVENTS.jsonl`, `tasks.md`, `.hiveai/CYCLE_INDEX.md`, `.hiveai/audits/**`, or used prompt history;
- begin PAG-M07+;
- self-audit.

## 9. Builder exit criteria

Builder may stop as implementation/evidence complete and pending independent audit only when:

- WFC golden top-level strategy is explicitly validated against generated candidate and reconstructed request config;
- WFC golden base topology digest is directly bound to generated base-stage geometry/engine-specific digest evidence;
- both WFC-detail review cases directly bind base topology to recorded base-stage digest evidence;
- final topology bindings remain exact;
- at least one negative evidence-corruption test proves these checks fail closed;
- no production source change exists unless a focused test found and documented a real contradiction;
- all C003 AUTO/replay tests remain green;
- focused/full regression is green except the documented unchanged environment-only `pip check` mismatch;
- no M07+ implementation exists;
- matching C004 builder log is committed and pushed;
- final local HEAD equals `origin/main`;
- Codex does not declare M06 accepted.

Return the C004 builder log to ChatGPT for independent strict re-audit.
