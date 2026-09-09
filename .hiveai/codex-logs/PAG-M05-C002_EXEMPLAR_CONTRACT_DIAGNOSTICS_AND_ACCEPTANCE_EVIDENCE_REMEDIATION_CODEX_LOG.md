# PAG-M05-C002 — Exemplar Contract, Diagnostics & Acceptance Evidence Remediation
Document role: CODEX BUILDER LOG

## 2026-09-09T19:30:00+03:00 — Start, authority, and process gate

- Implementation/task authority: https://github.com/Sekiph82/ScrubBots-Level-Factory
- Authoritative remediation prompt read directly from GitHub: https://raw.githubusercontent.com/Sekiph82/ScrubBots-Level-Factory/main/.hiveai/prompts/PAG-M05-C002_EXEMPLAR_CONTRACT_DIAGNOSTICS_AND_ACCEPTANCE_EVIDENCE_REMEDIATION_PROMPT.md
- Previous independent strict audit read directly from GitHub: https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M05-C001_WAVE_FUNCTION_COLLAPSE_GENERATOR_STRICT_AUDIT.md
- Primary conceptual reference: https://github.com/ikarth/wfc_2019f/tree/3a937fed13934722377dd7fb6dd238518fa644dd
- Secondary conceptual reference: https://github.com/mxgmn/WaveFunctionCollapse/tree/de7d22e705e816b62b4d613199d0463820fcaef3
- Canonical repository: `Sekiph82/ScrubBots-Level-Factory`; branch: `main`; local root: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Starting local HEAD: `f431b24b2c965e615898020d30d48dedbcbc6bde`; fetched `origin/main`: `e808dcab099f049195b3b6fb3daad8c04afcda3d`; starting ahead/behind: `0/12`.
- Starting status contained only pre-existing dirty `.hiveai/EVENTS.jsonl`, `.hiveai/HANDOFF.md`, `.hiveai/PROJECT.json`, `.hiveai/STATE.json`, and untracked `.hiveai/EVENT_INDEX.json`. Existing preservation stashes were retained.
- This matching C002 builder log was created before the first C002 source, test, fixture, golden, review, benchmark, or documentation edit.
- The main `C:\Users\sekip\Desktop\ScrubBots` repository is out of scope and has not been accessed or modified.

## Scope and ownership

- Implement only the four audited C001 findings: M01 production-artifact dimension validation, terminal contradiction/rejection diagnostics, truthful raw/transformed pattern counters, and missing review/golden/rectangular acceptance evidence.
- Preserve validated WFC extraction, transforms, adjacency, solver, palette mapping, periodicity, retries, offline boundary, and M00-M04 contracts. Do not begin PAG-M06+, modify task/H!veAI acceptance state, or author an audit.
- No upstream WFC source/sample artwork, runtime dependency, or new dependency is permitted. Synthetic fixtures remain test-only; no owner-approved exemplar ships in M05.

Further entries will be appended chronologically and truthfully.

## 2026-09-09T19:50:00+03:00 — Remediation implementation

- Reused the existing M01 `validate_dimensions(production_difficulty, width, height)` contract in `Exemplar`; no difficulty ranges were duplicated. TRAINING_MOTIF still accepts small logical fixtures. PRODUCTION_ARTIFACT now accepts EASY 20x20 and 29x23, MEDIUM 30x39, HARD 48x41, and VERY_HARD 59x50, while EASY 19x20 and 20x30 fail closed.
- Added immutable `WFCAttemptRecord` diagnostics and retained records on successful later attempts. Terminal `RETRY_EXHAUSTED` failures now expose a bounded canonical reason such as `bounded WFC generation attempts exhausted [0:EMPTY_WAVE@3,5;1:EMPTY_WAVE@3,5;2:EMPTY_WAVE@3,5]`; no exception repr, path, or mutable global state is exposed.
- Extended `PatternTable` with `raw_extracted_window_count` and `transformed_observation_count`; `extracted_pattern_count` now means raw windows. Counts are incremented before transform expansion and included in the canonical table digest. Exact checks cover 6x6 periodic N=2 = 36, 8x8 periodic N=3 rotations = 64, 12x12 periodic N=3 rotations/reflections = 144, and non-periodic formula counts.
- Added deterministic exemplar digests for golden/review provenance. Expanded goldens from the previous three square entries to five entries: retained EASY/MEDIUM/HARD cases plus EASY 29x23 and VERY_HARD 59x50 10-color evidence. Existing logical outputs remained unchanged; table/result evidence was regenerated for the corrected counter/digest contract.
- Expanded `review/m05/build_review.py` from 4 to 16 unique accepted candidates across all four synthetic exemplar IDs, multiple seeds, N=2/N=3, input periodic true/false, output periodic true/false where legal, rotations/reflections, and the four legal rectangular outputs. Every manifest candidate now embeds exemplar dimensions, logical pixels, source palette, ownership/provenance/digest, generated exact logical output, and WFC metadata. Contact sheet renders an exemplar motif canvas beside the generated output canvas for each candidate.
- Strengthened exemplar documentation: inbox items are not auto-approved; provenance and logical-contract validation are mandatory; upstream/external sample images are forbidden as owner exemplars; no owner-approved exemplar ships in M05. Fixture documentation now truthfully names five JSON fixtures including the benchmark fixture.
- No M00-M04 source or golden was modified, no M06+ implementation was added, no task/tracker/H!veAI acceptance state was edited, and the main ScrubBots repository was not touched.

## 2026-09-09T20:05:00+03:00 — Focused verification

- An initial focused command used `\\.venv\\Scripts\\python.exe` without the required leading dot and failed because PowerShell could not resolve the executable. The corrected `.\\.venv\\Scripts\\python.exe` command was run immediately.
- New adversarial/focused command: `.\\.venv\\Scripts\\python.exe -m pytest tests/unit/test_m05_wfc_contracts.py tests/unit/test_m05_wfc_patterns_solver.py tests/integration/test_m05_wfc_generator.py tests/integration/test_m05_review_evidence.py tests/golden/test_m05_wfc_golden.py tests/acceptance/test_m05_wfc_acceptance.py -q`; result: 23 passed, 1 existing pytest cache-permission warning.
- Adversarial coverage includes deterministic EMPTY_WAVE, reconstruction conflict, terminal all-attempt diagnostic summary, byte-identical failure replay, max-attempt behavior, later-success prior-history retention, retry-stream independence, missing-target-color rejection, production dimension legality, raw/transformed count truth, golden metadata revalidation, and all four generator-level rectangles.
- Review command: `.\\.venv\\Scripts\\python.exe review/m05/build_review.py`; result: `M05 review candidates: 16`, with paired exemplar/output evidence and rectangular candidates in the regenerated manifest/contact sheet.
- Acceptance command: `.\\.venv\\Scripts\\python.exe -m pytest tests/acceptance/test_m05_wfc_acceptance.py -q`; result: 120 total candidates, all accepted, including square and legal rectangular requests with metadata-count and deterministic rerun assertions.
- Benchmark command: `.\\.venv\\Scripts\\python.exe scripts/benchmark_m05.py`; result: N=2/N=3 non-periodic and periodic 59x59 cases all accepted. The refreshed report records raw windows 384, transformed observations 384, unique pattern counts 21/32, placement dimensions 58x58/59x59, three samples per case, and measured median/p95/worst timings. No M10 budget was invented.

## 2026-09-09T20:40:00+03:00 — Full regression and safety checks

- Full repository command: `.\\.venv\\Scripts\\python.exe -m pytest -q`; result: 231 passed, 1 existing pytest cache-permission warning, in 141.91 seconds.
- Standalone import command passed: `import scrubbots_pixel_factory; from scrubbots_pixel_factory.generators.wfc import WFCGenerator`, with the default production registry empty.
- Dependency command `.\\.venv\\Scripts\\python.exe -m pip check` passed: no broken requirements.
- An initial broad forbidden-runtime scan intentionally included the repository's cross-process tests and reported expected `subprocess` references there. The corrected production WFC-source-only scan passed: no random module, Python `hash()`, subprocess, eval/exec, network client, socket, URL, or HTTP runtime references.
- Corrected M06+ source scope scan passed: no PAG-M06, router, or hybrid implementation was found under the M05 WFC source.

## 2026-09-09T21:00:00+03:00 — Publication checkpoint

- GitHub synchronization: fetched `origin/main`, preserved the pre-existing dirty H!veAI control-plane files and the new C002 log in `codex-preserve-preexisting-controls-and-M05-C002-work-before-sync`, fast-forwarded local `main` from `f431b24b2c965e615898020d30d48dedbcbc6bde` to `e808dcab099f049195b3b6fb3daad8c04afcda3d`, reapplied the work, and resolved only control-plane stash conflicts by retaining the pre-existing local dirty versions. Current GitHub prompt/audit/control commits remain in repository history.
- Final C002 staged file list was limited to: this matching builder log; `exemplars/README.md`; M05 review/benchmark builders and regenerated artifacts; the WFC source model/exemplar/patterns/generator package; and M05 acceptance/golden/unit/integration tests. The five documented synthetic/benchmark fixture files from C001 were preserved unchanged and were not restaged. No ChatGPT-owned task/tracker/H!veAI state, prompt, audit, recovery, or main ScrubBots file was staged.
- Implementation/remediation commit: `e52559f` (`remediate M05 WFC evidence and diagnostics`). Push result: `e808dca..e52559f main -> main`.
- This log will be published in a separate log-only commit. Its own final commit SHA is intentionally not written into itself; the terminal repository HEAD will be independently recorded by ChatGPT/H!veAI.
- `git diff --check` passed with only normal CRLF conversion warnings on changed files and no whitespace errors.
