# SB-LF00-006-C001 — Factory Workspace Exclusions & Secret Boundary
Document role: CODEX BUILDER LOG

## 1. Start and authority

- Exact starting timestamp: `2026-09-15T01:12:14.3246250+03:00` (Europe/Istanbul).
- Canonical repository: `Sekiph82/ScrubBots-Level-Factory`.
- Canonical GitHub URL: `https://github.com/Sekiph82/ScrubBots-Level-Factory`.
- Canonical local mirror used exclusively: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Branch: `main`.
- Remote: `origin https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- Synchronization: fetched `origin/main` and fast-forwarded the clean canonical mirror from `631d59c07f59df39b8f059def0676686f8f30c9b` to `8dd0dcf9bbefc6572175fce8ddbef8e162015a03` using `git merge --ff-only origin/main`. No reset, rebase, force-push, discard, cleanup, or sibling-repository discovery was used.
- Starting HEAD: `8dd0dcf9bbefc6572175fce8ddbef8e162015a03`.
- Starting `origin/main`: `8dd0dcf9bbefc6572175fce8ddbef8e162015a03`.
- Starting divergence: local `main` equals `origin/main`; no ahead/behind divergence.
- Starting worktree: clean before this required builder-log creation.
- Existing stash/worktree state was inspected; only the canonical mirror worktree is being used.

## 2. Required reads before implementation

Read completely before any implementation, test, documentation, or `.gitignore` edit:

- Full authoritative GitHub prompt: `.hiveai/prompts/SB-LF00-006-C001_FACTORY_WORKSPACE_EXCLUSIONS_AND_SECRET_BOUNDARY_PROMPT.md`.
- Current root `TASKS.md`, whose active task is `SB-LF00-006`; root `TASKS.md` is owner-controlled and will not be edited.
- Previous strict PASS audit: `.hiveai/audits/SB-LF00-002-C001_FACTORY_PROJECT_BOUNDARIES_AND_LOCAL_DOCUMENTATION_STRICT_AUDIT.md`.
- `level_factory/README.md`, `level_factory/GOVERNANCE.md`, and `level_factory/docs/DIRECTORY_BOUNDARIES.md`.
- Current root `.gitignore`.
- Root `README.md`, `GOVERNANCE.md`, and `AGENTS.md`.
- `docs/migration/LF_CP_UNIFICATION_POST_CUTOVER_AUDIT_V01.md`.
- Current safe directory structure for `output/`, `review/`, `data/`, `exemplars/`, `docs/`, `level_factory/`, and `.hiveai/`, plus existing cache/log directory names.

The legacy v3 paths `.hiveai/RULES.md`, `.hiveai/PROJECT.json`, `.hiveai/TASKS.md`, and `.hiveai/EVENTS.jsonl` remain absent from the synchronized GitHub `main` branch. They were not recreated or used as current-state authority.

No API key, token, credential, DPAPI store, environment-secret value, or external credential store was read or printed. No main-game repository was accessed.

## 3. Scope and pre-implementation chronology

This builder log was created and verified before any workspace policy document, test, documentation, `.gitignore`, or other product edit. Verification confirmed the exact H1 and document-role lines, a clean log diff, and that the log was the only worktree change at that point. The scope is limited to SB-LF00-006 workspace classification, narrow ignore rules, focused ignore-policy tests, and required verification. SB-LF00-007/008, secret storage/encryption, provider/OAuth/DPAPI work, M01+, gameplay, Factory Studio, Content Platform, and main-game work are out of scope.

No generated owner file will be deleted, relocated, rewritten, or untracked. No provider, cloud service, Magnific, PixelLab, API key, credential, network service, or cleanup operation is authorized or introduced.

## 4. Workspace classification and implementation decisions

- Created `docs/FACTORY_WORKSPACE_AND_EXCLUSIONS.md` as the single repository-wide policy document. Its table classifies tracked source, durable audit/review/reference evidence, generated output, candidate/transient output, cache/temp state, local runtime logs, tracked builder evidence, and local-only secrets with Git treatment and retention boundaries.
- Explicitly protected tracked source/evidence surfaces including `src/`, root `tests/`, `docs/`, `.hiveai/prompts/`, `.hiveai/codex-logs/`, `.hiveai/audits/`, root `TASKS.md`, `level_factory/` source/docs/markers, `review/`, `data/`, and `exemplars/`.
- Explicitly documented that durable `review/` evidence is not generated `output/`; `.hiveai/codex-logs/` is tracked builder evidence while ordinary runtime `logs/` is ignored; `data/` and `exemplars/` are source/evidence rather than disposable caches; `level_factory/output/` is generated/export staging rather than tracker truth; and root `TASKS.md` remains the sole live task ledger.
- Added only the narrow `.gitignore` rules required by the prompt:
  - `level_factory/output/*` with `!level_factory/output/.gitkeep` so generated staging contents are ignored while the intentional marker remains visible;
  - `.env`, `.env.*`, `!.env.example`, `.secrets/`, `secrets/`, `level_factory/.secrets/`, and `level_factory/secrets/` for repository-local secret locations only.
- Preserved the existing root `output/*`/marker convention, Python/cache/build/coverage/WFC/temp/log rules, and `level_factory/.godot/` rule. No broad `review/`, `data/`, `exemplars/`, `.hiveai/`, `docs/`, extension-wide, or arbitrary evidence ignore was added.
- Added `tests/unit/test_sb_lf00_006_workspace_policy.py` using Git's `check-ignore --no-index` semantics for positive and negative representative paths. Tests do not create persistent files or secret fixtures.

## 5. Focused test failures and corrections

- Initial focused command: `python -m pytest -q tests/unit/test_sb_lf00_006_workspace_policy.py` → `1 failed, 6 passed`. The policy correctly used the wording `data/` and `exemplars/` as source/evidence surfaces, while the assertion expected a different paraphrase.
- First correction aligned the assertion wording but still did not account for the policy's Markdown line wrapping; rerun remained `1 failed, 6 passed`.
- Second correction normalized policy whitespace in the assertion; rerun still exposed the final phrase mismatch (`source/evidence surfaces, not disposable caches`).
- Final correction matched the explicit policy sentence. Focused rerun → `7 passed` with the pre-existing pytest cache-permission warning.
- These were test-harness wording corrections only; no policy scope or product behavior changed.

## 6. Ignore and safety evidence

Representative positive `git check-ignore --no-index` evidence confirmed:

- `output/generated/sample.png` and `output/candidates/candidate.json` → root `output/*`;
- `level_factory/output/export.zip` → `level_factory/output/*`;
- `level_factory/.godot/editor/cache` → `level_factory/.godot/`;
- `.venv/`, `__pycache__/`, pytest/mypy/ruff caches, build/dist/coverage, WFC caches, tmp/temp, and runtime log paths → their existing narrow cache rules;
- `.env`, `.env.local`, `.secrets/provider.toml`, `secrets/session.data`, `level_factory/.secrets/local.toml`, and `level_factory/secrets/oauth.data` → the new local-secret-location rules.

Representative negative `git check-ignore --no-index` evidence confirmed these remain visible/not ignored: `output/.gitkeep`, `level_factory/output/.gitkeep`, representative `review/`, `data/`, `exemplars/`, `docs/`, `.hiveai/audits/`, `.hiveai/prompts/`, `.hiveai/codex-logs/`, `level_factory/project.godot`, and root `TASKS.md` paths.

Changed-file-only credential-literal scan found no private-key marker, key-like literal, or assignment-shaped API-key/token/password/secret/credential value. No actual secret, token, key, credential, environment-secret value, DPAPI store, or external credential store was read or created. No generated owner file was deleted, moved, rewritten, or untracked.

## 7. Verification evidence

- Focused SB-LF00-006 suite: `python -m pytest -q tests/unit/test_sb_lf00_006_workspace_policy.py` → `7 passed`.
- Prior SB-LF00-001 suite: `python -m pytest -q tests/unit/test_sb_lf00_001_project_contract.py` → `7 passed`.
- Prior SB-LF00-002 suite: `python -m pytest -q tests/unit/test_sb_lf00_002_project_boundaries.py` → `9 passed`.
- Full regression: `python -m pytest -q` → `589 passed, 1 warning in 161.86s (0:02:41)`. The warning is the pre-existing `.pytest_cache` permission warning from the local environment.
- Compile check: `python -m compileall -q src tests` → success.
- Package import smoke: `python -c "import scrubbots_pixel_factory; print(scrubbots_pixel_factory.__name__)"` → `scrubbots_pixel_factory`.
- Module CLI help smoke: `python -m scrubbots_pixel_factory.cli --help` → success.
- Installed CLI help smoke: `scrubbots-pixel --help` → success.
- Godot smoke: `godot --headless --path level_factory --editor --quit` → success with existing `Godot Engine v4.7.2.stable.official.ed1daf0bf`.
- `git diff --check` → no whitespace errors; Git emitted only the non-failing LF-to-CRLF working-copy warning for `.gitignore`.
- `git diff -- TASKS.md` → empty.

## 8. Files changed and boundaries

Created:

- `.hiveai/codex-logs/SB-LF00-006-C001_FACTORY_WORKSPACE_EXCLUSIONS_AND_SECRET_BOUNDARY_CODEX_LOG.md`.
- `docs/FACTORY_WORKSPACE_AND_EXCLUSIONS.md`.
- `tests/unit/test_sb_lf00_006_workspace_policy.py`.

Changed:

- `.gitignore` — 13 narrow lines: project-local generated-output marker preservation and repository-local secret-location exclusions; no existing durable-source/cache rule was removed.

No root `TASKS.md` builder edit exists. No file in `C:\Users\sekip\Desktop\ScrubBots` was accessed or modified. No provider/network call or credit spend occurred. No dependency, package, or license change was made. The existing root output/batch implementation and all tracked review/data/exemplar/docs/.hiveai evidence remain in place.

## 9. Pre-commit state

At `2026-09-15T01:18:58.5810073+03:00`, local `main` remained at `8dd0dcf9bbefc6572175fce8ddbef8e162015a03`, equal to `origin/main`, with only the listed SB-LF00-006 policy, `.gitignore`, focused-test, and builder-log changes. This log is fully populated through pre-commit verification. Commit and push results will be appended chronologically after the implementation commit.

## 10. Commit and publication

Pending the required non-force commit and push. No audit verdict is asserted here; this is builder evidence for independent ChatGPT strict audit.
