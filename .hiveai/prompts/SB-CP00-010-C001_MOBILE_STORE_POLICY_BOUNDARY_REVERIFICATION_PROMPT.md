# SB-CP00-010-C001 — Mobile / Store Policy Boundary Re-Verification

Document role: CODEX IMPLEMENTATION / POLICY-EVIDENCE PROMPT

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Parent state:
- SB-CP00-001..009 = PASS / CLOSED.
- This is the final open child in M11.
- M20 still owns the final pre-production Apple/Google policy re-verification.

## FIRST OPERATION — mandatory local <-> GitHub synchronization

Before policy research, edits, tests, or builder-log work:

1. Verify the canonical persistent Level Factory root:
   `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
2. Verify repository identity, branch, origin, HEAD, dirty tracked/untracked state, stashes, and registered worktrees.
3. Run `git fetch --prune origin`.
4. Read current GitHub/`origin/main:TASKS.md`; require `SB-CP00-010 / SB-CP00-010-C001` and this exact prompt.
5. Preserve every byte of legitimate owner-local dirty work. Do not reset, clean, auto-stash, rebase, force, restore, overwrite, or discard it.
6. If the persistent checkout cannot be safely fast-forwarded, leave it untouched and create/reuse only:
   `%TEMP%\ScrubBots-Level-Factory\SB-CP00-010-C001`
   from exact latest `origin/main`.
7. Do not create a Desktop sibling clone/worktree.
8. Require the execution worktree clean and 0/0 against `origin/main` before edits.
9. Stop if repository identity, owner-work preservation, or remote overlap is ambiguous.

## Goal

Implement:

`SB-CP00-010 — Re-verify mobile/store-policy boundary before release.`

This task is an architecture/policy boundary re-verification, not legal advice and not store approval.

It must answer:

> Does the current M11 Content Platform architecture remain deliberately constrained to declarative remote content/data, with remote executable code and hidden post-review functionality outside the authorized boundary?

Do not implement runtime downloads, provider uploads, remote storage, credentials, app-store submission, billing, pack publishing, or game-runtime behavior.

## Official-source-only rule

Use current first-party policy sources as authority.

At minimum re-fetch and inspect the current official pages at execution time:

### Google Play

- Device and Network Abuse:
  https://support.google.com/googleplay/android-developer/answer/16559646
- Deceptive Behaviour / Behaviour Transparency:
  https://support.google.com/googleplay/android-developer/answer/17006354
- Current policy archive / current-version context:
  https://support.google.com/googleplay/android-developer/answer/13386702

### Apple

- App Review Guidelines:
  https://developer.apple.com/app-store/review/guidelines/
  Pay particular attention to the current code-download / self-contained-app boundary, including Guideline 2.5.2 and any current relevant exceptions such as 4.7.
- Apple Developer Program License Agreement:
  https://developer.apple.com/support/terms/apple-developer-program-license-agreement/
  Inspect the current executable/interpreted-code provisions and any related functionality-distribution restrictions.

If an official URL moves, use only the replacement on the same official provider domain and record the replacement URL.

Do not use blogs, forum posts, AI summaries, Reddit, StackOverflow, news articles, or third-party policy summaries as acceptance authority.

## Required evidence report

Create:

`docs/security/MOBILE_STORE_POLICY_BOUNDARY_V01.md`

The report must include for every authoritative source:
- platform;
- official page title;
- exact official URL;
- retrieval/check date in UTC;
- relevant current section/guideline identifier;
- concise paraphrase of the rule;
- why it matters to SCRUBBOTS remote content;
- current M11 architecture disposition;
- future milestone/recheck dependency.

Do not paste large copyrighted policy text. Use concise paraphrase and only very short quotes if needed.

## Machine-readable boundary snapshot

Create:

`content_pipeline/policy/mobile_store_policy_boundary_v1.json`

and a matching versioned schema:

`content_pipeline/schemas/v1/mobile-store-policy-boundary.schema.json`

The snapshot must be deterministic and must contain at least:
- schema/version;
- checked_at_utc;
- official sources and exact URLs;
- source section IDs;
- platform;
- boundary rules;
- architecture dispositions;
- explicit final-recheck-required flag;
- M20 ownership reference.

The snapshot must not claim:
- APP_STORE_APPROVED;
- PLAY_APPROVED;
- LEGALLY_COMPLIANT;
- guaranteed acceptance;
- policy certification.

A safe disposition vocabulary should distinguish:
- architecture currently consistent with a declarative-data boundary;
- prohibited/forbidden architecture;
- not-yet-verified future runtime/provider behavior;
- final release recheck required.

Exact enum names are implementation-defined but must be unambiguous.

## Required architecture mapping

Map the accepted M11 surfaces explicitly:

### Allowed architectural intent

- LevelData V1 JSON is declarative data only.
- `scrubbots.level_supply_plan.v1` is declarative data only.
- `scrubbots.level.metadata.v1` is declarative data only.
- payload validation rejects executable/script/plugin/native/module/resource-smuggling surfaces.
- dry-run planning performs no remote mutation.
- provider abstraction has no concrete network provider.
- no publishing credentials live in Git/project data.
- no remote runtime manager exists yet in this repository.

### Explicitly forbidden by the current SCRUBBOTS Content Platform boundary

At minimum:
- remote `.gd`, `.cs`, dex, JAR, native libraries, DLL/SO/dylib, WASM or other executable code;
- downloadable plugins/addons/autoloads;
- remote scenes/resources/shaders used as executable/application-behavior surfaces unless a future owner-approved policy review explicitly establishes a safe declarative exception;
- eval/exec/interpreted code payloads;
- hidden/dormant functionality activated remotely to evade review;
- dynamic feature injection that changes application behavior outside the reviewed app contract;
- review-environment detection/evasion;
- using Apple 4.7-style mini-app/software exceptions as a silent justification for SCRUBBOTS levels.

If current policy wording is stricter than this list, the report must adopt the stricter boundary or mark the architecture BLOCKED.

## Required policy conclusion

The report must use careful language.

It may conclude that the current M11 design is **architecturally consistent with a declarative remote-data boundary** if the official sources support that conclusion.

It must also state that:
- this is not a guarantee of store acceptance;
- store policies can change;
- M15/M16 runtime work and M18 provider work remain separately unverified until implemented;
- M20 `SB-CP09-001` and `SB-CP09-002` must re-fetch then-current Google/Apple policy before production launch;
- any future executable/interpreted-code capability requires explicit new owner authorization and policy/security review.

## Fail-closed outcome

If current official policy appears to prohibit the planned declarative content model itself, or if the policy position is materially ambiguous:
- do not weaken the report to force PASS;
- record `BLOCKED / OWNER_POLICY_REVIEW_REQUIRED`;
- make no product/runtime workaround;
- stop after publishing truthful evidence.

## Mechanical guards

Add focused tests that verify at least:
- report and JSON snapshot exist;
- snapshot validates against its schema;
- all authority URLs are official Apple/Google domains;
- required platforms and source sections are present;
- final release recheck is true;
- M20 ownership is present;
- forbidden definitive approval/certification claims are absent;
- M11 declarative payload families are mapped;
- executable remote code remains forbidden;
- no network/provider/runtime implementation is added by CP010;
- root `TASKS.md` remains sole tracker.

Do not build a web scraper into product code.

Tests may validate committed policy evidence offline.

## Regression

Run:
1. CP010 focused tests.
2. cumulative CP001..010 focused tests.
3. governance/tracker tests.
4. full `python -m pytest -q`.
5. compileall.
6. JSON schema/snapshot parsing.
7. `git diff --check`.

## Builder log

Create before edits:

`.hiveai/codex-logs/SB-CP00-010-C001_MOBILE_STORE_POLICY_BOUNDARY_REVERIFICATION_CODEX_LOG.md`

Record:
- synchronization disposition;
- exact official URLs checked;
- retrieval/check date;
- relevant section IDs;
- architecture conclusion;
- any ambiguity/blocker;
- focused/cumulative/full test results;
- implementation commit;
- builder-log commit;
- final main parity.

Do not edit root `TASKS.md`.
Do not edit `.hiveai/audits/**`.

## Publication

If all gates pass:
- commit policy evidence/schema/tests;
- commit builder log separately;
- fetch/prune;
- normal non-force update to Level Factory `main`;
- fetch again;
- require execution HEAD == `origin/main`, 0/0 divergence, clean execution worktree;
- stop for ChatGPT independent audit.

## Final response

Return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-CP00-010-C001_MOBILE_STORE_POLICY_BOUNDARY_REVERIFICATION_CODEX_LOG.md
