# PAG-M06-C002 — WFC Remap, Stage Replay & Router Evidence Remediation

Document role: CODEX REMEDIATION PROMPT

Status: AUTHORITATIVE / READY_FOR_IMPLEMENTATION
Builder: Codex
Independent auditor / tracker owner: ChatGPT
Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`
Canonical branch: `main`

Previous independent strict audit:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M06-C001_HYBRID_GENERATOR_ROUTER_STRICT_AUDIT.md`

Previous implementation prompt:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/PAG-M06-C001_HYBRID_GENERATOR_ROUTER_PROMPT.md`

## 1. Scope

This is a bounded M06 remediation for exactly four findings:

- `F-PAG-M06-C001-001` — WFC-detail source→target palette remap is incorrectly forced to outer-palette identity.
- `F-PAG-M06-C001-002` — `reproduce_hybrid()` does not replay and verify every recorded stage.
- `F-PAG-M06-C001-003` — AUTO fallback/selection acceptance evidence is incomplete.
- `F-PAG-M06-C001-004` — topology review evidence and WFC-detail golden evidence are incomplete.

Preserve the validated M06 router architecture and all accepted M03-M05 engines.

Do not begin PAG-M07+.

## 2. GitHub-first v3 authority

GitHub is the sole current-state authority.

Before work, read completely from `main`:

1. `.hiveai/PROJECT.json`
2. `.hiveai/RULES.md`
3. the machine block in `.hiveai/TASKS.md`
4. `.hiveai/EVENTS.jsonl`
5. `tasks.md` for the detailed project ledger
6. `.hiveai/CYCLE_INDEX.md` for historical cycle records
7. `AGENTS.md`
8. `GOVERNANCE.md`
9. C001 builder log
10. C001 strict audit
11. current M06 router/hybrid source/tests/review/goldens
12. this prompt

Do not use removed legacy files such as:

- `.hiveai/HANDOFF.md`
- `.hiveai/STATE.json`
- `.hiveai/PROJECT_DASHBOARD.md`

as task authority.

Do not search sibling local repositories.

## 3. Matching builder log

Create before the first source/test/golden/review edit:

`.hiveai/codex-logs/PAG-M06-C002_WFC_REMAP_STAGE_REPLAY_AND_ROUTER_EVIDENCE_REMEDIATION_CODEX_LOG.md`

Exact H1:

`# PAG-M06-C002 — WFC Remap, Stage Replay & Router Evidence Remediation`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record chronologically:

- GitHub authority/prompt/audit URLs;
- starting branch/HEAD/origin/status;
- synchronization;
- mandatory reads;
- exact fix per finding;
- commands and failed attempts;
- focused tests;
- regenerated review/golden evidence;
- full regression;
- implementation commit SHA(s);
- push/equality checkpoint;
- final changed-file summary.

Do not self-audit.

Do not modify ChatGPT-owned acceptance state in:

- `.hiveai/TASKS.md`
- `.hiveai/EVENTS.jsonl`
- `tasks.md`
- `.hiveai/CYCLE_INDEX.md`
- `.hiveai/audits/**`.

## 4. Finding F-PAG-M06-C001-001 — WFC-detail palette remap

### Current defect

Current WFC-detail composition overwrites WFC options with an identity mapping derived from the outer target palette:

```python
wfc_values["palette_mapping"] = {
    source: target
    for source, target in zip(palette, palette, strict=True)
}
```

This only works when exemplar source C-IDs already equal the outer palette C-IDs.

M05 explicitly supports deterministic source→target remapping.

A valid exemplar may use:

```text
source: C11 C12 C13
target: C01 C02 C03
```

Current HYBRID incorrectly sends:

```text
C01 -> C01
C02 -> C02
C03 -> C03
```

which M05 correctly rejects because mapping keys do not match exemplar source IDs.

### Required target behavior

Do not synthesize an identity map from the outer target palette.

Preferred behavior:

- if nested `wfc_options.palette_mapping` is absent:
  - pass no explicit mapping;
  - allow M05 `canonical_palette_mapping()` to deterministically map exemplar source palette to the exact outer target palette.
- if a nested explicit mapping is supplied:
  - preserve it unchanged;
  - let M05 validate that its source keys match the exemplar and its target values equal the outer palette.

Do not bypass M05 validation.

Do not inspect or mutate upstream exemplar internals merely to recreate M05's mapping algorithm in M06.

### Required tests

Use an injected synthetic test-only exemplar whose source IDs differ from the outer target palette.

At minimum:

- RULE_BASE_WFC_DETAIL succeeds with default M05 mapping;
- MASK_BASE_WFC_DETAIL succeeds with default M05 mapping;
- both are deterministic;
- both use exact outer palette;
- both preserve base topology;
- a valid explicit non-identity mapping is honored;
- invalid explicit mapping fails through M05;
- caller mapping is never silently overwritten.

## 5. Finding F-PAG-M06-C001-002 — true metadata-driven stage replay

### Current defect

Current `reproduce_hybrid()` only:

1. re-runs the whole HYBRID request using current code/defaults;
2. compares final logical-grid digest;
3. compares stage-seed tuple.

That is not sufficient for PAG-0616.

### Required target behavior

Implement an actual metadata replay/verifier.

It must use the recorded `HybridCandidate` stage metadata as evidence, not merely current defaults.

For every recorded stage:

1. verify stage index/order/name/kind;
2. rederive and compare the recorded stage seed;
3. reconstruct the child GenerationRequest represented by `stage.child_request`;
4. verify child request digest;
5. invoke the same engine/composition stage;
6. verify actual engine ID/version;
7. verify child result/output digest;
8. verify geometry/topology digest;
9. verify engine-specific metadata:
   - MASK family + mask digest where recorded;
   - RULES recipe/canvas/region digest where recorded;
   - WFC exemplar ID + pattern-table digest + attempt where recorded.
10. verify final topology digest;
11. verify final logical-grid digest;
12. verify final GenerationResult digest.

### Composition-only stages

The two direct composition/color stages are not full accepted generators.

Do not pretend they are MASK/RULES engine invocations.

Represent them explicitly and truthfully, for example:

- stage_kind = `COMPOSITION`
- engine/helper ID = stable project helper identity such as `rule-colorize` or `mask-symmetry-compose`
- stable helper version.

Replay them through the exact logical helper used in production.

Do not introduce image operations.

### Metadata corruption tests

Copy/reconstruct metadata with exactly one corrupted field and prove replay rejects it.

At minimum corruption cases:

- stage seed;
- child request digest;
- engine version;
- child result digest;
- geometry digest;
- WFC pattern-table digest;
- final grid digest.

The replay helper must fail deterministically.

### Historical-default independence

Where stage metadata already records explicit child config, replay must reconstruct that child config rather than silently relying on a new current default.

## 6. Finding F-PAG-M06-C001-003 — AUTO acceptance

The current source architecture may be retained if tests confirm it.

Required tests:

### Seed determinism/diversity

- same AUTO request + same seed -> same initial selection;
- fixed seed set across default candidates MASK/RULES -> at least two selected modes.

Do not assert a specific seed→mode mapping unless needed for a fixture.

### fallback=false

Construct a selected engine that deterministically fails.

Assert:

- exactly one engine is attempted;
- no next candidate is invoked;
- outer AUTO request is preserved;
- failure reason identifies selected engine failure stably.

### fallback=true success

Construct ordered candidates where initial selected engine fails and next cyclic candidate succeeds.

Assert:

- cyclic order is deterministic;
- failed attempt is recorded;
- failure code is retained;
- successful attempt engine ID/version is recorded;
- final GenerationResult uses original AUTO request/mode/master seed;
- exact outer dimensions/palette preserved.

### fallback=true all fail

Assert:

- every candidate tried once in deterministic cyclic order;
- stable bounded exhaustion summary;
- same request yields byte-identical failure.

### Explicit HYBRID route

Add:

- router explicit HYBRID result == direct HybridGenerator result for the same root request/RNG;
- no fallback occurs.

## 7. Finding F-PAG-M06-C001-004 — topology review and WFC-detail golden

### Review manifest

Keep >=12 accepted examples.

Add explicit topology evidence for applicable strategies.

For each candidate include enough row-major data to render and verify:

- topology before transformation/detail stage;
- topology after transformation/detail stage;
- final topology.

A compact boolean/0-1 row-major array is acceptable.

Required examples:

#### MASK_GEOMETRY_RULE_COLOR_REGIONS
- source MASK foreground topology;
- final topology;
- exact equality.

#### RULE_GEOMETRY_MASK_SYMMETRY
- source RULES occupancy topology;
- transformed symmetry topology;
- final topology.

#### RULE_BASE_WFC_DETAIL
- RULES base topology;
- final topology;
- exact equality.

#### MASK_BASE_WFC_DETAIL
- MASK base topology;
- final topology;
- exact equality.

### Contact sheet

Render topology panels beside final colored output.

At minimum show:

- Before topology
- After/final topology
- Final colored logical grid

For symmetry strategy show all three when before != after.

No network/CDN/script dependency.

### Review validation

Add tests proving:

- each topology array length == width×height;
- digest of topology array equals recorded topology digest;
- WFC-detail before == final topology;
- MASK_GEOMETRY before == final topology;
- symmetry after == final topology.

### WFC-detail golden

WFC-detail has already demonstrated stable accepted output, so add at least one WFC-detail golden.

Use a synthetic test-only exemplar.

Golden must record/validate:

- strategy;
- outer request;
- exemplar ID/ownership;
- stage seeds;
- stage engine/helper IDs/versions;
- child request digests;
- child result/output digests;
- geometry/topology digests;
- WFC pattern-table digest;
- final grid digest;
- final GenerationResult digest.

Do not fabricate owner-approved art.

## 8. Preserve validated behavior

Do not rewrite without necessity:

- explicit router dispatch;
- GeneratorMode.AUTO parser;
- root-RNG coherence;
- AUTO outer result wrapping;
- MASK_GEOMETRY_RULE_COLOR_REGIONS core;
- RULE_GEOMETRY_MASK_SYMMETRY core;
- exact outer dimensions/palette handling;
- final topology/palette/component rejection;
- bounded hybrid retries;
- offline boundary.

Do not modify M03/M04/M05 generator behavior.

## 9. M06 acceptance rerun

Rerun:

- explicit router tests;
- AUTO tests;
- all four hybrid strategy tests;
- non-identity WFC remap tests;
- topology rejection tests;
- metadata replay/corruption tests;
- M06 golden tests;
- review evidence tests;
- 24-case robust acceptance matrix or stronger equivalent;
- WFC-detail deterministic acceptance examples;
- cross-process determinism;
- offline source-policy scans;
- full M00-M05 regression;
- full repository pytest;
- standalone import;
- `pip check`;
- `git diff --check`;
- no M07+ source scan.

C001 builder baseline:

- full repository: 241 PASS
- robust hybrid acceptance: 24 accepted
- review candidates: 14

The suite should grow.

## 10. Security / prohibited shortcuts

Do not:

- bypass M05 palette mapping;
- use identity mapping unless the exemplar source really equals target and M05 accepts it naturally;
- mutate recorded metadata to make replay pass;
- implement replay as only a second full request rerun;
- ignore corrupted stage metadata;
- hide AUTO failed attempts when fallback=true;
- resize/crop/interpolate topology evidence;
- synthesize topology masks from a final colored grid when the requirement is to show the actual before-stage topology;
- start M07+;
- edit ChatGPT-owned tracker/audit state;
- self-audit.

## 11. Builder exit criteria

Builder may stop as implementation complete / pending independent audit only when:

- non-identity WFC exemplar mapping works in both WFC-detail strategies;
- valid explicit mapping is preserved;
- metadata replay reconstructs and validates every recorded stage;
- corruption tests fail closed;
- AUTO fallback=true and all-fail paths are covered;
- fixed-seed AUTO selection diversity is proven;
- explicit HYBRID routing equals direct HybridGenerator;
- review includes actual before/after topology panels;
- WFC-detail golden exists;
- M06 acceptance/regression is green;
- no M07+ implementation exists;
- matching C002 builder log is published;
- implementation commit(s), push result, and equality checkpoint are recorded.

Do not close M06. ChatGPT will independently re-audit.
