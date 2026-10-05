# SB-CP01-001-C001 — Define Versioned .scrubpack Spec

Document role: CODEX BUILDER LOG

## Starting record

- Timestamp: 2026-10-05 08:14 +03:00 (Europe/Istanbul).
- Execution root: `C:\Users\sekip\AppData\Local\Temp\ScrubBots-Level-Factory\M12-CP01-001-010-CPX001-MASTER`.
- Repository/origin: `Sekiph82/ScrubBots-Level-Factory`, `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- Execution HEAD/base: `612958f9a5641cb37d386707f26460aaee2e7cd0`, detached, clean, `0/0` with `origin/main` at child start.
- Persistent Desktop disposition: owner checkout remains untouched; its post-fetch state was `main`, HEAD `7c6051589d0a95fc785d7f182ccd0d7f8d7013ce`, 123 tracked modifications, 53 untracked paths, 18 stashes, and 144 commits behind the fetched `origin/main`.

## Contract set read

- M12 master implementation prompt and master audit wrapper.
- Child prompt `.hiveai/prompts/SB-CP01-001-C001_SCRUBPACK_V1_SPEC_PROMPT.md` and criteria `.hiveai/audit-criteria/SB-CP01-001-C001_SCRUBPACK_V1_SPEC_AUDIT_CRITERIA.md`.
- `TASKS.md`, `AGENTS.md`, `GOVERNANCE.md`, and previous CP00-010 and M11 audits.
- CP003-R01 audit and remediation prompt; existing `content_pipeline/src/scrubbots_content_pipeline/content_boundary.py` and `payload_validation.py`.
- The accepted CP003 boundary uses strict JSON, duplicate/non-finite rejection, bounded input, exact current payload contracts, and app-code/executable-content rejection. M12 will keep pack contents declarative and offline and will not alter provider, runtime, or game behavior.

## Commands and corrections

- `git rev-parse --show-toplevel`, branch/HEAD/origin/status/stash/worktree inspection, and `git fetch --prune origin` completed in the persistent checkout.
- `git worktree add --detach %TEMP%\\ScrubBots-Level-Factory\\M12-CP01-001-010-CPX001-MASTER origin/main` created the authorized execution worktree.
- Initial source inspection assumed CP00 modules were directly under `content_pipeline/`; those `Get-Content` lookups failed because the Python package is under `content_pipeline/src/scrubbots_content_pipeline/`. Follow-up inspection used the correct paths and read the source successfully. An `rg` invocation with PowerShell-style wildcard arguments also reported invalid path syntax; a corrected `rg --files` plus `Select-String` enumerated the intended test files. No product test had run before these corrections.

## Implementation and verification

Implementation, focused and regression test outcomes, changed paths, offline/security/dependency review, commits, pushes, and parity will be appended chronologically. No product source or test file had been changed at log creation.

## Implementation decisions

- Added the V1 ZIP identity, fixed `pack.json` and per-level JSON paths, a closed manifest schema, and a Python model/path-name validator. This child defines the contract only; it adds no ZIP reader/writer or payload execution path.
- Documented regular JSON-only entries and forbidden symlink, executable, resource, script, shader, and native content. Existing CP003 allow-list validation remains the payload authority.
- Added narrow `-text` attributes for the three byte-pinned CP003/CP010 JSON evidence files so Windows checkout conversion cannot change fixture digests. Preserved the existing `tools/scrubbots_canonical_bridge_runner.gd text eol=lf` rule.
- Updated the governance contract test to check the complete Current Sprint descriptor, including its task-range description. This lets the protected live M12 master tracker state be validated without editing `TASKS.md`.

## Commands, failures, and corrections

1. `python -m pytest -q tests/unit/test_sb_cp01_001_scrubpack_spec.py` — **28 passed**.
2. First cumulative command, `python -m pytest -q <tests/unit/test_sb_cp00_*.py> tests/unit/test_sb_cp01_001_scrubpack_spec.py` — **184 passed, 7 failed**. Two pinned CP003 fixture files and the CP010 raw-byte snapshot had CRLF worktree bytes due global `core.autocrlf=true`; the CP010 source-boundary assertion also saw the new uncommitted Child 1 module. Added path-specific `-text` rules and committed the module before rerunning. No fixture blob content was changed.
3. Initial governance command — **12 passed, 1 failed** because its sprint parser discarded the current sprint description and therefore missed the live `SB-CP01-001..010` range. Updated the assertion to inspect the full sprint line; rerun: **13 passed**.
4. The first quiet full-suite attempt was interrupted after prolonged silence without a captured traceback. A verbose rerun completed **866 passed, 2 skipped** before the Windows runner portability test failed: the first `.gitattributes` edit had replaced the existing runner `eol=lf` rule. Restored that exact rule in a corrective implementation commit. The focused regression command initially used the wrong test filename and returned “file or directory not found; no tests ran”; corrected command `python -m pytest -q tests/unit/test_sb_lf04_001_runner_portability.py tests/unit/test_sb_cp01_001_scrubpack_spec.py` passed **29 tests**.
5. `python -m pytest --collect-only -q | Select-Object -Skip 120 -First 30` closed the producer pipe early and emitted `OSError: [Errno 22] Invalid argument`; collection itself was subsequently run successfully as `python -m pytest --collect-only -q` (1,363 collected). This was an inspection-only shell pipeline issue.
6. Final `python -m pytest -q` — **1,360 passed, 3 skipped** in 1,125.64 seconds. Skips: configured slow test; two capability-gated canonical-game bridge tests. The existing Route A integration performed a read-only canonical game clone into pytest temp storage and ran the real verifier; its test passed and asserted protected game files remained byte-identical.
7. `python -m compileall -q src content_pipeline/src tests` — passed. `python -m json.tool content_pipeline/schemas/v1/scrubpack-manifest.schema.json` — passed. `git diff --check` — passed.

## Files changed

- `.gitattributes` — byte-pinned JSON checkout rules, with the pre-existing LF runner rule retained.
- `content_pipeline/schemas/v1/scrubpack-manifest.schema.json`.
- `content_pipeline/src/scrubbots_content_pipeline/scrubpack_spec.py`.
- `docs/content_platform/SCRUBPACK_V1_SPEC.md`.
- `tests/unit/test_sb_cp01_001_scrubpack_spec.py`.
- `tests/unit/test_sb_lf00_007_governance_authority.py` — current sprint description parsing fix.

No dependency or license changes. No audit, prompt, tracker, provider, credential, runtime, or game source was changed. CP00 offline/network-boundary tests passed; one pre-existing integration used read-only network access to test current game authority in an isolated temp copy. No remote provider or game/runtime mutation occurred.

## Implementation commits

- Spec/schema/docs/focused tests: `af03ac8f387e90f5a0260d5d5b62b19c66e83089`.
- Byte-exact Windows checkout attributes: `f20375e3be147302a2ac654916ba66601bd3792d`.
- Preserve existing runner line-ending contract: `72a510738d7d86b6a2f82af80b85a71e434a8531`.
- Governance regression support: `e59e1bf44ee8d216068e834df902bde163e1029c`.

Implementation and builder log will publish as separate commit groups. The child remains builder evidence pending independent audit.


## Publication parity

- Before implementation push, `git fetch --prune origin` showed local HEAD `e59e1bf44ee8d216068e834df902bde163e1029c` at 4 ahead / 0 behind.
- Normal non-force `git push origin HEAD:main` succeeded, advancing `main` from `612958f9a5641cb37d386707f26460aaee2e7cd0` to `e59e1bf44ee8d216068e834df902bde163e1029c`.
- Follow-up `git fetch --prune origin` confirmed local HEAD == `origin/main` == `e59e1bf44ee8d216068e834df902bde163e1029c`, divergence `0/0`. Only the two required, not-yet-committed builder logs remained untracked before the log commit.
- Distinct implementation commits: `af03ac8f387e90f5a0260d5d5b62b19c66e83089`, `f20375e3be147302a2ac654916ba66601bd3792d`, `72a510738d7d86b6a2f82af80b85a71e434a8531`, `e59e1bf44ee8d216068e834df902bde163e1029c`.
- Separate Child 1/master builder-log commit and final parity will be recorded after publication.
