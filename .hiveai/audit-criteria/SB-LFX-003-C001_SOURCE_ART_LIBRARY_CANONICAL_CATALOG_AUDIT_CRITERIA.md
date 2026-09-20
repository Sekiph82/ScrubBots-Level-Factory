# SB-LFX-003-C001 — Source Art Library Canonical Catalog — Strict Audit Criteria

Document role: INDEPENDENT CHATGPT AUDIT CRITERIA

Target extension:

`SB-LFX-003 — Build searchable Source Art Library/index with immutable source identity, provenance, tags, review state and usage references. [EXTENSION]`

Authoritative product contract:
`docs/product/FACTORY_STUDIO_OWNER_OPERATIONS_EXTENSIONS_V01.md`

## 1. Purpose

Build the first real Factory Studio Source Art Library as an asset catalog over canonical retained source records.

The Library must not become:
- a second source-of-truth database;
- a project/task tracker;
- a review/acceptance system;
- a candidate/level store;
- a training corpus.

For C001, the only fully durable canonical source family already available to the Studio is the accepted `OWNER_UPLOAD` source contract from SB-LFX-002.

Provider/procedural source families must not be fabricated into the Library until equivalent canonical persisted source records exist.

## 2. Truth model

Immutable source authority remains:
- `level_factory/output/owner-uploads/<source_id>/source.png`
- matching canonical `source.json`

Every Library refresh must re-verify:
- source record schema/version;
- source ID;
- OWNER_UPLOAD origin;
- source SHA-256;
- stored byte length;
- stored source bytes;
- immutable source path;
- original dimensions;
- SOURCE_ONLY / UNVALIDATED state.

The Library must never trust a stale index row without re-verifying canonical source truth.

## 3. Allowed mutable catalog metadata

LFX-003 may add a narrowly scoped, source-ID-bound operator metadata sidecar for:
- human label/name;
- tags.

Recommended location:

`level_factory/output/source-library/metadata/<source_id>.json`

This metadata is not source provenance or source identity.

It must:
- bind exact source_id;
- use a versioned schema;
- validate label length/type;
- validate tags as bounded, normalized strings;
- reject duplicate/invalid tags;
- never overwrite source.png or source.json;
- never carry QA/review/solver/difficulty/promotion truth.

No cached copy of source hash/origin/dimensions may become authority.

## 4. Review state / palette facts / usage references

These fields must be present in the Library presentation, but only from real canonical evidence.

Today, if no canonical evidence source is connected:
- owner-review state = `NOT AVAILABLE` with reason;
- derived logical dimensions = `NOT AVAILABLE` pending SB-LFX-004;
- palette facts = `NOT AVAILABLE` pending SB-LFX-004;
- candidate/level usage references = `NOT AVAILABLE` until canonical usage linkage exists.

Do not show:
- `UNREVIEWED` if no real review record exists;
- zero usages as fact if usages are not actually indexed;
- C01..C16 PASS merely because the source is a PNG;
- accepted/ready/production status from source retention alone.

## 5. Search

Provide bounded basic Library search across currently real catalog facts:
- source ID;
- original filename;
- operator label;
- tags;
- origin.

Search results must be derived fresh from the validated source catalog.

Search is not LFX-009 smart collections. Do not implement advanced saved filters, campaign queries or production-readiness views here.

No query may mutate source or metadata.

## 6. Source verification / corruption behavior

A malformed or tampered canonical source must never appear as trusted Library content.

Acceptable behaviors:
- fail the refresh closed with ERROR; or
- surface the source separately as invalid/quarantined while excluding its canonical fields from trusted results.

Under no circumstance may corrupted source bytes/record be silently repaired, rewritten or treated as valid.

A corrupted metadata sidecar may fail that source's catalog metadata closed, but must not corrupt or rewrite source identity.

## 7. UI / navigation

Make the existing `Library` navigation surface real.

At minimum provide:
- refresh;
- basic search box;
- deterministic source list;
- selected source detail;
- source ID;
- origin;
- SHA-256;
- original filename;
- original dimensions;
- SOURCE_ONLY / UNVALIDATED state;
- operator label;
- tags;
- explicit review/palette/derived-dimension/usage availability;
- immutable source location.

Allow editing only label/tags in C001.

Display explicit wording equivalent to:

`ASSET CATALOG ONLY — source art is not training data and Library membership is not owner acceptance.`

## 8. No source mutation / no second index truth

BLOCKER if Library:
- rewrites source.png;
- rewrites source.json;
- changes source ID/provenance;
- silently normalizes/validates/promotes;
- stores a standalone master index whose copied source fields become authoritative;
- reads root TASKS.md as asset data;
- treats Library membership as owner acceptance;
- claims source art is training data;
- introduces provider/network/credential access;
- builder modifies root TASKS.md.

A derived in-memory list is preferred. A persisted metadata directory for label/tags is allowed because it contains operator catalog metadata only.

## 9. Real runtime integration

PASS requires a committed real Godot integration through the actual Factory Studio scene.

Minimum scenario:
1. create/import at least two real OWNER_UPLOAD sources via the accepted canonical path;
2. open real Library surface;
3. refresh and prove both validated source identities appear;
4. verify displayed hash/origin/dimensions/state against canonical source records and bytes;
5. set a label and multiple tags on one source through the real Library -> Gateway -> Python boundary;
6. prove source.png and source.json remain byte-identical;
7. refresh and prove metadata persists and remains bound to the same source ID;
8. search by source ID, filename, label and tag and prove correct filtering;
9. prove owner review / palette facts / derived logical dimensions / usages remain NOT AVAILABLE when no canonical evidence exists;
10. corrupt a bounded test source or source record and prove it is not presented as trusted valid content;
11. prove no candidate/QA/owner-acceptance/promotion mutation is performed;
12. clean bounded source and catalog metadata artifacts.

## 10. Focused static/security guards

Tests must guard:
- no TASKS parsing/import;
- no provider/network/credential code;
- no source.png/source.json writes in Library metadata update path;
- no palette/LEVEL_ART/QA/solver/difficulty invocation;
- source verification is Python-owned and reused by Library scan;
- catalog metadata schema binds source ID;
- tags/label are bounded and deterministic;
- Library search is read-only.

## 11. Severity model

### BLOCKER
Any violation of immutable source authority, provenance, tracker boundary, training-data boundary, or owner-acceptance truth.

### MAJOR
Examples:
- Library lists unverified/tampered source as valid;
- tags/label can change source identity;
- search works from stale copied source facts without re-verification;
- missing review/usage/palette evidence shown as factual values;
- no real Godot Library integration;
- source bytes/record change during metadata edit.

### MINOR
Examples:
- basic search ergonomics rough but truthful;
- metadata editing truthful but limited.

## 12. Retained regressions / publication

Builder records:
- focused SB-LFX-003 tests;
- real Godot Library integration;
- SB-LFX-002 import regression;
- SB-LFX-001 Dashboard regression;
- relevant LF06 regressions;
- full pytest;
- compileall;
- Godot headless boot;
- `git diff --check`;
- `git diff -- TASKS.md` empty;
- exact changed-file review;
- exactly one terminal builder-log-only publication commit.

## 13. Scope limits

Do not implement:
- SB-LFX-004+;
- Import Validation Wizard;
- Candidate Inbox / Review Queue;
- owner acceptance;
- smart collections;
- Production Readiness Card;
- batch import;
- revision history;
- provider integration;
- M03/M04/M05;
- Content Platform;
- main-game work.

## PASS closure rule

`SB-LFX-003` closes only when Factory Studio exposes a real searchable asset catalog over re-verified canonical source truth, permits only bounded label/tag metadata mutation, shows unavailable review/palette/usage domains truthfully, preserves immutable source bytes/provenance, and proves all of this through real runtime integration.
