# SB-LF06-008-C001 — Factory Studio Manual Artwork Structural Revalidation — Strict Audit

Document role: INDEPENDENT CHATGPT STRICT AUDIT

## Verdict

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Severity summary:
- BLOCKER: 0
- MAJOR: 1
- MINOR: 0

## Audited builder chain

- Synchronized start / active tracker commit: `bbc4492a42a84e40cf45b119bd7f0772724081f8`
- Implementation commit: `df34197592eccc1498877478849c1f2aabeac8c4`
- Terminal builder publication: `208bf04f175ff5a07089172818f6e642aa9c0670`
- `bbc4492... -> df341975...` is exactly one implementation commit.
- `df341975... -> 208bf04...` changes only `.hiveai/codex-logs/SB-LF06-008-C001_FACTORY_STUDIO_MANUAL_ART_STRUCTURAL_REVALIDATION_CODEX_LOG.md`; publication discipline is clean.

## Accepted implementation retained

The core LF06-008 architecture is directionally correct and should be retained.

Independent source inspection confirms:

- LF06-003 `Validate` remains unavailable and is not repurposed as full validation.
- The new operation is explicitly scoped as `STRUCTURAL_ART_QA_ONLY` / `STRUCTURAL ART QA ONLY — NOT FULL GAMEPLAY VALIDATION`.
- The existing LF06-006 editor remains the source of the memory-only DIRTY working grid.
- The Studio transport is fixed to the committed launcher operation and fixed request path.
- Python fail-closed reads the immutable source bundle through canonical `read_bundle()`.
- Source candidate ID, dimensions, source cells, canonical grid hash and retained source artwork SHA-256 are cross-bound before evaluation.
- The exact quality policy recorded in `metadata.quality.report.policy` is reconstructed through canonical `QualityPolicy(**policy_data)` and canonicalized back through `policy.as_dict()`.
- The recorded source quality report is recomputed with canonical `evaluate_grid()` and must match before the edited working grid is evaluated.
- The edited working grid is evaluated with canonical `evaluate_grid()` and hashed with canonical `logical_grid_hash()`.
- Source `artwork.png`, `artwork.json`, and `metadata.json` are byte/hash checked before and after revalidation.
- Revalidation does not clear the editor DIRTY state or write a durable edited candidate.
- Solver, measured difficulty, unified validation and owner acceptance limitations are explicitly presented.
- The committed Python test independently proves source-policy reuse and canonical quality/hash parity.
- The committed Godot integration executes a real Generate -> editor edit -> Python revalidation boundary and also exercises a real canonical structural REJECT path.

Builder-reported final verification is `722 passed, 1 warning`, compileall PASS, Godot headless boot PASS, `git diff --check` PASS, and root `TASKS.md` unchanged. These command claims were not rerun by this independent audit; committed source, tests, changed-file scope and commit topology were inspected independently.

## MAJOR finding

### F-LF06-008-001 — STALE results dead-end the manual revalidation workflow

The revalidation lifecycle correctly detects that later edits invalidate a recorded result:

```gdscript
if _result_current and cells != _last_evaluated_cells:
    _state = STALE
    _error_message = "STALE — working artwork changed after the recorded structural result; revalidate again."
```

However `_result_current` remains `true`, and the presentation enables the revalidation button only when state is exactly `AVAILABLE`:

```gdscript
_revalidate_button.disabled = _state != AVAILABLE
```

Therefore after the first valid structural result, any subsequent pixel edit moves the panel to `STALE` and disables the only revalidation control. The operator cannot revalidate the new current DIRTY working grid.

The only tested escape is `reset_to_source()`, which discards the current manual changes. That defeats the central iterative contract of `SB-LF06-008 — Revalidate after manual changes`.

The committed integration suite verifies only:

1. result becomes `STALE` after another edit;
2. stale result is not current;
3. immediately after that, the test resets to source.

It never verifies that the current changed DIRTY grid can be revalidated again while preserving the edits.

This is not a cosmetic UI issue. It breaks the required edit -> revalidate -> edit -> revalidate lifecycle and makes the stated `"revalidate again"` instruction impossible through the actual UI.

## Required remediation

Retain all accepted architecture and change only the stale/re-entry lifecycle.

Required behavior:

1. A later working-grid mutation after a structural result marks the prior evidence `STALE` and not current.
2. The current DIRTY grid remains eligible for a fresh revalidation without Reset and without losing edits.
3. The retained stale result may remain visible as historical/stale evidence, but it must never be presented as current.
4. The Revalidate control must be available for the stale-but-DIRTY current grid, or the lifecycle must deterministically transition from stale evidence to an `AVAILABLE` revalidation state while preserving the stale label/evidence separately.
5. A second real revalidation must replace/bind current evidence to the new exact working-grid hash.
6. Repeating edit -> stale -> revalidate must work more than once.
7. Returning exactly to an earlier grid must not silently resurrect an older result; a new revalidation is required unless identity is explicitly rechecked through the canonical path.
8. Reset to source still yields `NOT_REQUIRED`.

## Required R01 runtime evidence

Extend the committed real Godot integration to prove, without Reset between these steps:

1. first DIRTY edit -> real structural result A;
2. second edit -> `STALE`, result A not current;
3. revalidation control is available for the current DIRTY grid;
4. real second canonical Python revalidation runs;
5. result B is current and its working-grid hash differs from result A when the grid differs;
6. editor remains DIRTY throughout;
7. source bundle bytes remain unchanged;
8. third edit can stale result B and revalidation can run again or otherwise prove the lifecycle is repeatable;
9. only then may Reset return `NOT_REQUIRED`.

Retain the existing deliberate canonical REJECT test.

## Scope constraints

R01 must not:
- redesign the canonical Python revalidation bridge;
- change source-policy semantics;
- enable LF06-003 Validate;
- implement M03/M04/M05;
- add persistence/revision history/promotion;
- edit canonical Python quality semantics;
- start SB-LF06-009+ or SB-LFX work;
- edit root `TASKS.md`.

## Closure decision

`SB-LF06-008` is **not closed**.

The implementation is retained and requires one bounded R01 remediation for stale-result revalidation re-entry.