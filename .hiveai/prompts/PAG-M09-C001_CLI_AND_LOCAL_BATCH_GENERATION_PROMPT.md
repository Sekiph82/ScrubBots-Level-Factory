# PAG-M09-C001 — CLI & Local Batch Generation
Document role: CODEX IMPLEMENTATION PROMPT

Status: AUTHORITATIVE / READY_FOR_IMPLEMENTATION
Builder: Codex
Independent auditor / tracker owner: ChatGPT
Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`
Canonical branch: `main`
Canonical current-state tracker: `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/TASKS.md`
Previous closing audit: `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M08-C003_DETERMINISTIC_RICH_PROVENANCE_BINDING_CLOSURE_STRICT_AUDIT.md`

## 1. Mission

Implement only `PAG-M09 — CLI & Local Batch Generation`, covering `PAG-0901` through `PAG-0930`.

M09 turns the accepted M00-M08 engine into a Windows-friendly offline command-line tool for:

1. one candidate generation;
2. exact reproduction from recorded metadata;
3. deterministic finite batch generation with resumable canonical state;
4. batch duplicate detection and human review output.

M09 must orchestrate accepted APIs. It must not redesign M03-M08 generation, quality, provenance, PNG or bundle contracts merely to make CLI behavior convenient.

Do not begin M10 or M11.

## 2. Current authority and tracker migration

The repository tracking contract has migrated. Root `TASKS.md` is the only current project-status tracker. Hidden legacy tracker files under migrated `.hiveai`/legacy locations are historical only and must not be revived as competing current state.

Historical implementation prompts, Codex logs and independent audits under `.hiveai/prompts/`, `.hiveai/codex-logs/` and `.hiveai/audits/` remain valid evidence records.

Codex is builder only. For this cycle:

- do not mark `PAG-0901..PAG-0930` `[x]`;
- do not declare M09 finally accepted;
- do not author an independent audit;
- do not rewrite prior prompts/logs/audits;
- do not modify root `TASKS.md` acceptance/checkbox state. ChatGPT will reconcile the tracker after independent audit.

## 3. GitHub-first start

Before implementation read from GitHub `main`:

1. root `TASKS.md` completely;
2. `AGENTS.md`;
3. `GOVERNANCE.md`;
4. M08 C001/C002/C003 prompts, builder logs and audits as needed to recover the accepted export/reproduce contract;
5. `pyproject.toml`;
6. `src/scrubbots_pixel_factory/core/` request/result/RNG contracts;
7. `src/scrubbots_pixel_factory/generators/router/` including AUTO/HYBRID contracts;
8. `src/scrubbots_pixel_factory/generators/wfc/` exemplar/registry contracts;
9. `src/scrubbots_pixel_factory/quality/`;
10. `src/scrubbots_pixel_factory/output/`;
11. existing relevant tests and fixtures;
12. this M09 prompt.

Authorized local mirror only:
`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

Never use or modify:
`C:\Users\sekip\Desktop\ScrubBots`

Synchronize non-destructively. No hard reset, force push, blanket clean/restore or silent rebase.

## 4. Matching builder log

Before the first M09 source/test/documentation edit create:

`.hiveai/codex-logs/PAG-M09-C001_CLI_AND_LOCAL_BATCH_GENERATION_CODEX_LOG.md`

Exact H1:

`# PAG-M09-C001 — CLI & Local Batch Generation`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record chronologically and truthfully:

- timestamp/repository/branch/origin/starting HEAD;
- GitHub-first authority reads;
- local status and preserved pre-existing changes;
- each implementation step;
- focused failures and corrections;
- exact commands/test counts;
- Windows CLI evidence;
- offline/no-network checks;
- manifest/reproduce/batch evidence;
- dependency/license changes;
- final diff/status;
- implementation commit(s);
- push results;
- completed-log publication;
- post-completed-log `local HEAD == origin/main`, divergence `0 0` checkpoint.

Do not hide failed tests after correcting them.

## 5. CLI package and executable contract

Create a dedicated package such as:

`src/scrubbots_pixel_factory/cli/`

Keep parsing/orchestration separate from generators and output internals. A reasonable split is `main.py` plus small project-owned helpers/models if needed.

Add an installed console entry point in `pyproject.toml`:

`scrubbots-pixel = "scrubbots_pixel_factory.cli.main:main"`

Also support:

`python -m scrubbots_pixel_factory.cli ...`

Use Python standard library CLI facilities, preferably `argparse`. M09 must not add a runtime CLI framework dependency.

The CLI must be Windows-friendly and work from PowerShell. Do not require Bash syntax, shell-specific quoting tricks, Godot, a browser or internet access.

## 6. Stable command surface

Implement these commands:

### 6.1 Single generation

Conceptual UX:

```text
scrubbots-pixel generate \
  --difficulty MEDIUM \
  --width 37 \
  --height 34 \
  --mode RULES \
  --style ORGANIC \
  --seed 849323 \
  --output output
```

Required flags/behavior:

- `--difficulty` required;
- `--width` and `--height` independently optional;
- omitted dimensions use the accepted deterministic M01/M02 resolver;
- `--mode` required and accepts exactly MASK/RULES/WFC/HYBRID/AUTO;
- `--style` and `--theme` optional and passed faithfully into `GenerationRequest`;
- `--seed` optional for single generation;
- `--output` optional with a documented local default that does not pollute source-controlled test fixtures;
- optional explicit candidate ID may be supported, but the default candidate ID must be deterministic, filesystem-safe and stable for the exact request;
- optional generator configuration must use a Windows-friendly local JSON input such as `--options-json PATH`, representing the accepted `{namespace, version, values}` contract. Do not invent a second configuration language.

The CLI must construct the accepted `GenerationRequest`; do not duplicate dimension/palette validation in ad-hoc CLI logic where the existing contract already owns it.

### 6.2 Reproduce

Required UX:

```text
scrubbots-pixel reproduce path\to\candidate\metadata.json
```

Optional output/exemplar flags may follow.

### 6.3 Batch

Conceptual UX:

```text
scrubbots-pixel batch \
  --difficulty EASY \
  --count 100 \
  --mode AUTO \
  --seed 100000 \
  --max-attempts 400 \
  --output output\batch-easy
```

Add a clear resume surface, for example:

```text
scrubbots-pixel batch --resume output\batch-easy\batch-manifest.json
```

Do not make resume depend on mutable defaults or undocumented CLI state.

## 7. Seed contract

### Explicit seed

CLI must preserve seed type deterministically. Define and document one unambiguous parse rule.

Preferred simple rule:

- canonical decimal integer token => integer seed;
- otherwise => string seed.

If a different rule is chosen, it must be explicit, tested and stable.

### Omitted single-generation seed

For `generate` only, when seed is omitted:

- choose a seed locally from OS entropy using a standard-library source such as `secrets`;
- do not use time as the sole seed source;
- print the selected seed before/with the result summary;
- record exactly that same typed seed in the M02 request and M08 metadata;
- tests must monkeypatch/inject the entropy boundary so this behavior is testable without weakening generator determinism.

Uncontrolled entropy must remain at the CLI request-creation boundary. Generator modules must continue using only project deterministic RNG.

For batch, require an explicit root seed unless an omitted-seed design records it once in the new manifest before any attempt. Never choose a fresh hidden seed on resume.

## 8. Generator construction and local exemplar input

MASK and RULES must work using accepted local generators with no exemplar dependency.

WFC and WFC-bearing HYBRID/AUTO configurations require accepted M05 exemplar data. The repository currently has no owner-approved production exemplar catalog that M09 may fabricate.

Provide a narrow offline local exemplar-loading surface, preferably repeatable:

`--exemplar-json PATH`

The loader must:

- read local JSON only;
- construct the existing immutable `Exemplar` contract rather than a parallel model;
- preserve exemplar ID, role, pixels, provenance and ownership fields exactly;
- reject malformed/off-palette/ineligible exemplars through accepted M05 contracts;
- build the existing `ExemplarRegistry`;
- reject duplicate exemplar IDs;
- never download exemplars;
- never silently substitute test artwork or a different exemplar when the requested ID is unavailable.

Synthetic fixture exemplars may be used only in automated tests/evidence. Do not copy them into production data as owner artwork.

For a WFC request without required local exemplar evidence, fail clearly and non-zero.

For AUTO fallback, preserve the accepted AUTO policy. Do not secretly remove WFC/HYBRID from configured candidate order merely because an exemplar is missing. Configuration/exemplar errors must surface according to accepted generator/fallback semantics.

## 9. Single-generation pipeline

The single `generate` command must orchestrate:

1. parse CLI/config/exemplars;
2. construct exact `GenerationRequest`;
3. build `GeneratorRouter` with local WFC registry where supplied;
4. call `generate_candidate()`, not a provenance-losing shortcut, so WFC/HYBRID/AUTO rich metadata can reach M08;
5. distinguish generator failure from successful candidate;
6. run the accepted M07 quality evaluation on the exact logical grid;
7. if quality rejects, return non-zero and print stable rejection codes without mutating the grid;
8. if accepted, publish through accepted M08 `export_candidate()` / bundle API;
9. print concise success summary including candidate ID, typed seed, mode, resolved dimensions, logical-grid hash and output path.

Do not hand-build PNG/metadata files in the CLI.

Do not silently export a rejected candidate as an accepted success.

If exposing an explicit diagnostic option to keep rejected artifacts, it must preserve M08 quality state truth and must not count as CLI success. This is optional and should not expand the cycle unnecessarily.

## 10. Exit-code contract

Define a small documented stable exit-code enum/table.

At minimum distinguish:

- success;
- CLI usage/invalid request/config;
- generation failure;
- quality rejection;
- reproduce mismatch/unsupported metadata;
- batch exhausted before requested accepted count;
- filesystem/output failure if not covered by the invalid/config bucket.

`argparse` may retain its conventional usage-error behavior if documented and tested.

Expected domain failures must not dump an uncontrolled traceback in normal CLI use. Unexpected programmer errors may still fail loudly during development/tests.

Write normal summaries to stdout and errors to stderr consistently.

## 11. Reproduce contract

Implement `PAG-0912..PAG-0916` against the accepted M08 metadata contract.

Input is an existing candidate's `metadata.json`.

Required behavior:

1. parse JSON fail-closed;
2. require supported M08 metadata schema/version;
3. recover the exact embedded canonical M02 request, including typed seed, difficulty, width/height choices, style/theme, palette subset, generator mode and exact versioned generator options;
4. do not substitute current defaults for any historical field that is present/missing contrary to schema;
5. reject unsupported generator/request/output versions clearly;
6. reconstruct required local generator/exemplar environment;
7. regenerate through accepted generator candidate APIs;
8. preserve WFC/HYBRID/AUTO rich provenance requirements;
9. compute the reproduced logical-grid hash using accepted M07/M08 hashing;
10. compare to the original metadata's artwork grid hash;
11. report exact MATCH/MISMATCH and return non-zero on mismatch.

For rich modes whose exact generation depends on exemplar contents not embedded in metadata, require the matching local exemplar through `--exemplar-json` or another explicit local-only registry input. Missing exemplar is a hard reproduce failure, not permission to substitute another source.

Where the accepted metadata records enough identity evidence such as exemplar ID, provenance identity, palette/pattern/stage information, cross-check the supplied local exemplar/candidate through existing M05/M06/M08 contracts before declaring MATCH.

An optional `--output` may publish the reproduced M08 bundle, but only after the grid hash matches. The default reproduce command may be verification-only.

## 12. Reproduce parsing must be strict

Do not implement reproduce by cherry-picking a few convenient metadata keys.

Prefer a small project-owned parser/reconstructor that validates exact key/schema expectations and constructs existing M02 types.

Mandatory negative tests:

- malformed JSON;
- wrong M08 schema/version;
- unsupported request schema version;
- unsupported generator-options version/namespace;
- missing required request field;
- changed typed seed;
- changed generator mode/version;
- changed original grid hash;
- missing required WFC exemplar;
- wrong exemplar ID/content/provenance where reconstructibly detectable;
- successful regeneration whose hash differs from recorded hash.

Do not silently normalize broken historical metadata into a current valid request.

## 13. Deterministic batch orchestration

Implement `PAG-0917..PAG-0927` as a finite deterministic state machine.

Separate these quantities explicitly:

- target accepted count;
- attempts executed;
- successful generated grids;
- quality-rejected generated grids;
- generator failures;
- exact duplicates;
- accepted unique candidates.

`--count` means accepted unique candidates requested, not attempts.

Require a positive explicit `--max-attempts`; choose a documented finite default only if the CLI always persists it into the manifest. Never loop until success without a hard bound.

### Attempt seed derivation

Derive every attempt seed from the batch root seed and attempt index through a project-owned deterministic rule. Reuse `DeterministicRNG` rather than Python global `random` or process hash.

The attempt seed sequence must be independent of acceptance/rejection outcomes. Attempt N must receive the same seed on a clean rerun and on resume.

Record every attempted seed, including failed/rejected/duplicate attempts.

### Dimensions

If width/height are omitted, each attempt uses the accepted `GenerationRequest` resolver from that attempt seed. Do not generate an image at one size and resize it.

## 14. Versioned canonical batch manifest

Create a versioned project-owned batch manifest, for example:

`batch-manifest.json`

Use deterministic canonical JSON. Do not include timestamps, absolute machine-specific paths, random UUIDs or unordered mappings that create meaningless diffs.

At minimum store:

- manifest schema/version;
- batch identity derived deterministically from immutable batch config;
- requested accepted count;
- explicit max attempts;
- root typed seed;
- immutable request template: difficulty, optional width/height, mode, style/theme, palette request, exact generator options;
- exemplar identities/provenance needed to validate resume, without embedding third-party/unapproved artwork unless an accepted upstream contract explicitly allows it;
- next attempt index;
- ordered attempt records;
- each attempt's derived typed seed;
- resolved dimensions when generation reached them;
- generator status/failure code;
- quality decision and ordered rejection codes when a valid grid exists;
- logical-grid hash for successful grids;
- duplicate relation when applicable;
- deterministic candidate ID for accepted entries;
- accepted output relative path/name;
- accepted count;
- terminal state such as IN_PROGRESS / COMPLETE / EXHAUSTED.

Each manifest write must be crash-resistant enough for local use, preferably write-temp + atomic replace in the same directory.

Do not mutate earlier attempt history on resume.

## 15. Resume semantics

`--resume MANIFEST` must:

- validate exact manifest schema/version;
- reconstruct the immutable original batch config;
- resume exactly at recorded `next_attempt_index`;
- derive the same next attempt seed as a clean uninterrupted run;
- preserve prior accepted IDs/hashes/rejections;
- reject attempts to change seed/count/max-attempts/mode/difficulty/dimensions/style/theme/options through additional CLI flags unless an explicit future schema defines such mutation. For V1, immutable means immutable;
- validate required local exemplar identity again;
- stop when accepted count reaches target or max attempts is reached;
- produce byte-identical final manifest and accepted bundles versus an equivalent uninterrupted run, except for filesystem ordering which must not affect serialized bytes.

Re-running `--resume` on an already COMPLETE manifest should verify and exit success without changing bytes.

Re-running an EXHAUSTED manifest should remain exhausted and not secretly extend max attempts.

## 16. Candidate identity and duplicate handling

Candidate IDs must be deterministic and collision-resistant for this local workflow.

Recommended design:

- single generate default ID from canonical request digest, with a stable prefix;
- batch candidate ID from immutable batch identity + attempt index + request/grid digest component.

Do not use Python `hash()`, timestamps or random UUIDs.

Use accepted M07 `logical_grid_hash()`/exact duplicate semantics.

Before accepting a successful quality-passing batch candidate:

- compare exact logical-grid hash against already accepted hashes;
- if hash matches, perform exact logical cell equality before calling it an exact duplicate, preserving collision safety;
- record duplicate rejection/relation deterministically;
- do not mutate the grid to make it different;
- continue with the next pre-derived attempt seed.

No duplicate candidate ID may overwrite another candidate bundle.

## 17. Batch quality and rejection codes

Use accepted M07 quality policy. Define which policy the CLI uses and persist the exact policy/version/data into the batch manifest or otherwise make it reconstructible without current defaults.

For every generated grid record:

- quality accepted/rejected;
- stable ordered rejection codes;
- grid hash;
- no grid mutation.

For generator failures record the stable M02 failure code/reason class without pretending there was a quality result.

Do not collapse generator failure, quality rejection and duplicate rejection into one generic status.

## 18. Batch review report/contact sheet

Implement `PAG-0926` by reusing the accepted M07 review infrastructure where possible.

Produce a deterministic human-readable batch report/contact sheet for successful generated candidates that have logical grids. It must make accepted/rejected/duplicate status understandable and include enough identifiers to trace each image/card back to manifest attempt index/seed/candidate/hash.

Do not build a second incompatible quality engine or resize logical source art.

Contact-sheet scaling is presentation-only nearest-neighbor/integer rendering under accepted M07/M08 rules.

No CDN, telemetry, runtime web service or online asset is allowed.

## 19. Output directory contract

A successful single generation should create one accepted M08 candidate bundle under the requested output directory.

A batch output should have a deterministic, documented structure such as:

```text
batch-output/
  batch-manifest.json
  candidates/
    <candidate-id>/
      artwork.json
      metadata.json
      artwork.png
      artwork.preview.png   # only if explicitly configured
  review/
    ...
```

Exact names may differ if documented, but:

- manifest paths should be relative/portable where stored;
- no absolute owner machine paths in canonical artifacts;
- source repository must not be polluted by generated output during tests;
- identical completed reruns/resume must not create meaningless diffs.

## 20. Determinism and cross-process acceptance tests

Add tests proving at minimum:

1. same explicit single request => same candidate ID and same M08 bundle bytes;
2. omitted single seed is printed and exactly recorded; entropy boundary is controlled in test;
3. auto-dimension request via CLI obeys difficulty bounds and records resolved dimensions;
4. rectangular single CLI generation works;
5. invalid dimension/mode/options fails non-zero without traceback noise;
6. quality rejection returns the documented non-zero code and stable rejection codes;
7. reproduce MATCH for accepted MASK and RULES artifacts;
8. reproduce detects tampered hash/request/version;
9. rich-mode reproduce works with matching local synthetic test exemplar where required and fails without/wrong exemplar;
10. batch accepted count differs from attempt count when deliberate rejects/duplicates occur;
11. every attempted seed is recorded;
12. hard max-attempt exhaustion terminates and returns documented code;
13. exact duplicate is detected without grid mutation;
14. candidate IDs are unique and deterministic;
15. interrupted/resumed batch final manifest and accepted bundle bytes equal uninterrupted run;
16. completed resume is a byte no-op;
17. same batch config/root seed produces identical manifest bytes across separate processes and at least two `PYTHONHASHSEED` settings;
18. different root batch seeds can produce different accepted sets;
19. rectangular batch path works;
20. offline execution works with network calls blocked.

Tests must be reasonably bounded; M10 owns large fuzz/performance/100-candidate owner acceptance.

## 21. Windows acceptance evidence

M09 targets the owner's Windows laptop.

Builder evidence must include PowerShell-compatible installed or module invocation examples for:

- `--help`;
- one successful MASK or RULES `generate` command;
- one invalid command and non-zero exit code;
- `reproduce` MATCH;
- small deterministic `batch`;
- interrupted/resume or equivalent test-driven resume proof.

Do not hardcode `C:\Users\sekip` into production output or tests. Use temporary directories.

## 22. Preserve accepted M00-M08 contracts

Do not weaken:

- C01..C16 and BG01 rules;
- difficulty dimension/color bands;
- one logical pixel = one gameplay cell;
- deterministic `GenerationRequest` and `DeterministicRNG`;
- generator result/failure contracts;
- MASK/RULES/WFC/HYBRID/AUTO accepted behavior;
- M07 grid-only quality and exact duplicate semantics;
- M08 immutable artwork JSON;
- exact logical PNG and optional integer preview;
- M08 rich provenance fail-closed rules;
- rectangular goldens;
- strict PNG corruption handling;
- byte-stable bundles;
- zero runtime dependencies unless an independently justified later cycle explicitly changes that architecture.

M09 may add the console entry point and CLI package. It must not modify generator algorithms to get convenient CLI outputs.

## 23. Offline/security/path safety

CLI input paths are local files only.

Prohibit/avoid:

- HTTP/HTTPS fetches;
- telemetry;
- remote exemplar lookup;
- shelling out to arbitrary commands;
- `eval`/`exec` for config;
- pickle or unsafe deserialization;
- path traversal via candidate/batch IDs;
- overwriting unrelated files outside the requested output root;
- following manifest candidate paths outside the batch root.

Use JSON and existing strict contracts.

Add negative path tests for at least traversal candidate IDs/manifest paths where a new M09 path surface is introduced.

## 24. Required focused verification

At minimum run and log:

- new M09 CLI unit tests;
- single-generation integration tests;
- reproduce integration tests;
- batch/manifest/resume integration tests;
- duplicate/rejection/max-attempt tests;
- Windows/module/console-entry invocation tests where practical;
- cross-process/PYTHONHASHSEED determinism;
- network-blocked CLI test;
- relevant M08 export tests;
- representative M03-M07 generator/quality regressions.

## 25. Full regression verification

Run and record:

- full `python -m pytest -q`;
- `python -m compileall -q src tests`;
- standalone package import;
- `python -m scrubbots_pixel_factory.cli --help`;
- installed entry-point smoke test if the local environment permits editable install without network;
- `git diff --check`;
- source scans proving no runtime HTTP/API/telemetry or logical resize/resample/interpolation was added;
- `python -m pip check` and distinguish pre-existing environment mismatch from introduced dependency problems.

Do not delete or weaken previous tests to make the suite pass.

## 26. Required review evidence

Commit deterministic M09 test fixtures/manifests only when they are small, project-owned and necessary as golden evidence.

Do not commit bulk generated candidate outputs from manual smoke runs.

At minimum provide repository tests that independently prove:

- a canonical completed batch manifest is byte-stable;
- a resumed run converges byte-for-byte with uninterrupted execution;
- reproduce is based on recorded historical request/config, not current defaults;
- failure/rejection/duplicate records remain distinguishable;
- rich provenance survives CLI generation/reproduction.

## 27. Acceptance gates for PAG-0901..PAG-0930

The milestone can close only if independent audit can establish:

- PAG-0901 generate command exists;
- PAG-0902 explicit difficulty;
- PAG-0903 optional width/height;
- PAG-0904 deterministic automatic legal dimensions;
- PAG-0905 explicit seed;
- PAG-0906 omitted single seed generated, printed and recorded;
- PAG-0907 mode support;
- PAG-0908 style/theme support;
- PAG-0909 output directory;
- PAG-0910 concise summary;
- PAG-0911 non-zero invalid/rejected exit;
- PAG-0912 reproduce command;
- PAG-0913 exact recorded config reproduction;
- PAG-0914 reproduced grid-hash comparison;
- PAG-0915 unsupported historical version/config fails loudly;
- PAG-0916 no silent default substitution;
- PAG-0917 deterministic batch orchestration;
- PAG-0918 attempts separate from accepted count;
- PAG-0919 every attempted seed recorded;
- PAG-0920 rejection codes recorded;
- PAG-0921 explicit max attempts;
- PAG-0922 no infinite loop;
- PAG-0923 resumable manifest;
- PAG-0924 duplicate candidate IDs prevented;
- PAG-0925 exact duplicate grids detected;
- PAG-0926 contact sheet/report;
- PAG-0927 same manifest rerun deterministic;
- PAG-0928 Windows command-line generation without Godot;
- PAG-0929 no internet during generation;
- PAG-0930 single and batch preserve provenance.

Passing tests alone are builder evidence, not final acceptance.

## 28. Prohibited shortcuts

Do not:

- bypass M07 quality to make accepted count easier;
- mutate rejected/duplicate grids;
- use timestamps/UUIDs/global random/Python hash for seeds or candidate identity;
- regenerate with an unrecorded seed;
- treat attempt count as accepted count;
- resume from `len(records)` without validating record sequence and immutable config;
- silently increase max attempts;
- recreate rich metadata manually when accepted candidate wrappers provide it;
- export raw WFC/HYBRID/AUTO `GenerationResult` and discard wrapper provenance;
- reproduce from current defaults instead of the recorded request;
- silently substitute missing exemplars;
- make network access a prerequisite;
- add M10 fuzz/performance acceptance or M11 Godot integration.

## 29. Builder completion record

Before stopping, the builder log must contain:

- exact changed files;
- M09 schema/exit-code/seed/candidate-ID decisions;
- exact focused and full test results;
- representative PowerShell/module CLI outputs;
- deterministic batch/resume/reproduce evidence;
- dependency/offline/path-safety evidence;
- implementation commit SHA;
- push result;
- completed-log publication commit;
- post-completed-log local `HEAD == origin/main`, divergence `0 0` verification.

## 30. Stop condition

Stop after `PAG-M09-C001` implementation/evidence/log publication.

Do not begin M10/M11.

Return the matching builder log to the owner for independent ChatGPT strict audit.