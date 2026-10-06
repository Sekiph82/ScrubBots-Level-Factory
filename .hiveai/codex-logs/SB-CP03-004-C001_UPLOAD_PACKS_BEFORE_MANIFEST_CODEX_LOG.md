# SB-CP03-004-C001 - Upload Packs Before Active Manifest References Them

Document role: CODEX BUILDER LOG

## Start and inherited M14 synchronization

- Starting timestamp: `2026-10-06T18:59:02+03:00`.
- Canonical repository: `Sekiph82/ScrubBots-Level-Factory`, origin `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- Reused the authorized TEMP worktree `C:\Users\sekip\AppData\Local\Temp\ScrubBots-Level-Factory\M14-CP03-001-012-CPX002-MASTER`.
- CP03-003 final published HEAD/origin/main: `55df7d200ce93c5430bf85e4105aaf6e29df6220`; fetch verified 0/0 and clean before this child.
- Live tracker authorizes M14 master order. Factory Studio icon maintenance is explicitly `QUEUED_AFTER_M14 / DO_NOT_RUN_CONCURRENTLY`.

## Child authority and contracts read

- `.hiveai/prompts/SB-CP03-004-C001_UPLOAD_PACKS_BEFORE_MANIFEST_PROMPT.md` and `.hiveai/audit-criteria/SB-CP03-004-C001_UPLOAD_PACKS_BEFORE_MANIFEST_AUDIT_CRITERIA.md` from current execution HEAD.
- Reuse existing provider protocols/capability negotiation and CP03-003 validated candidate result. Require STAGING object write, integrity verification, and conditional write; upload exact immutable pack bytes in deterministic order; stop on first failure/conflicting digest; exact same bytes may be idempotent only with provider digest proof; do not authorize manifest write until every pack succeeds. No deletes, production target, real SDK, credential, or external network.
- Add deterministic stateful in-memory/local test provider recording order and exact bytes. Implementation decisions and evidence will be appended chronologically.

## Implementation and verification

- Added provider-neutral `staging_pack_upload.py`. It accepts only a publishable frozen CP03-003 candidate, rechecks the strict manifest byte/hash/round-trip and CP02-009 references, negotiates STAGING `OBJECT_WRITE`, `INTEGRITY_VERIFY`, and `CONDITIONAL_WRITE`, then conditionally sends exact immutable pack bytes in canonical pack-ID order.
- Each new write is followed by integrity verification. A conditional conflict is reusable only if verification returns the exact expected digest. Any capability denial, write error, conflicting bytes, malformed provider evidence, or integrity failure stops immediately and returns `manifest_write_authorized=False`; the module has no manifest-write or delete method and cannot target production.
- Added `StagingByteWriter` as the narrow byte boundary over existing provider identity/capability/result contracts; added a stateful in-memory test provider that records call order and stores exact bytes. No real provider SDK, credential, or network operation was introduced.
- Focused command `python -m pytest -q tests/unit/test_sb_cp03_003_candidate_manifest.py tests/unit/test_sb_cp03_004_staging_pack_upload.py`: **10 passed in 0.19s**.
- Prior M14 and M11-M13 regression command `python -m pytest -q tests/unit tests/integration/test_sb_cpx_001_solver_identity_pack.py tests/integration/test_sb_cp03_002_factory_candidate_pack.py`: **1,395 passed, 4 skipped in 291.35s**. Skips explicitly require canonical ScrubBots/Godot capability.
- Required unfiltered `python -m pytest -q`: **1,592 passed, 19 skipped in 945.27s**. Skips are the existing explicit missing canonical ScrubBots/Godot authority cases; no owner Desktop game checkout was used.
- `python -m compileall -q content_pipeline/src src tests` passed; all 16 Content Pipeline JSON files parsed; `git diff --check` exited 0 (only the existing Windows LF-to-CRLF working-copy notice appeared).
- Files changed: `content_pipeline/src/scrubbots_content_pipeline/staging_pack_upload.py`, package exports in `content_pipeline/src/scrubbots_content_pipeline/__init__.py`, and `tests/unit/test_sb_cp03_004_staging_pack_upload.py`. No dependency/license, production/vendor/network, game-repository, tracker, audit, or prompt changes. No test failed during this child.
- The first implementation push was rejected as non-fast-forward because `origin/main` advanced concurrently. `git fetch --prune` showed one upstream commit changing only `TASKS.md` with a new owner-priority roadmap; Current Task remains M14 and SB-CPX-004 is explicitly after M14. No overlap with CP03-004 files. Merged the tracker-only update normally at `77dc7ef4aaa6cee5d45ef9d2924f284cebb71aee`; the rejected push was not retried until after this safe merge.
- Product implementation commit: `ead32e996cc77a5ec27b3fa9ff879e8b535f8d6a`.
- Implementation/log commit SHAs, successful normal push and exact post-push parity will be appended before advancing to CP03-005.
