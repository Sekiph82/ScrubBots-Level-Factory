# PAG-M09-C002 — Manifest Integrity, Reproduce Fidelity & Acceptance Evidence Remediation
Document role: CODEX BUILDER LOG

## Start

- Starting timestamp: 2026-09-11T09:23:09.5773439+03:00.
- Canonical repository: `Sekiph82/ScrubBots-Level-Factory`.
- Canonical authority: `https://github.com/Sekiph82/ScrubBots-Level-Factory`.
- Branch: `main`.
- Starting HEAD: `fe1a5e09a271c78e29703976cf78739ba7ccf72b`.
- `origin/main`: `fe1a5e09a271c78e29703976cf78739ba7ccf72b`.
- Starting divergence: `0 0` (ahead/behind).
- Origin: `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- Initial status preserved as pre-existing user dirt:
  - modified `docs/migration/legacy-task-trackers/EVENTS.jsonl`
  - modified `docs/migration/legacy-task-trackers/PROJECT.json`
  - untracked `.hiveai/EVENT_INDEX.json`
  - untracked `.hiveai/HANDOFF.md`
  - untracked `.hiveai/STATE.json`
- Synchronization was non-destructive: origin was fetched, the fast-forward was applied, and the pre-existing worktree dirt was restored. No reset, rebase, force push, clean, or sibling repository was used.

## Authority and scope

- Read directly from GitHub: the authoritative PAG-M09-C002 prompt, the PAG-M09-C001 strict audit, the PAG-M09-C001 builder log, and the root `TASKS.md` tracker.
- Read locally after synchronization: `AGENTS.md`, `GOVERNANCE.md`, `tasks.md`, `.hiveai/CYCLE_INDEX.md`, the M09 CLI implementation and tests, and the accepted M00-M08 interfaces used by the CLI.
- The current GitHub migration does not contain `.hiveai/PROJECT.json`, `.hiveai/RULES.md`, or `.hiveai/EVENTS.jsonl`; the local legacy/control-plane dirt was preserved and is not used as current task authority.
- Scope is limited to PAG-M09-C002 and F-PAG-M09-C001-001 through F-PAG-M09-C001-004. Root `TASKS.md`, task acceptance state, prompts, audits, and prior logs will not be modified.
- The accepted M03-M08 production algorithms remain out of scope.

## Planned work

- Tighten batch manifest validation so recorded history, seeds, statuses, accepted records, bundles, dimensions, paths, counts, and terminal states are semantically fail-closed.
- Reproduce using the exact persisted M08 quality policy and bind the immutable batch environment, including exemplar identities and policy, into batch identity and candidate identity.
- Add the missing focused, corruption, rectangular, quality-policy, cross-process/PYTHONHASHSEED, and full regression evidence required by the authoritative prompt.

## Chronological record

Implementation, commands, tests, corrections, changed files, dependency/security observations, final diff, commit, push, and final `HEAD == origin/main` verification will be appended here as work completes.

## Implementation record

- Preserved the accepted M09 `argparse` command surface and `GeneratorRouter.generate_candidate()` routing. No M03-M08 production algorithm was changed.
- Extended persisted exemplar identities with the complete ordered contract/provenance fields (schema/version, dimensions, provenance, ownership, approval and production difficulty), and included those identities plus the exact canonical `QualityPolicy` in the batch identity digest.
- Added optional local canonical `--quality-policy-json` input for single generation and new batches so non-default policies can be persisted and reproduced without changing the default behavior. Resume never accepts policy overrides.
- Reworked manifest validation to require exact attempt/accepted field sets, typed root/attempt seed derivation from `DeterministicRNG(root_seed).retry_seed(index)`, status-specific field semantics, canonical candidate IDs/paths, one-to-one accepted/attempt correspondence, duplicate ancestry, count/index limits, and terminal-state invariants.
- Added accepted-bundle cross-binding for candidate ID, dimensions, grid hash, canonical request/attempt seed, and persisted quality policy. Resume now deterministically replays every recorded attempt, including generator failures, quality decisions/rejection codes, hashes and duplicate relationships, before continuing.
- Changed reproduction to parse and re-evaluate the exact persisted M08 quality policy/report rather than using the current default policy.
- Added C002 integration coverage for cross-process artifact bytes under different `PYTHONHASHSEED` values, rectangular/autodimension batches, quality-policy persistence/rejection, exemplar-environment identity, semantic manifest corruption, metadata corruption, path traversal, and exact MASK byte reproduction.

### Test checkpoint

- Command: `pytest -q tests/unit/test_m09_cli.py tests/integration/test_m09_cli_integration.py`
- Result: PASS — 36 tests passed (one pre-existing Windows pytest cache permission warning; no test failure).

- Command: `pytest -q tests/unit/test_m08_output.py tests/integration/test_m08_export_integration.py tests/golden/test_m08_export.py tests/unit/test_m09_cli.py tests/integration/test_m09_cli_integration.py tests/integration/test_offline_boundary.py`
- Result: PASS — 62 tests passed (same pre-existing pytest cache permission warning).
- Command: `pytest -q`
- Result: FAILED during collection before test bodies: the standalone Windows `pytest` launcher resolved an unrelated installed `tests` package and reported `ModuleNotFoundError: No module named 'tests.support'` for four M02 modules. The repository contains the tracked `tests/support/__init__.py`; this was not a source failure and no test package was modified.
- Diagnostic correction: `python -c "import tests.support; print(tests.support.__file__)"` resolved the repository package, and `python -m pytest -q tests/unit/test_m02_result.py` passed 32 tests.
- Corrected full command: `python -m pytest -q`
- Result: PASS — 327 tests passed in 3:43.78 (same pre-existing pytest cache permission warning).
- Offline/source-policy check: the focused offline-boundary test passed; no runtime dependency, network API, key, telemetry, or third-party asset was added. `pyproject.toml` continues to declare `dependencies = []`.

### Publication and synchronization

- Implementation commit created: `e5d3c5b951ae4cd95198860a042e955912b6b030` (`Implement M09 C002 manifest integrity remediation`).
- First `git push origin main` was rejected with `fetch first` because GitHub had advanced `origin/main` from `fe1a5e09a271c78e29703976cf78739ba7ccf72b` to `91a3d85e76ee201efa026c8773db89db2770d538` with the owner’s C002 tracker/prompt/audit-authority updates.
- Fetched origin and merged the GitHub tip non-destructively with `git merge --no-edit origin/main`; no reset, rebase, force-push, or discard was used. Merge commit: `a8045f0bafd17460e98058a6b6e3972e8f6ccb31`.
- The pre-existing migration/control-plane worktree dirt remained untouched and unstaged throughout.

### Terminal publication verification

- After publication commit `cd23b5d3d7ec4663e7c2b65e7d2d1630a18ec9f3` was pushed, executed `git fetch origin`, `git rev-parse HEAD`, `git rev-parse origin/main`, and `git rev-list --left-right --count HEAD...origin/main`.
- Observed: local HEAD `cd23b5d3d7ec4663e7c2b65e7d2d1630a18ec9f3` == `origin/main` `cd23b5d3d7ec4663e7c2b65e7d2d1630a18ec9f3`; divergence `0 0`; branch `main`.
- This builder log records implementation evidence only. No audit, acceptance declaration, tracker mutation, M10/M11 work, or main ScrubBots repository access was performed.
