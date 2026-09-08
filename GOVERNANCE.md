# ScrubBots Level Factory Governance

## Purpose

This repository follows an H!veAI-compatible evidence-first development protocol with strict separation between builder and independent auditor.

Canonical task and implementation authority:

`https://github.com/Sekiph82/ScrubBots-Level-Factory`

The owner's Windows folder `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator` is a local mirror/worktree only. It is never a task-discovery authority. A prompt may explicitly require synchronization with GitHub, but Codex must never choose a repository or active cycle by searching local sibling folders.

## Roles

### ChatGPT — planner, tracker owner, independent auditor

ChatGPT owns:

- implementation and remediation prompt authoring,
- independent strict audits,
- acceptance and rejection decisions,
- task checkbox state in `tasks.md`,
- milestone, sprint, and cycle closure state,
- H!veAI handoff and cycle-index state,
- bounded remediation prompt creation,
- final determination of whether work may advance.

### Codex — builder only

Codex owns:

- implementation requested by the active prompt,
- builder-side tests,
- builder-side verification commands,
- detailed chronological implementation logging,
- commits and pushes requested by the active prompt.

Codex does **not** independently audit its own work.

Codex must not:

- declare `AUDIT_PASSED`,
- declare a milestone, sprint, or cycle finally accepted,
- mark tasks complete in `tasks.md`,
- edit `.hiveai/HANDOFF.md`,
- edit `.hiveai/CYCLE_INDEX.md`,
- author or edit files under `.hiveai/audits/`,
- rewrite historical prompt/log/audit files,
- author a strict audit,
- treat its own passing tests as final acceptance evidence.

## Evidence policy

A Codex log is a builder claim/evidence record, not proof.

Statements such as “all tests passed”, “implementation complete”, or “requirements satisfied” must be independently verified by ChatGPT.

ChatGPT audit must inspect repository truth directly and, where tooling permits, independently run or reproduce relevant tests and checks.

A passing builder test suite does not override a direct contract violation.

Missing independent evidence must remain `UNVERIFIED`, not silently promoted to PASS.

## Audit verdicts

Independent audits use exactly one final verdict:

- `PASS`
- `CONDITIONAL`
- `FAIL`

Acceptance criteria use:

- `PASS`
- `PARTIAL`
- `FAIL`
- `UNVERIFIED`

Findings use severity:

- `BLOCKER`
- `MAJOR`
- `MINOR`
- `NOTE`

## Strict audit minimum sections

Every ChatGPT strict audit must include:

1. VERDICT
2. CONTRACT RECOVERY
3. BRANCH / HEAD / DIFF SCOPE
4. ACCEPTANCE CRITERIA MATRIX
5. BUILDER CLAIMS VS REPOSITORY TRUTH
6. FILE / SYMBOL EVIDENCE
7. FOCUSED TEST EVIDENCE
8. REGRESSION EVIDENCE
9. SECURITY / SAFETY / OFFLINE REVIEW
10. ARCHITECTURE CONSISTENCY
11. TRACKER / LOG / DOCUMENTATION TRUTHFULNESS
12. FINAL REPOSITORY STATE
13. OPEN CROSS-MILESTONE FINDINGS
14. DEFECTS BY SEVERITY
15. TECHNICAL DEBT / UPGRADE OPPORTUNITIES
16. UNVERIFIED ITEMS
17. REGRESSION RISK
18. AUDIT CONFIDENCE
19. FINAL VERDICT
20. REQUIRED REMEDIATION

## Remediation

If an audit is not an unconditional PASS, ChatGPT decides whether a bounded remediation cycle is required.

Each remediation finding must specify:

- source cycle and finding ID,
- severity,
- affected file, symbol, or subsystem when known,
- current incorrect behavior,
- required target behavior,
- required changes,
- focused tests,
- regression tests,
- security/offline constraints,
- acceptance criteria,
- prohibited shortcuts.

Do not create vague cleanup prompts.

## Immutable operational records

Paths:

- prompts: `.hiveai/prompts/`
- builder logs: `.hiveai/codex-logs/`
- independent audits: `.hiveai/audits/`

A used record is immutable. Never rewrite history to make a failed run look successful.

## Shared cycle title contract

For one cycle, Prompt, Codex Log, and Strict Audit use the exact same H1 title.

Example:

`# PAG-M00-C001 — Repository Bootstrap & Governance`

Document type is declared immediately below the heading.

Matching filenames:

- `PAG-M00-C001_REPOSITORY_BOOTSTRAP_AND_GOVERNANCE_PROMPT.md`
- `PAG-M00-C001_REPOSITORY_BOOTSTRAP_AND_GOVERNANCE_CODEX_LOG.md`
- `PAG-M00-C001_REPOSITORY_BOOTSTRAP_AND_GOVERNANCE_STRICT_AUDIT.md`

## GitHub authority and local mirror rule

- GitHub repository `Sekiph82/ScrubBots-Level-Factory` is the sole task/prompt/audit authority.
- Every user-facing Codex handoff must include the full GitHub repository URL and full authoritative prompt URL.
- When a previous independent audit exists, the handoff must include its full GitHub URL.
- Codex must read the authoritative prompt from GitHub before acting.
- Local folders must never be searched to infer the active project or task.
- `C:\Users\sekip\Desktop\ScrubBots` is the separate main-game repository and is off-limits unless an authoritative prompt names a narrowly scoped read-only or recovery action.
- `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator` may be synchronized from GitHub only when the authoritative prompt explicitly requests that synchronization.

## Tracker ownership

`tasks.md` is the canonical task ledger.

Only ChatGPT may promote task states or mark sprint/milestone closure.

Codex may describe proposed completion in its log but must not edit task state.

## SCRUBBOTS contract precedence

Owner instructions and current owner-locked contracts in the main `Sekiph82/Scrubbots` repository outrank stale historical references copied into this repository.

Historical audit copies under `reference/audits/` remain read-only evidence.

## Offline invariant

Pixel Art Generator V1 runtime generation must remain offline-only.

No cloud image-generation API, runtime HTTP dependency, API key, telemetry requirement, or network-only generation path may become necessary for core generation.
