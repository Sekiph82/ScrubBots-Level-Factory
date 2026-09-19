# SB-LF06-011-C001 — Factory Studio Exact Reproduce by Recorded Seed / Config — Strict Audit

Document role: CHATGPT INDEPENDENT STRICT AUDIT

## VERDICT

**PASS / CLOSED**

Severity:
- BLOCKER: 0
- MAJOR: 0
- MINOR: 0
- NOTE: 1

Target requirement:
`SB-LF06-011 — Reproduce candidate by seed/config. [PARTIAL]`

## Audited publication chain

- Starting authoritative tracker HEAD: `5da14aee8756c2706cca7af2c94a69d315d3ac2c`
- Builder implementation: `fa0046fd69d2166e4e6d124cd1eec4d06f698f9a`
- Terminal builder publication: `fc7e187fc12e594556c36a28edb66172ad187a78`
- Terminal publication is log-only.

## Acceptance findings

### 1. Reproduce source authority — PASS

Factory Studio does not reconstruct reproduction input from current draft controls. The accepted gateway invokes canonical Python with only:
- launcher;
- `reproduce`;
- retained successful `metadata.json` path;
- governed output path.

Draft seed/difficulty/dimensions/mode/candidate-presentation fields and manual-editor working pixels do not cross the Reproduce process boundary.

### 2. Pre-source availability — PASS

The real Godot integration proves Reproduce is disabled/UNAVAILABLE before a successful canonical Generate establishes a retained metadata source.

### 3. Recorded source A reproduction — PASS

The runtime suite:
- generates deterministic rectangular candidate A;
- records canonical typed seed, difficulty, dimensions, mode and full `metadata.generation.request`;
- changes current draft values without Generate;
- invokes Studio Reproduce;
- requires action=Reproduce, SUCCESS, disposition=MATCH;
- requires candidate ID, grid hash, selected typed seed, mode and dimensions to match A;
- requires reproduced `metadata.generation.request` to equal A exactly;
- compares canonical artifact bytes for metadata/artwork JSON/PNG and preview when present;
- proves source A bytes remain unchanged;
- proves presentation labels do not become canonical identity/input.

### 4. Latest Generate source transition A -> B — PASS

After a distinct successful Generate B:
- the gateway retained metadata source moves to B;
- later draft-only changes do not redirect that source;
- Reproduce returns exact B MATCH rather than A or draft-derived output;
- recorded B request and canonical artifact bytes reproduce exactly.

### 5. Unavailable-action retention — PASS

A dependency-gated Validate attempt remains UNAVAILABLE, does not redirect the retained B metadata source, and a subsequent Reproduce still returns exact B MATCH.

### 6. Canonical Python authority / fail-closed behavior — PASS

No second request parser, generator or reproduction compiler was added to GDScript. Canonical Python remains responsible for:
- recorded request reconstruction;
- typed seed semantics;
- router regeneration;
- grid/hash match;
- recorded quality-policy/report replay;
- canonical bundle rebuild;
- byte-level MATCH decision.

Existing mismatch/fail-closed CLI behavior remains untouched.

### 7. Scope and governance — PASS

Implementation changes are limited to:
- new LF06-011 real Godot integration runner;
- new focused Python regression test;
- one project-boundary allowlist entry for that runner;
- behavior-preserving loader spelling normalization in the retained LF06-010 runner;
- builder log.

No root `TASKS.md`, canonical Python Core semantics, Studio product bridge, provider/network/dependency, M03/M04/M05, LF06-012+, SB-LFX, Content Platform or main-game product implementation was changed.

## Builder verification evidence

Builder reports:
- focused LF06-011: 4 passed;
- real committed Godot integration: exit 0 / PASS marker / empty stderr;
- retained focused regression rerun: 21 passed;
- full pytest: **731 passed, 1 warning**;
- compileall: PASS;
- Godot headless boot: exit 0;
- git diff --check: PASS;
- TASKS diff: empty.

These are builder-reported results; the independent audit additionally inspected the committed runtime assertions, gateway Reproduce argv contract, exact implementation diff and terminal publication topology.

## NOTE

The finalized builder log necessarily states that the terminal publication commit will follow; independent commit inspection confirms `fc7e187...` is exactly that single log-only publication commit.

## Closure

`SB-LF06-011` is accepted as **PASS / CLOSED**.

The requirement is satisfied because real Studio runtime evidence proves exact reproduction is governed by retained canonical recorded seed/config metadata, not current draft/manual presentation state, follows the accepted Generate-source transition, preserves source bytes, and reports MATCH only through canonical Python reproduction authority.
