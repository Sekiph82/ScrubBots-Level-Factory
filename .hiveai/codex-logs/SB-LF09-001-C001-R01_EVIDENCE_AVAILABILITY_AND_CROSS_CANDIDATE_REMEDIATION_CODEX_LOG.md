# SB-LF09-001-C001-R01 — Evidence Availability and Cross-Candidate Identity Remediation
Document role: CODEX BUILDER LOG

## Starting record

- Starting timestamp: 2026-09-27 Europe/Istanbul.
- Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`.
- Canonical owner mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Canonical owner mirror is dirty and 36 commits behind fetched `origin/main`; it is preserved and will not be reset, cleaned, stashed, rebased, overwritten, or synchronized in place.
- Safe isolated-worktree procedure: use the existing same-repository temporary worktree `C:\Users\sekip\AppData\Local\Temp\ScrubBots-Level-Factory\SB-LF09-001-C001-20260927` at live `origin/main`.
- Isolated branch state: detached `HEAD` at `672c0340823b1eb25631f921be26c938908812bf`, with fetched `origin/main` at the same SHA.
- Required actor/task authorization: live `origin/main:TASKS.md` authorizes only `SB-LF09-001-C001-R01`; status is `CHANGES_REQUIRED / M09-001_R01_REMEDIATION_AUTHORIZED`; Required Actor is `CODEX`.

## Authority and contracts read

- `AGENTS.md`, `README.md`, and `GOVERNANCE.md` from live `origin/main`.
- Root `TASKS.md` from live `origin/main`; it remains read-only.
- Authoritative prompt: `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/672c0340823b1eb25631f921be26c938908812bf/.hiveai/prompts/SB-LF09-001-C001-R01_EVIDENCE_AVAILABILITY_AND_CROSS_CANDIDATE_REMEDIATION_PROMPT.md`.
- Audit criteria: `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/672c0340823b1eb25631f921be26c938908812bf/.hiveai/audit-criteria/SB-LF09-001-C001-R01_EVIDENCE_AVAILABILITY_AND_CROSS_CANDIDATE_AUDIT_CRITERIA.md`.
- Previous independent audit: `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/672c0340823b1eb25631f921be26c938908812bf/.hiveai/audits/SB-LF09-001-C001_STRICT_AUDIT.md`.
- Accepted experimental-selection prompt/criteria and previous M08 strict re-audit summary from live `origin/main`.
- Existing `m08_batch.verify_artifact_set()` contract and `CandidateEvidence` lineage contract.

## Authorized scope

Remediate only unavailable/stale artifact evidence and complete cross-candidate artifact identity policy for `SB-LF09-001-C001`. Preserve accepted M00-M08 evidence, `TASKS.md`, `.hiveai/audits/**`, deterministic bounded offline selection, exact opt-in isolation, source-art immutability, M03/M04/M05/M07 gates, and no production promotion. Implementation and log publication commits will remain separate. Builder evidence is not independent acceptance.

Further entries will be appended chronologically as implementation, verification, and publication occur.

## Chronological implementation and verification

- A first patch attempt used an incorrect isolated-worktree path and was rejected before any file changed; the path was corrected and the authorized patch was then applied.
- Implementation files changed: `src/scrubbots_pixel_factory/evolutionary_selection.py`, package exports in `src/scrubbots_pixel_factory/__init__.py`, and `tests/unit/test_sb_lf09_001_evolutionary_selection.py`.
- The selector now requires the canonical M08 `verify_artifact_set()` byte/reference boundary before ranking. Missing or stale bytes return `UNAVAILABLE`; invalid lineage remains `INVALID_INPUT`; no selection or ranking occurs before verification.
- The versioned policy is `EVOLUTIONARY_SELECTION_V2` with `ALL_REQUIRED_ARTIFACT_IDENTITIES_CANDIDATE_SPECIFIC_V1`. All required artifact reference/digest pairs are explicitly candidate-specific; collisions are rejected across candidate IDs, references, and digests. Verified artifact-set digests are included in the immutable selection input/provenance binding.
- Deterministic replay, finite budgets, explicit opt-in, source-art immutability, accepted M03/M04/M05/M07 evidence boundaries, and production/publication isolation remain unchanged. No shared-identity exception was introduced.
- Initial R01 focused command: `python -m pytest -q tests/unit/test_sb_lf09_001_evolutionary_selection.py`; result `2 failed, 19 passed in 3.91s`. The failures were test assertion wording for two identities already rejected by existing bundle/generation duplicate guards, not a product failure. The assertions were corrected without weakening the contract.
- Corrected focused R01 command: `python -m pytest -q tests/unit/test_sb_lf09_001_evolutionary_selection.py` -> `21 passed in 0.31s`.
- Focused additions cover missing artifact bytes, stale digest/reference bytes, every required artifact reference/digest collision, explicit policy version/field declaration, and verified-artifact provenance.
- Retained M08/M07 command: `python -m pytest -q tests/unit/test_m08_batch.py tests/unit/test_m08_output.py <explicit test_sb_lf07_*.py files>` -> `85 passed in 3.83s`.
- Compile gate: `python -m compileall -q src tests` -> `PASS`.
- Godot gate: `godot_console.exe --headless --editor --path . --quit` -> `PASS`, Godot `4.7.2.stable.official.ed1daf0bf`, exit `0`.
- Full suite: `python -m pytest -q` -> `1086 passed, 2 skipped in 532.54s (0:08:52)`. The truthful pre-existing skips were `test_sb_lf03_002_compact_solver_state.py` and `test_sb_lf04_012_regression.py` because the canonical ScrubBots checkout capability was not supplied; no bridge was exercised.
- Hygiene/protected checks: `git diff --check`, `git diff --exit-code -- TASKS.md`, `git diff --exit-code -- .hiveai/audits`, and the active prompt diff check -> `PASS`.
- Offline/security review: only standard-library Python hashing, JSON, dataclasses, enums, and M08 verification were used. No dependency, license, network, provider, telemetry, API-key, runtime HTTP, cloud image-generation, production-router, or publication integration was added.

## Publication record

- Implementation commit: `483eb5e2b0f348e167e3b4396cbff40ccc38e3c1` (`Close evolutionary selection evidence boundary`).
- Implementation commit contained only the three authorized implementation/test paths; this log was kept separate.
- Implementation publication URL: `https://github.com/Sekiph82/ScrubBots-Level-Factory/commit/483eb5e2b0f348e167e3b4396cbff40ccc38e3c1`.
- Push command: `git push origin HEAD:main`; result `672c034..483eb5e HEAD -> main`, non-forceful fast-forward succeeded.
- Post-implementation fetch verification: isolated local HEAD `483eb5e2b0f348e167e3b4396cbff40ccc38e3c1` equals fetched `origin/main`.

## Final handoff

- The owner mirror remains untouched and dirty/behind as recorded at start; no owner files, stashes, or sibling repositories were used or altered.
- The isolated worktree contains the published implementation plus this new matching log only; `TASKS.md`, `.hiveai/audits/**`, prompts, and accepted M00-M08 evidence remain unchanged.
- Separate log-publication commit and post-push SHA verification remain to be recorded.
- Status: `AWAITING_CHATGPT_AUDIT`.
