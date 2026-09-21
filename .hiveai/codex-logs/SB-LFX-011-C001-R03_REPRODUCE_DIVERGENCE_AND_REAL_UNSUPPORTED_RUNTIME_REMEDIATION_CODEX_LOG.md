# SB-LFX-011-C001-R03 — Reproduce Divergence + Real Unsupported Runtime Remediation

Document role: CODEX BUILDER LOG

## Chronology

- 2026-09-21 Europe/Istanbul: Started from the canonical `main` mirror after a non-destructive fast-forward to `7eb161b6a080b02bff6286d7c04b87eadaa4bfb2`; repository identity, branch, origin, and protected `TASKS.md` boundary verified.
- Read `AGENTS.md`, `GOVERNANCE.md`, root `TASKS.md`, the R03 master prompt and index, the R02 summary, the SB-LFX-011 R02 strict audit, the exact R03 prompt, and retained R02 implementation/log contracts. `TASKS.md` is read-only.
- This log was created before SB-LFX-011 R03 product or integration edits.

## Scope and implementation

Close only the remaining SB-LFX-011 R02 findings: prove draft/preset divergence through the capability-gated Exact Reproduce surface and prove a real durable unsupported/non-replayable record keeps the action disabled with its canonical reason. Retain canonical metadata replay, OWNER_UPLOAD verification, tamper fail-closed behavior, and source/bundle immutability.

## Verification ledger

- Added a real Godot R03 surface integration that generates a canonical candidate, changes the live Studio draft to different dimensions/seed/mode/label, invokes `FactoryStudioReproduce.exact_reproduce()`, and checks MATCH plus unchanged source bundle bytes.
- Added a real strict OWNER_UPLOAD fixture through the canonical importer and exercised it through the same reproduce surface; the rendered capability is `SOURCE_RETRIEVABLE_ONLY`, Exact Reproduce remains disabled, and the reason states that source retrieval is not deterministic regeneration.
- The first focused run failed because the test selected `AUTO` while asserting `WFC`; corrected the fixture to select the canonical `WFC` option. No product authority or accepted contract was changed.
- Focused Python/Godot gate passed: `python -m pytest -q tests/unit/test_sb_lfx_011_r03_reproduce.py` — `1 passed, 1 warning`; `godot_console.exe --headless --path level_factory --script res://tests/factory_studio_exact_reproduce_r03_integration_suite.gd` — `SB-LFX-011-C001-R03 EXACT REPRODUCE divergence integration PASS`.
- Files changed: this R03 builder log, `level_factory/tests/factory_studio_exact_reproduce_r03_integration_suite.gd`, and `tests/unit/test_sb_lfx_011_r03_reproduce.py`. `TASKS.md` was not modified.
- Retained SB-LFX-011 gates passed after folding the R03 assertions into the allowlisted R01 integration surface: `SB-LFX-011-C001 EXACT REPRODUCE integration PASS`; `14 passed, 1 warning` across the retained boundary/reproduce unit gates; `git diff --check` passed.
- The initial full-suite closure run completed `760 passed, 1 failed, 2 warnings`. The sole failure was the protected project-boundary allowlist because the temporary new R03 suite was not an allowlisted project script. The suite was removed and its real surface assertions were folded into the existing allowlisted integration suite; the boundary and retained focused rerun then passed. This was a test-harness correction, not a product or tracker change.
- `python -m compileall -q src` passed; headless Godot editor boot passed with `BOOT_EXIT=0`; `TASKS.md` diff length was zero. The full-suite result remains truthfully recorded as `760 passed, 1 failed, 2 warnings` for this task closure run, with the sole failure corrected afterward through the focused boundary gate.
- Implementation publication SHAs: `63dcade91c8ee3bdd1e1e2f08d764eda1cb626c6` (initial R03 proof) and `add67f37915dd97d1f0f497e0a6f3bb5236ee552` (folded real surface path). Both were pushed to `main`; final local HEAD and `origin/main` were equal at `add67f37915dd97d1f0f497e0a6f3bb5236ee552`.
- Final tracked diff before log publication contained only the pending builder log; generated `.uid` files were pre-existing untracked owner work and were not staged. `TASKS.md` was not modified.
- The required terminal log-only commit and SHA are recorded after this log is finalized and pushed.
