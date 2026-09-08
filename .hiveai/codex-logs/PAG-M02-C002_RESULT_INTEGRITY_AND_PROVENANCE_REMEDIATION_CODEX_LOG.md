# PAG-M02-C002 — Result Integrity & Provenance Remediation
Document role: CODEX BUILDER LOG

## 2026-09-09T00:10:12+03:00 — Start and authority

- Canonical repository/task authority: `https://github.com/Sekiph82/ScrubBots-Level-Factory`.
- Authoritative remediation prompt fetched directly from GitHub before implementation: `https://raw.githubusercontent.com/Sekiph82/ScrubBots-Level-Factory/main/.hiveai/prompts/PAG-M02-C002_RESULT_INTEGRITY_AND_PROVENANCE_REMEDIATION_PROMPT.md`.
- Previous independent strict audit: `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M02-C001_DETERMINISTIC_GENERATION_CORE_STRICT_AUDIT.md`.
- Prompt SHA-256 in the synchronized checkout: `DD8BA5CA558619C85227F46ABD03A811518083EE6DBAFE1BBCB90035FC1EDF44`.
- Previous-audit SHA-256 in the synchronized checkout: `9B8FA08C86B5137FDA634CEA8B848C4CAF04C208F08A62E0583D0D215CC48DDC`.

## Starting repository evidence

- Canonical root: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Origin: `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- Branch: `main`.
- Starting synchronized HEAD: `726b84ebaca39f0f32f3e970f635ab03e7925f50`.
- `HEAD...origin/main`: `0 0`.
- Initial worktree: pre-existing unstaged modifications in `.hiveai/PROJECT.json` and `.hiveai/STATE.json`; both were preserved byte-for-byte and remain outside this remediation scope.
- A temporary preservation stash (`codex-preserve-preexisting-control-plane-edits-before-M02-C002`) remains so those unrelated local changes are recoverable.
- Synchronization used `git fetch origin main` and `git merge --ff-only origin/main`. The local control-plane edits initially blocked the fast-forward; they were temporarily stashed, the checkout fast-forwarded from `e527489` to `726b84e`, and the exact local files were restored without editing their contents.
- A PowerShell quoting error occurred while applying the stash (`git stash apply --index stash@{0}`); the corrected quoted command was used. No product files were changed by that failed command.

## Mandatory reads

- Read completely from the authorized checkout: `.hiveai/PROJECT.json`, `.hiveai/RULES.md`, `.hiveai/STATE.json`, `.hiveai/HANDOFF.md`, `tasks.md`, `AGENTS.md`, `GOVERNANCE.md`, `.hiveai/PROJECT_DASHBOARD.md`, `.hiveai/CYCLE_INDEX.md`, the C001 implementation prompt, the C001 builder log, the C001 strict audit, `core/request.py`, `core/rng.py`, `core/result.py`, current M02 result/RNG/request/golden/determinism tests, and this C002 prompt.
- The authoritative `origin/main` versions of the migrated PROJECT/STATE control-plane files were also inspected; the local pre-existing versions were not replaced.
- No main `ScrubBots` repository was accessed. No task, tracker, H!veAI state, handoff, cycle index, prompt, audit, or prior builder log was modified.

## Remediation design before source edits

This bounded cycle addresses only audit findings F-PAG-M02-C001-001, -002, and -003. `GenerationResult` will have no public raw-field construction path: validated factories will allocate through a private internal builder that is not externally callable. Provenance validation will receive the request, compare exact stage seeds to `DeterministicRNG(request.seed).stage_seeds()`, and authenticate optional retry-seed mappings with canonical non-negative attempt keys. Empty string will be restored as a valid M01-compatible string seed in both request and RNG while preserving typed serialization and existing non-empty golden vectors. Existing valid request/RNG/golden behavior will remain unchanged.

## 2026-09-09T00:10–00:15+03:00 — Remediation implementation

- `core/request.py`: removed the M02-only empty-string rejection; integer/string distinction and canonical typed serialization remain unchanged for existing seeds.
- `core/rng.py`: removed empty-string rejection so the M01 string seed domain is preserved. Added extended attempt encoding for retry indices beyond the normal 128-bit range while preserving retry 0/1/... vectors. No global randomness or uncontrolled state was introduced.
- `core/result.py`: removed the public custom raw-field `__init__`. `@dataclass(frozen=True, slots=True, init=False)` now exposes no constructor accepting result fields (`inspect.signature(GenerationResult) == ()`; `GenerationResult.__dict__.get('__init__') is None`; raw construction raises `TypeError`). Validated factories use the private `_from_validated_fields` allocator only after validation.
- Provenance validation now authenticates exact five stage seeds against `DeterministicRNG(request.seed).stage_seeds()`, rejects unsupported provenance fields, and validates optional retry mappings against canonical non-negative attempt keys and `retry_seed(attempt)` for the request seed. Present-but-null retry metadata is rejected.
- Added adversarial result tests for direct-constructor bypass, invalid success/failure construction, deep immutability, fake/altered/missing/extra/wrong-seed stage digests, wrong RNG metadata, malformed/wrong-seed/wrong-attempt retry metadata, and canonical failure stability.
- Added empty-string request/RNG/cross-process tests. Existing four golden fixtures and the C001 known RNG vector were not changed.

### Material commands, failures, and corrections

- `git fetch origin main` found eight authoritative commits. Fast-forward was initially blocked by the two pre-existing local control-plane edits; a reversible stash was created, `git merge --ff-only origin/main` advanced `e527489` to `726b84ebaca39f0f32f3e970f635ab03e7925f50`, and both exact local files were restored. The preservation stash remains.
- The first `git stash apply --index stash@{0}` invocation was rejected by PowerShell/Git option parsing (`unknown switch 'e'`); quoting the stash reference corrected the command. The resulting conflict was resolved by restoring the exact stash versions, verified byte-equivalent with `git diff 'stash@{0}' -- .hiveai/PROJECT.json .hiveai/STATE.json`.
- Pre-remediation M02 focused regression after the source change: `39 passed in 0.88s`.
- Final focused remediation command covering result, request/seed, RNG, interface, golden, and cross-process tests:
  `.venv\\Scripts\\python.exe -m pytest tests/unit/test_m02_result.py tests/unit/test_m02_request.py tests/unit/test_m02_rng.py tests/unit/test_m02_interface.py tests/golden/test_m02_golden.py tests/integration/test_m02_determinism.py -q -p no:cacheprovider`
  Result: `53 passed in 1.39s`.
- Final full repository regression:
  `.venv\\Scripts\\python.exe -m pytest -q -p no:cacheprovider`
  Result: `113 passed in 2.30s`.
- Standalone import/empty-seed smoke passed with package `0.1.0`; empty-seed geometry stage digest was `7af4c2b29986ad6cd52a19acc71653b1f0a16a42ae8f0314ee98b03e5fbe05b0`.
- `.venv\\Scripts\\python.exe -m pip check` passed: `No broken requirements found.`
- Production-core static scan checked five modules and found no network imports, global-random imports, shell/subprocess execution, `eval`, `exec`, or `pickle`. Existing offline/source-policy tests passed in the full regression.
- `git diff --check` passed with only normal Git LF-to-CRLF working-copy warnings.
- Construction-reference inspection found no production `GenerationResult(` calls; the sole raw-construction reference is the adversarial test, while production/test-support creation uses `GenerationResult.success(...)` or `GenerationResult.failure(...)`. No `src` paths for `generators`, `output`, or `cli` exist.
- `git diff HEAD -- tests/golden/m02_fixtures.json` was empty; all existing golden hashes remain unchanged.

## Changed-file scope

- `src/scrubbots_pixel_factory/core/request.py`
- `src/scrubbots_pixel_factory/core/rng.py`
- `src/scrubbots_pixel_factory/core/result.py`
- `tests/unit/test_m02_request.py`
- `tests/unit/test_m02_rng.py`
- `tests/unit/test_m02_result.py`
- `tests/integration/test_m02_determinism.py`
- this matching C002 builder log

The pre-existing local `.hiveai/PROJECT.json` and `.hiveai/STATE.json` edits remain uncommitted and untouched. No task/H!veAI acceptance state, handoff, cycle index, prompt, audit, prior log, or main ScrubBots repository was modified.

## 2026-09-09T00:16+03:00 — Remediation publication checkpoint

- Implementation commit: `c15ea0cf1d8954fbfc12d30d3e185dffe82e5c74` (`Remediate generation result integrity`).
- Implementation push succeeded: `726b84e..c15ea0c` to `origin/main`.
- Equality checkpoint before log publication: local `HEAD = c15ea0cf1d8954fbfc12d30d3e185dffe82e5c74`; `origin/main = c15ea0cf1d8954fbfc12d30d3e185dffe82e5c74`; ahead/behind `0 0`.
- Final remediation scope consists of `core/request.py`, `core/rng.py`, `core/result.py`, focused request/RNG/result/integration tests, and this matching builder log. Existing M02 source, interface, probe, golden fixture data, and golden test remain unchanged.
- Final worktree before log publication contains only the two preserved pre-existing local control-plane modifications and this untracked C002 log.

The completed log is being published in one final log commit. Its own terminal commit SHA is intentionally not recorded in the file; ChatGPT/H!veAI will record terminal repository HEAD independently.
