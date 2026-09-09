# RECOVERY-R002 — Publish Existing PAG-M05-C002 Work to GitHub

Document role: CODEX RECOVERY / PUBLICATION PROMPT

Status: AUTHORITATIVE / READY_FOR_EXECUTION
Builder: Codex
Independent auditor / tracker owner: ChatGPT
Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`
Canonical branch: `main`

Target implementation cycle:
`PAG-M05-C002 — Exemplar Contract, Diagnostics & Acceptance Evidence Remediation`

Authoritative C002 prompt:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/PAG-M05-C002_EXEMPLAR_CONTRACT_DIAGNOSTICS_AND_ACCEPTANCE_EVIDENCE_REMEDIATION_PROMPT.md`

Previous independent audit:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M05-C001_WAVE_FUNCTION_COLLAPSE_GENERATOR_STRICT_AUDIT.md`

## 1. Recovery objective

The owner reported that the PAG-M05-C002 Codex run completed, but independent GitHub inspection found:

- no PAG-M05-C002 builder log on GitHub;
- no PAG-M05-C002 implementation commit on GitHub;
- no PAG-M05-C002 branch on GitHub;
- canonical `main` still contains only ChatGPT's C002 activation/control-plane commits after the C001 audit.

This is a publication handoff recovery, not a new implementation cycle and not an audit.

The goal is to publish the **already completed local PAG-M05-C002 work**, if and only if it exists in the designated Level Factory local checkout.

## 2. Authority and local checkout

GitHub remains the sole task/prompt/audit authority.

Repository:
`https://github.com/Sekiph82/ScrubBots-Level-Factory`

Designated local mirror/worktree only:
`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

Do not search sibling folders.

Do not use or modify:
`C:\Users\sekip\Desktop\ScrubBots`

If the designated local folder is not the correct `Sekiph82/ScrubBots-Level-Factory` repository, STOP. Do not discover or substitute another repository.

## 3. First verify local C002 work exists

Before modifying anything, inspect only the designated local checkout and record:

- branch;
- HEAD;
- origin URL;
- `git status --short`;
- `git log --oneline --decorate -20`;
- whether the expected C002 builder log exists locally:
  `.hiveai/codex-logs/PAG-M05-C002_EXEMPLAR_CONTRACT_DIAGNOSTICS_AND_ACCEPTANCE_EVIDENCE_REMEDIATION_CODEX_LOG.md`
- whether local source/test/review/golden files contain C002 remediation changes.

Expected C002 remediation themes:

- production-artifact dimension validation via existing M01 contracts;
- terminal contradiction/rejection diagnostics;
- raw/transformed pattern-count metadata;
- expanded >=12 review pack with exemplar/output paired rendering;
- rectangular and 10-color golden evidence;
- rectangular acceptance coverage.

## 4. Critical fork

### Case A — completed C002 work exists locally

Publish that existing work only.

Do not redesign or add new product behavior.

### Case B — C002 work does not exist locally

Do **not** implement it during this recovery prompt.

Create only the recovery log described below, state that the completed local work could not be found in the authorized checkout, push that log if safely possible, and stop.

ChatGPT will then issue a fresh implementation cycle if required.

## 5. GitHub synchronization rules for Case A

Fetch:

`origin main`

Current GitHub main contains ChatGPT control-plane commits that may not exist in the local builder base.

Preserve both:

- local completed C002 product/test/evidence work;
- current GitHub control-plane/audit/prompt/tracker commits.

Use a non-destructive integration method.

Allowed:

- fetch;
- fast-forward where possible;
- a normal merge/rebase only when it preserves both sides and you can verify the resulting diff;
- a temporary stash solely to preserve pre-existing local changes if necessary, with full logging.

Forbidden:

- `git reset --hard`;
- `git clean -fd`;
- blanket `git restore .`;
- force push;
- deleting ChatGPT control-plane commits;
- overwriting current GitHub `tasks.md`, `.hiveai/HANDOFF.md`, `.hiveai/CYCLE_INDEX.md`, `.hiveai/STATE.json`, `.hiveai/EVENTS.jsonl`, or audits with stale local versions.

## 6. Builder log requirement

The expected C002 builder log is:

`.hiveai/codex-logs/PAG-M05-C002_EXEMPLAR_CONTRACT_DIAGNOSTICS_AND_ACCEPTANCE_EVIDENCE_REMEDIATION_CODEX_LOG.md`

If it already exists locally from the completed run, preserve its historical content.

Append a clearly separated publication-recovery section containing:

- GitHub authority URL;
- RECOVERY-R002 prompt URL;
- local starting branch/HEAD/status;
- local C002 evidence found;
- fetch/synchronization commands;
- conflicts if any and exact resolutions;
- final staged file list;
- implementation commit SHA(s) if already present locally;
- any new publication/merge commit SHA;
- push result;
- final `HEAD == origin/main` verification.

Do not rewrite the historical builder log to pretend it was created at a different time.

If no C002 builder log exists locally, do not fabricate a historical implementation log. Follow Case B.

## 7. Recovery log

Always create:

`.hiveai/codex-logs/RECOVERY-R002_PUBLISH_EXISTING_PAG-M05-C002_WORK_TO_GITHUB_CODEX_LOG.md`

Exact H1:

`# RECOVERY-R002 — Publish Existing PAG-M05-C002 Work to GitHub`

Immediately below:

`Document role: CODEX RECOVERY LOG`

Record:

- whether Case A or Case B occurred;
- local repository identity;
- local initial HEAD/status;
- whether C002 implementation/log existed;
- exact Git commands;
- exact files/commits published;
- GitHub push result;
- final remote HEAD;
- any retained stash and why.

## 8. Publication scope

For Case A, publication may include only files genuinely belonging to the completed C002 builder run, such as:

- WFC source files changed by C002;
- M05 tests;
- M05 goldens;
- M05 review builder/manifest/contact sheet;
- M05 benchmark/docs as changed by C002;
- exemplar documentation corrections;
- matching C002 builder log;
- RECOVERY-R002 recovery log.

Do not stage stale ChatGPT-owned tracker/audit/control-plane files from local state.

Do not begin M06+.

## 9. Validation before push

For Case A, before push:

1. inspect staged diff;
2. prove no M06+ product files;
3. prove no main ScrubBots files;
4. prove no stale overwrite of ChatGPT-owned acceptance state;
5. run `git diff --check`;
6. if existing C002 builder log already records final tests, do not rerun product development merely for this recovery;
7. if synchronization creates a merge conflict touching product files, resolve only by preserving the completed C002 work plus current GitHub governance state.

## 10. Push and stop

Push to canonical:

`origin/main`

Then verify:

- local HEAD;
- `origin/main`;
- GitHub main;

are the same commit.

Do not audit.

Do not modify task acceptance state.

Do not start M06.

Stop after the publication/recovery logs and existing C002 work are safely published.

## 11. Exit criteria

Recovery succeeds only if either:

### Case A
- completed C002 work was found locally;
- it was safely integrated with current GitHub main;
- expected C002 builder log is on GitHub;
- RECOVERY-R002 log is on GitHub;
- product/evidence files are on GitHub;
- no stale tracker/audit overwrite occurred;
- no M06+ scope exists;
- remote main contains the publication.

### Case B
- authorized local checkout was inspected;
- completed C002 work was not found;
- RECOVERY-R002 log truthfully records that fact;
- no product implementation was invented;
- recovery log is pushed if safely possible;
- Codex stops.

ChatGPT will independently inspect GitHub after the owner reports the recovery log has arrived.
