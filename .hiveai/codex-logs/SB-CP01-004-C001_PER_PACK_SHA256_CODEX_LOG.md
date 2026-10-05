# SB-CP01-004-C001 — Per-Pack SHA-256

Document role: CODEX BUILDER LOG

## Starting record

- Starting timestamp: 2026-10-05 10:21:01 +03:00 (Europe/Istanbul).
- Canonical persistent root verified: C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator; repository Sekiph82/ScrubBots-Level-Factory, branch main, origin https://github.com/Sekiph82/ScrubBots-Level-Factory.git.
- The canonical Desktop checkout remains owner-dirty and behind; it is not modified. Fetch/prune confirmed origin/main at 155aab9bc9b89c3cc65ea0f23c74fa8858193eb9; Desktop main remains 0 ahead / 157 behind after fetch. Existing stashes/worktrees were inspected and left intact, including the unrelated prunable worktree.
- Active M12 authority in live origin/main:TASKS.md still authorizes SB-CP01-001 through 010 then SB-CPX-001 in order.
- Reused the one authorized master worktree, clean at 155aab9bc9b89c3cc65ea0f23c74fa8858193eb9, equal to origin/main, 0/0.
- Read the exact Child 4 implementation prompt and audit criteria from this HEAD before implementation. Child 3 master record is published.

## Contract set read

- .hiveai/prompts/SB-CP01-004-C001_PER_PACK_SHA256_PROMPT.md and .hiveai/audit-criteria/SB-CP01-004-C001_PER_PACK_SHA256_AUDIT_CRITERIA.md.
- M12 master prompt, Child 1 manifest/spec, Child 2 builder, Child 3 pack identity/time/levels, and M11/CP00 payload-validation contracts.

## Implementation and verification

Child 4 will compute SHA-256 over the exact completed .scrubpack byte sequence outside the archive, retain per-member SHA-256 identities in pack.json, and bind immutable receipt evidence to pack ID/version and exact bytes. Focused tests, full required regression gates, failures/corrections, changed files, commits, and push parity will be appended chronologically.

### Implementation and verification results

- Implementation commit: `0a59b432325e8963925e2117fdaed6ec85bad1d8` (`Bind scrubpack archive and payload digests`). Seven files changed: schema, public package exports, pack builder, manifest model, specification, and two Child 1/2 unit test files.
- `pack.json` now requires lowercase 64-hex SHA-256 for each exact level-data, supply-plan, and metadata member. Manifest construction validates complete exact-path coverage and freezes the digest mapping. Strict parsing rejects missing or malformed digest maps.
- Frozen external build evidence carries exact final archive SHA-256 and byte length with pack ID/version/time. The pack digest is not in the archive. `verify_scrubpack_build()` verifies exact archive bytes, member digests, manifest/receipt identity, and evidence payload identity; tests cover byte tampering, payload tampering with a recomputed outer digest, forged identity, and forged member evidence.
- Initial focused run: `1 failed, 55 passed`; duplicate level IDs escaped as `ScrubpackSpecError` after digest collection was moved after payload validation. Wrapped it back into `ScrubpackBuildError`; focused rerun passed `56 passed` (0.61s). A further focused run after tamper-hardening passed `56 passed` (0.53s).
- Initial cumulative CP00/M12 run failed only CP010's clean-source guard while the implementation was still uncommitted (`218 passed, 1 failed`). Initial governance pair likewise failed that same guard (`12 passed, 1 failed`). Committed source first; cumulative then passed `219 passed` (1.24s), governance pair passed `13 passed` (0.50s).
- Required full regression: `python -m pytest -q` -> `1388 passed, 3 skipped in 1046.06s (0:17:26)`. Skips were the opt-in slow pipeline test and two canonical-game-capability-gated tests.
- `python -m compileall -q src content_pipeline/src tests`, manifest JSON parse via `python -m json.tool`, and `git diff --check` passed.
- No dependency/license change, provider/runtime network integration, credentials, production game-source edits, `TASKS.md` edits, or audit edits. The full-suite verifier's clone and Godot run used its pytest temporary workspace only.
- Failures were retained above; the source commit was made before rerunning the CP010 clean-source guard. Implementation publication is pending.
- Implementation publication: pre-push fetch showed `1/0`; normal `git push origin HEAD:main` succeeded. Post-push fetch confirmed local HEAD == origin/main == `0a59b432325e8963925e2117fdaed6ec85bad1d8`, `0/0`.
