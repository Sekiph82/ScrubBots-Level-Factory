# M18 + CPX-004 R03 — Studio UTC + Production Approval Regression Closure

Document role: CODEX REMEDIATION PROMPT

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Strict audit:
`.hiveai/audits/M18_CPX004_R2_R02_STRICT_REAUDIT_V01.md`

Audit criteria:
`.hiveai/audit-criteria/M18_CPX004_R2_R03_AUDIT_CRITERIA.md`

## FIRST TASK — safe sync

1. Verify canonical persistent root:
   `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
2. Run `git fetch --prune origin`.
3. Read latest `origin/main:TASKS.md`, this prompt, criteria and R02 strict audit.
4. Preserve all owner-local work. Never reset, clean, rebase, auto-stash, restore/discard, overwrite or force.
5. If Desktop is unsafe, use one clean TEMP worktree:
   `%TEMP%\ScrubBots-Level-Factory\M18-R2-CPX004-R03`
   at exact latest `origin/main`.
6. Never edit root `TASKS.md`.
7. Never write `.hiveai/audits/**`.

Builder log:
`.hiveai/codex-logs/M18_CPX004_R2_R03_CODEX_LOG.md`

## R03-1 — fix the real Studio UTC timestamp boundary

Current runtime defect:

`factory_studio_release.gd` uses:

`Time.get_datetime_string_from_system(true, false)`

Godot 4.7 returns `YYYY-MM-DDTHH:MM:SS` without a timezone suffix. The accepted scrubpack contract rejects timezone-less timestamps.

Fix narrowly.

Requirements:

- actual Studio preflight must send a canonical timezone-explicit UTC instant;
- canonical whole-second output must normalize to `YYYY-MM-DDTHH:MM:SSZ`;
- reviewed identity must bind that canonical value;
- publish-to-STAGING must rebuild using exactly that same value;
- Python service must independently validate/normalize the timestamp before pack assembly so malformed/ambiguous callers fail closed;
- reuse the accepted scrubpack timestamp normalization authority rather than inventing a competing format parser where practical;
- do not add a hidden wall-clock read to the pack builder.

Add tests proving:

1. actual Studio-generated UTC boundary includes explicit UTC authority;
2. timezone-less `YYYY-MM-DDTHH:MM:SS` cannot become a reviewed publish identity;
3. canonical `...Z` survives preflight -> reviewed identity -> STAGING rebuild byte-for-byte;
4. an offset-aware timestamp, if accepted by the existing normalizer, is normalized deterministically before review.

## R03-2 — add the missing production approval adversarial regressions

Do not redesign M14 production code unless a test finds a real defect.

Add permanent tests proving:

- missing owner approval rejects;
- same approval shape but wrong manifest SHA rejects before production mutation;
- same approval shape but wrong content_version rejects before production mutation;
- exact manifest SHA + exact content_version approval still reaches the accepted M14 production path;
- STAGING-only handoff remains `AWAITING_OWNER_PRODUCTION_PROMOTION`.

## R03-3 — regression

Run:

- R03 focused timestamp tests;
- production approval focused tests;
- CPX-004 R02 suite;
- R01 ledger/idempotent promotion tests;
- M11-M14 publisher/production regressions;
- governance tests;
- safe full pytest;
- compileall;
- JSON/schema checks;
- `git diff --check`;
- secret scan.

No live R2 mutation is required.
No fabricated Release Pool batch is allowed.
No real production approval is implied.

## Publication

Implementation/test commit separate from builder log.
Normal push only.
Final execution worktree clean and 0/0.

## Final state

If green:

`AWAITING_GPT_M18_CPX004_R03_STRICT_REAUDIT`

Final response:
return only the R03 builder log GitHub URL.
