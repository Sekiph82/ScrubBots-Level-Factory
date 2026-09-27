# SB-LF09-002-C001 — Versioned Fitness Metrics

Document role: INDEPENDENT CHATGPT STRICT AUDIT

## VERDICT

**CHANGES_REQUIRED**

The published implementation establishes a closed, canonically serialized,
deterministic evidence-only fitness policy and preserves the offline,
experimental, no-promotion boundary. It does not yet close the caller-forged
fitness-result boundary: a caller can rehash an altered `CandidateFitness`,
place it in a rehashed `FitnessEvaluation`, and retrieve it through the public
`for_candidate()` path without artifact recomputation. The deserializer also
accepts duplicate candidate results, so the evaluation container is not fully
canonical or unambiguous.

## CONTRACT RECOVERY

- Repository: `Sekiph82/ScrubBots-Level-Factory`
- Branch: `main`
- Audited live head: [d7028e1dec6b03d0228f5cf9d0377074b07b70a3](https://github.com/Sekiph82/ScrubBots-Level-Factory/commit/d7028e1dec6b03d0228f5cf9d0377074b07b70a3)
- Prompt: [SB-LF09-002-C001 prompt](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/d7028e1dec6b03d0228f5cf9d0377074b07b70a3/.hiveai/prompts/SB-LF09-002-C001_VERSIONED_FITNESS_METRICS_PROMPT.md)
- Audit criteria: [SB-LF09-002-C001 criteria](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/d7028e1dec6b03d0228f5cf9d0377074b07b70a3/.hiveai/audit-criteria/SB-LF09-002-C001_VERSIONED_FITNESS_METRICS_AUDIT_CRITERIA.md)
- Previous independent audit: [SB-LF09-001-C001-R02 strict audit](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/d7028e1dec6b03d0228f5cf9d0377074b07b70a3/.hiveai/audits/SB-LF09-001-C001-R02_COMPLETE_CROSS_CANDIDATE_ARTIFACT_IDENTITY_STRICT_AUDIT.md)
- Implementation commit: [d8718f69b32fc6d1960c01ac42c80522bf9c2de4](https://github.com/Sekiph82/ScrubBots-Level-Factory/commit/d8718f69b32fc6d1960c01ac42c80522bf9c2de4)
- Separate log publication commit: [c8125cd96d53b95ab77842834ba5d7e93a199dcf](https://github.com/Sekiph82/ScrubBots-Level-Factory/commit/c8125cd96d53b95ab77842834ba5d7e93a199dcf)
- Final handoff append: [d7028e1dec6b03d0228f5cf9d0377074b07b70a3](https://github.com/Sekiph82/ScrubBots-Level-Factory/commit/d7028e1dec6b03d0228f5cf9d0377074b07b70a3)
- Builder log: [published CODEX builder log](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/d7028e1dec6b03d0228f5cf9d0377074b07b70a3/.hiveai/codex-logs/SB-LF09-002-C001_VERSIONED_FITNESS_METRICS_CODEX_LOG.md)

## BRANCH / HEAD / DIFF SCOPE

The canonical owner mirror at
`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator` was dirty and
47 commits behind fetched `origin/main`; it was not reset, cleaned, stashed,
rebased, synchronized in place, or otherwise disturbed. Audit inspection used
the fetched live Git objects and a clean same-repository publication worktree.

The implementation/publication range from
`64e6795d44bc56d8eb00714c56f765432a460ebb` through
`d7028e1dec6b03d0228f5cf9d0377074b07b70a3` contains only:

- `src/scrubbots_pixel_factory/fitness_metrics.py`
- `src/scrubbots_pixel_factory/evolutionary_selection.py`
- `src/scrubbots_pixel_factory/__init__.py`
- `tests/unit/test_sb_lf09_002_fitness_metrics.py`
- the matching `.hiveai/codex-logs/` builder log

No `TASKS.md`, prompt, criteria, or ChatGPT audit file was changed by the
builder range. Independent `git diff --check` for the range passed.

## ACCEPTANCE CRITERIA MATRIX

| Criterion | Result | Evidence |
| --- | --- | --- |
| Closed metric catalog and versioned policy are explicit, canonical, and included in the policy digest | PASS | `FitnessMetricDefinition`, the closed catalog, `FitnessPolicy.canonical_dict()`, and `FitnessPolicy.digest()` are directly present in `fitness_metrics.py` lines 61-181. |
| Deterministic fitness derives from accepted evidence and policy | PASS | `evaluate_fitness()` verifies each M08 artifact set, uses integer basis-point arithmetic, sorts candidates canonically, and binds policy/result digests. The five published LF09-002 behavioral tests passed independently against the remote blobs. |
| Exact lineage/policy binding; missing, malformed, forged, stale, and cross-candidate bindings fail closed | **FAIL** | `validate_fitness_result()` recomputes and rejects the forged case, but `FitnessEvaluation.for_candidate()` only checks candidate ID and lineage at lines 300-306. A rehashed altered result was independently returned through that public path. `FitnessEvaluation.__post_init__()` and `from_dict()` also do not reject duplicate candidate IDs at lines 273-313. |
| Finite, offline, side-effect-free, experimental, production-isolated behavior | PASS | The changed source adds no network/provider/telemetry/API-key path; the selector remains explicitly opt-in and separate from production generation/publication. Static boundary inspection passed. |
| Focused tests and retained regressions | PARTIAL | The builder added six focused tests and recorded retained LF09-001/M07/M08 regressions. Independent execution passed the five behavioral tests, but no test covers rehashed forgery through `for_candidate()` or duplicate deserialization. |
| Full pytest, compileall, Godot, diff/protected checks, and truthful unavailable reporting | PARTIAL | The builder log records `1094 passed, 2 skipped`, compileall, Godot 4.7.2, diff-check, and truthful bridge skips. The range diff-check and protected-path inspection were independently reproduced; the full suite, compileall, and Godot gate were not independently rerun because the canonical mirror is dirty and stale. |

## BUILDER CLAIMS VS REPOSITORY TRUTH

The builder log truthfully records the authorized scope, failed focused runs
and corrections, separate publication commits, regression evidence, offline
review, and `AWAITING_CHATGPT_AUDIT`. Git history confirms the final live head
and marker. The builder's passing tests do not prove the public
reconstitution boundary: the missing negative cases were directly reproduced
against the published source.

## FILE / SYMBOL EVIDENCE

- The closed metric catalog and policy digest are in [`fitness_metrics.py`](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/d7028e1dec6b03d0228f5cf9d0377074b07b70a3/src/scrubbots_pixel_factory/fitness_metrics.py#L61-L181).
- Candidate result self-digests and aggregate checks are in [`CandidateFitness`](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/d7028e1dec6b03d0228f5cf9d0377074b07b70a3/src/scrubbots_pixel_factory/fitness_metrics.py#L205-L262).
- Evaluation ordering, policy binding, and deserialization are in [`FitnessEvaluation`](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/d7028e1dec6b03d0228f5cf9d0377074b07b70a3/src/scrubbots_pixel_factory/fitness_metrics.py#L265-L313).
- The unsafe public lookup is [`FitnessEvaluation.for_candidate()`](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/d7028e1dec6b03d0228f5cf9d0377074b07b70a3/src/scrubbots_pixel_factory/fitness_metrics.py#L300-L306); it does not call `validate_fitness_result()` or recompute from artifact bytes.
- The recomputation boundary that the public lookup must reuse is [`validate_fitness_result()`](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/d7028e1dec6b03d0228f5cf9d0377074b07b70a3/src/scrubbots_pixel_factory/fitness_metrics.py#L405-L418).
- Missing duplicate-ID enforcement is visible in [`FitnessEvaluation.__post_init__()` and `from_dict()`](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/d7028e1dec6b03d0228f5cf9d0377074b07b70a3/src/scrubbots_pixel_factory/fitness_metrics.py#L273-L313).
- The published tests cover the explicit validation API but not the unsafe lookup/deserialization cases at [`test_sb_lf09_002_fitness_metrics.py`](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/d7028e1dec6b03d0228f5cf9d0377074b07b70a3/tests/unit/test_sb_lf09_002_fitness_metrics.py#L150-L175).
- Selector integration and fitness provenance are in [`evolutionary_selection.py`](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/d7028e1dec6b03d0228f5cf9d0377074b07b70a3/src/scrubbots_pixel_factory/evolutionary_selection.py#L388-L455).

## FOCUSED TEST EVIDENCE

Independent remote-blob execution passed the five published behavioral tests:

- `test_closed_catalog_and_policy_digest_are_canonical_and_versioned`
- `test_fitness_replay_is_byte_identical_and_finite`
- `test_each_result_binds_exact_candidate_lineage_and_policy`
- `test_missing_or_forged_metric_evidence_fails_closed`
- `test_selection_publishes_fitness_bindings_without_production_promotion`

The same harness independently confirmed that
`validate_fitness_result()` rejects an altered but rehashed result, while
`FitnessEvaluation.for_candidate()` returns that altered result when placed in
a rehashed evaluation. It also confirmed that
`FitnessEvaluation.from_dict()` accepts two copies of the same candidate
result. An initial attempt against the dirty mirror failed because its stale
`studio_extensions.py` lacked the remote M08 symbol; the corrected harness
loaded the corresponding published dependencies from Git objects in memory.

## REGRESSION EVIDENCE

- Builder-recorded LF09-001 plus LF09-002 focused suite: `29 passed`.
- Builder-recorded retained M07/M08 suite: `79 passed`.
- Builder-recorded full suite: `1094 passed, 2 skipped`; the two skips truthfully
  report unavailable canonical ScrubBots bridge capability.
- Builder-recorded compileall and Godot 4.7.2 headless editor boot passed.
- Independent range `git diff --check` passed, and the changed path set contains
  no tracker, prompt, criteria, or audit mutation.

## SECURITY / SAFETY / OFFLINE REVIEW

No network, provider, telemetry, API-key, runtime HTTP, cloud image-generation,
production-router, or publication integration was added. The implementation
consumes accepted evidence identities and remains behind explicit experimental
opt-in. The defect is an integrity/reconstitution boundary, not a runtime
network or source-art mutation issue.

## ARCHITECTURE CONSISTENCY

The evidence-only metric design correctly reuses the M08 immutable byte
verification boundary and does not redefine difficulty, gameplay, source-art
provenance, or promotion. The R01 remediation must remain inside the fitness
receipt/evaluation boundary and its tests; it must not expand into a new
selector, generator, provider, or production integration.

## TRACKER / LOG / DOCUMENTATION TRUTHFULNESS

The builder did not edit `TASKS.md` or ChatGPT-owned audits and ended with the
required `AWAITING_CHATGPT_AUDIT` marker. This audit does not accept the task
or advance M09. The tracker is updated separately to the bounded R01
remediation authorization.

## FINAL REPOSITORY STATE

Audited live `origin/main` is
`d7028e1dec6b03d0228f5cf9d0377074b07b70a3`. The canonical owner mirror
remains untouched, dirty, and 47 commits behind. The authorized audit,
remediation prompt, criteria, and tracker update are published separately.

## OPEN CROSS-MILESTONE FINDINGS

No later M09 task, Content Platform task, main-game runtime, provider,
owner-only, native-device, physical, subjective, or unavailable bridge gate was
attempted or accepted.

## DEFECTS BY SEVERITY

- **BLOCKER — caller-forged fitness receipt accepted by public lookup:** a
  caller can change metric values, recompute the result digest and evaluation
  digest, preserve the exact candidate ID/lineage and policy digest, and obtain
  the forged result through `for_candidate()` without canonical artifact bytes
  being consulted.
- **MAJOR — duplicate evaluation entries accepted:**
  `FitnessEvaluation.from_dict()` and construction do not reject duplicate
  candidate IDs or duplicate lineage identities, despite claiming canonical
  ordered evaluation. This creates ambiguous lookup and replay behavior.

## TECHNICAL DEBT / UPGRADE OPPORTUNITIES

Keep untrusted serialized fitness data at an explicit validation boundary.
Receipt self-digests prove internal consistency, but they do not prove that a
receipt was computed from the accepted artifact bytes; only recomputation can
establish that authority.

## UNVERIFIED ITEMS

- The builder-recorded full pytest, compileall, and Godot gates were not
  independently rerun from the dirty/stale owner mirror.
- No owner-only, visual, physical, native-device, clean-machine, or external
  canonical-game bridge gate was available or converted to acceptance.

## REGRESSION RISK

R01 should remain narrow. The main risk is changing the public evaluation API
without preserving deterministic replay, exact artifact verification, the
offline boundary, and the existing selector's opt-in/no-promotion behavior.

## AUDIT CONFIDENCE

High for the two integrity defects: both were reproduced directly against the
published remote source, and the affected methods and missing tests are
line-identified. Medium for the unrerun broad gates because the owner mirror
was intentionally preserved rather than synchronized or overwritten.

## FINAL VERDICT

**CHANGES_REQUIRED** — `SB-LF09-002-C001` is not eligible for PASS/CLOSED until
caller-forged reconstituted results and duplicate evaluation entries fail
closed, focused tests cover both paths, and the bounded remediation is
independently re-audited.

## REQUIRED REMEDIATION

Proceed only with the bounded R01 prompt and criteria published alongside this
audit:

- `SB-LF09-002-C001-R01_VERSIONED_FITNESS_METRICS_REMEDIATION_PROMPT.md`
- `SB-LF09-002-C001-R01_VERSIONED_FITNESS_METRICS_AUDIT_CRITERIA.md`
