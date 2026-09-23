# SB-LF04-001-C001 — Versioned LevelMetrics Contract — Strict Audit

Document role: INDEPENDENT CHATGPT STRICT AUDIT

## 1. VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

- BLOCKER: 0
- MAJOR: 1
- MINOR: 0

## 2. AUDITED CHAIN

- Prompt: `.hiveai/prompts/SB-LF04-001-C001_VERSIONED_LEVEL_METRICS_CONTRACT_PROMPT.md`
- Audit criteria: `.hiveai/audit-criteria/SB-LF04-001-C001_VERSIONED_LEVEL_METRICS_CONTRACT_AUDIT_CRITERIA.md`
- Builder log: `.hiveai/codex-logs/SB-LF04-001-C001_VERSIONED_LEVEL_METRICS_CONTRACT_CODEX_LOG.md`
- Implementation commit: `39ffe413694ebc0e3d086d14e183a07b726dba8b`
- Terminal builder-log commit: `86c0b828ceaa307374f267feac41021efefa5406`
- Audit snapshot HEAD: `86c0b828ceaa307374f267feac41021efefa5406`

## 3. PRODUCT CONTRACT REVIEW

The LevelMetrics V1 implementation is materially correct and retained.

Positive findings:

- dedicated immutable `level_metrics.py` contract;
- explicit LevelMetrics schema/version;
- exact `LevelIdentity` source SHA-256 binding;
- exact canonical `SolverStateAuthority` binding;
- accepted M03 solver-evidence schema/version/digest identity;
- closed `AnalysisDisposition`;
- closed typed `MetricId` / `MetricValues` catalog;
- no unrestricted metric bag;
- missing metrics remain absent rather than fabricated zero;
- non-AVAILABLE dispositions cannot carry measurements;
- closed nested parsing rejects unknown fields/schema/version;
- malformed hashes/types and NaN/Infinity fail closed;
- mutable parsed mappings do not alias accepted immutable objects;
- operational elapsed/timeout/path/process/UI state is absent from canonical fields;
- production width/height and used-color envelopes remain independent from difficulty classification;
- no Challenge Score calculation;
- no gameplay invocation or copied gameplay semantics;
- no WFC-as-difficulty truth;
- no builder modification of root TASKS.

No product-code finding justifies redesigning LevelMetrics.

## 4. FOCUSED TEST EVIDENCE

Builder reports:

- focused SB-LF04-001: `11 passed`;
- compileall PASS;
- Godot headless editor boot PASS;
- `git diff --check` PASS;
- TASKS builder diff zero.

Focused source inspection supports those contract claims.

## 5. MAJOR-001 — REQUIRED FULL REPOSITORY GATE IS RED ON THE SUPPORTED WINDOWS WORKTREE

The audit criteria explicitly require:

`full repository pytest green`

The builder's final full suite is:

`865 passed, 1 skipped, 2 failed`

Failing tests:

- `test_real_canonical_capability_and_runner_are_capability_gated`
- `test_real_canonical_bridge_fixture_executes_declarative_operations`

Both fail because the Level-Factory-owned external bridge runner reports:

`configured external bridge runner identity drifted`

The builder deselected the real-canonical cases for a retained sub-suite, but deselection cannot satisfy the required full repository gate.

### Independent root-cause check

This audit independently fetched:

- `src/scrubbots_pixel_factory/canonical_bridge.py`
- `tools/scrubbots_canonical_bridge_runner.gd`

The pinned runner identity is:

`b66f307c4103a714d02b03ce61e7413e3ff07e0e90fb19b3417cc54afef05c3f`

SHA-256 independently computed from the committed GitHub runner UTF-8 bytes is exactly the same value.

Therefore the repository source itself has not drifted.

The failure occurs because the Windows execution worktree can materialize the runner with checkout-dependent line endings while `CanonicalHeadlessBridge` intentionally verifies exact physical runner bytes.

The repository currently has no `.gitattributes` rule pinning this security-sensitive runner to LF checkout bytes.

This is a real cross-platform repository/test portability defect. It is not acceptable to call the mandatory full-suite gate green by excluding the affected tests.

## 6. REQUIRED REMEDIATION

Open a narrow `SB-LF04-001-C001-R01` acceptance-gate remediation.

Retain the LevelMetrics implementation unchanged unless a regression forces a compatibility-only adjustment.

Fix the runner checkout-byte portability without weakening exact runner identity.

Preferred remediation:

- add a narrow repository `.gitattributes` rule for:
  `tools/scrubbots_canonical_bridge_runner.gd text eol=lf`;
- keep the existing pinned SHA-256 unchanged;
- do not repin to CRLF bytes;
- do not normalize bytes inside the bridge before hashing;
- add a portability regression proving a fresh Windows-style/local checkout with `core.autocrlf=true` still materializes runner bytes whose SHA-256 equals `CANONICAL_BRIDGE_RUNNER_SHA256`;
- rerun the two real canonical bridge tests without deselection;
- rerun the full repository suite and require zero failures.

No M04-002 work is authorized during R01.

## 7. FINAL VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

SB-LF04-001 remains the sole active task until the required repository-wide test gate is green.
