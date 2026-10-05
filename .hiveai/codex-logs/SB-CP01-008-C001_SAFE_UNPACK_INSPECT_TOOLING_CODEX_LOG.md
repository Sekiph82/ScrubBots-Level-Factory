# SB-CP01-008-C001 — Safe Unpack / Inspect Tooling

Document role: CODEX BUILDER LOG

## Starting record

- Starting timestamp: 2026-10-05 11:59:28 +03:00 (Europe/Istanbul).
- Canonical Desktop root: C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator; repository Sekiph82/ScrubBots-Level-Factory, branch main, origin https://github.com/Sekiph82/ScrubBots-Level-Factory.git.
- Required refresh completed: Desktop HEAD 7c6051589d0a95fc785d7f182ccd0d7f8d7013ce, 169 commits behind live origin/main; 123 tracked-status paths and 53 untracked paths, 18 stashes, 69 worktrees inspected. Owner checkout is unchanged. Live task authority retains the M12 master order.
- Reused the single master worktree, clean/0/0 at 7af6017adc13bca611fec7db5422b9ddb6f5186.
- Read Child 8 implementation prompt and criteria from execution HEAD before edits.

## Contract set read

- .hiveai/prompts/SB-CP01-008-C001_SAFE_UNPACK_INSPECT_TOOLING_PROMPT.md and .hiveai/audit-criteria/SB-CP01-008-C001_SAFE_UNPACK_INSPECT_TOOLING_AUDIT_CRITERIA.md.
- M12 master prompt and Children 1-7 container, manifest, digest, ordering, duplicate-ownership, preflight validation contracts; M11 ZIP/payload safety contracts.

## Implementation and verification

Child 8 will add local read-only inspection with human and machine result forms, strict ZIP metadata/member/manifest/digest validation, and optional extraction only after full validation. Extraction will reject traversal and special entries, remain under an explicit destination, and refuse pre-existing outputs without modifying them. No payload will be executed/imported/loaded and no network/provider behavior will be added. Detailed commands, failures/corrections, results, commits and parity will be appended chronologically.

### Implementation and verification results

- Implementation commits: `399e4a2b576eb30f75022606ad83bbc25c35a211` (`Add safe scrubpack inspect and extraction tools`) and `4734932b5c8d9b268a1f4a7e561b97ef1e86243d` (isolate local filesystem operations in the tools subpackage). The change adds inspection module/API exports and CLI flags, schema documentation, README instructions, and tests.
- `inspect_scrubpack()` reports human and machine forms and checks ZIP validity/CRC, regular non-executable stored-entry metadata, size/count bounds, exact canonical member order/paths, single root manifest, strict supported V1 manifest, complete member/hash maps, case/path collisions, and exact member SHA-256. Reports use fixed reason codes and do not expose source paths/payload content.
- `extract_scrubpack()` validates the same immutable archive bytes first, writes only regular allow-listed members into a fresh temporary directory, refuses existing destinations, and publishes the complete tree only after writing finishes. Traversal, symlinks/special entries, compressed/encrypted entries, bad digests, invalid manifests, and destinations with existing content fail closed. CLI supports `--inspect-pack` and `--extract-pack ... --destination ...` in human or JSON output. No payload is imported, executed, or loaded.
- Initial focused inspector run found two defects: malformed ZIP input was reported as an invalid manifest, and Unix symlink metadata with DOS creator flags was accepted. Error handling now distinguishes ZIP from manifest failures and rejects special mode bits regardless of creator system. Focused inspector tests then passed `5 passed` (0.17s); after transactional extraction and result updates, `5 passed` (0.16s) and final `5 passed` (0.19s). Combined Child 1/2/8 focused suite: `67 passed in 0.30s`.
- First cumulative run passed 229 tests and failed the existing top-level-package AST governance check because it flags filesystem calls such as `rename` in every top-level module. The implementation was isolated in `scrubpack_tools/inspection.py` behind the same public API; no governance rule/test was changed. The next cumulative/governance attempt then failed CP010's required clean-source guard while the wrapper/subpackage move was uncommitted (229 passed/1 failed; governance 12 passed/1 failed). Committed the move separately, then cumulative CP00/M11 + prior M12 + Child 8 passed `230 passed in 1.40s`, governance passed `13 passed in 0.53s`.
- Required full regression: `python -m pytest -q` -> `1399 passed, 3 skipped in 1148.42s (0:19:08)`. Skips: opt-in slow test and two canonical-game-capability-gated tests.
- `python -m compileall -q src content_pipeline/src tests`, manifest JSON parse, and `git diff --check` passed.
- No dependencies/licenses, runtime provider/network integration, credentials, production game changes, `TASKS.md`, or audit changes. Full verifier clone/execution remained in pytest temporary storage.
- Initial failures and corrections are retained above. Implementation push is pending.

- Implementation publication: normal git push origin HEAD:main succeeded. Post-push git fetch --prune origin confirmed local HEAD and origin/main both 4734932b5c8d9b268a1f4a7e561b97ef1e86243d, 0 ahead/0 behind. Child log publication follows separately.
