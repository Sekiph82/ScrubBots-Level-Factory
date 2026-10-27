# SB-LFX-018 R05 V13-C/D R09: PixelLab Pro Flash V2 zero-spend readiness

**Result:** `R09_PIXELLAB_ZERO_SPEND_READINESS_BLOCKED`

**Folder reconciliation:** `FOLDER_MERGE_PARTIAL_CONFLICT` — the secondary Desktop folder is a separate SCRUBBOTS Godot game project, not a second copy of this repository. No files were copied. Three same-path files differ; all copies were preserved. The nested source `.git` pointer targets a worktree under `C:\Users\sekip\Desktop\ScrubBots\.git`, outside the two authorized roots; it was not followed.

## Desktop folder reconciliation

Verified roots:

- Canonical: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
- Secondary: `C:\Users\sekip\Desktop\ScrubBots-factory\060-m43-078-shop`
- Secondary inventory: 7,031 files, 698 directories, 2,591,759,861 bytes; no reparse paths.
- The separate root classified 2,237 media/release/batch/manifest paths, 15 sensitive-name/path candidates, and 4,779 unrelated review candidates. These were not bulk-hashed or copied. Its root TASKS/AGENTS/CLAUDE/project configuration, `.git`, caches, generated assets, Release data, coordination and batch data were excluded.
- Focused SHA-256 path matrix for 17 `level_factory` and `content_pipeline` design/config candidates (source SHA / canonical SHA / decision):

| Source → canonical relative path | Source SHA-256 | Canonical SHA-256 | Decision |
|---|---|---|---|
| `level_factory/README.md` | `D3C41F99FB7F6FE8D3F59A35089C6FBFF6F5B1AF370225F613B721A1C7F886DA` | `4F08DAF640F4E8FDE8BBD6C558BD100D5046C50F8F233C5F0F32140AB883F196` | Collision; preserve both |
| `level_factory/project.godot` | `FF0614C317011558766D67DEA7633566B230995E027BEF337BED66727B14EE01` | `4ADB4B9B939D8AF178516E86A170AB1E8D725F32D8B4D3F1B8464E4759C655C7` | Collision; preserve both |
| `level_factory/CLAUDE.md` | `E5AC1FC1B08A21E98F4CD1195332412FC108C11A79330A35626917F9A7A81AC5` | Missing | Separate-project instructions; do not copy |
| `level_factory/docs/00_VISION_AND_SCOPE.md` | `013F13D7DEFFBFE3441305305AB436EF2B7826A64967DF325E7DD85F1EB4063A` | Missing | Separate-project design; do not copy |
| `level_factory/docs/01_ARCHITECTURE.md` | `A731ABCCCE02B456D6EC4C82B72A1D2CA943D288FD8B7B8DF9E5324DEA4D73E1` | Missing | Separate-project design; do not copy |
| `level_factory/docs/02_ROADMAP.md` | `10445B3FBA795D8F3AB071DD602BDB0AD5741D82C7B16FA7704BAECE6AC0096F` | Missing | Separate-project roadmap; do not copy |
| `level_factory/data/canonical_visual_contract_v1.json` | `7EE07337B7FD44B9BA32C17CDD33D8A4A4D1E480E456C67704F499F26C8597BE` | Missing | Foreign descriptor; canonical visual authority already exists here |
| `content_pipeline/README.md` | `5B10C2A9EE74EE2CA885A98E6E3AC3A11DB6331E9D9646BA1BF1BB6B5D24C0ED` | `4F24021DDEBF22E9F4CEB5CAFFCC0183775816E5BBAE8AAEC1C363B89B817492` | Collision; preserve both |
| `content_pipeline/CLAUDE.md` | `E017FF81C23D95B80F8F58A00E29491B50688A365799ACA155F6EB75DC8BB653` | Missing | Separate-project instructions; do not copy |
| `content_pipeline/docs/00_VISION_AND_SCOPE.md` | `C626BF56915A32ABEB8C0E118F7CD256DED563B192E356608A5067A1715076D5` | Missing | Separate-project design; do not copy |
| `content_pipeline/docs/01_ARCHITECTURE.md` | `B34F64D1895063FB8E46180B8F29324288831A7070CAECCA8F58324FE2A5D467` | Missing | Separate-project design; do not copy |
| `content_pipeline/docs/02_SCRUBPACK_SPEC.md` | `94321084A1F91355C14AFB2D588F8730E987D0C95948F65AF2E7BF80EBA02B42` | Missing | Separate-project format; do not copy |
| `content_pipeline/docs/03_MANIFEST_SPEC.md` | `6E47422BD3AF89F125FEF4A25E750C95AC759E8A786B8FC7EC31F0D411750561` | Missing | Separate-project format; do not copy |
| `content_pipeline/docs/04_PUBLISH_WORKFLOW.md` | `080549490E1233016DC6E86D2FFA96AA21728063791CE3D21987DE0E9694AE89` | Missing | Separate-project workflow; do not copy |
| `content_pipeline/docs/05_REMOTE_RUNTIME_CONTRACT.md` | `6432FAD40B17EC32FD88F71150BE9A3151B5246A6B70E1283B530B9575FC770C` | Missing | Separate-project contract; do not copy |
| `content_pipeline/docs/06_SECURITY_POLICY.md` | `729554E19CDA64BF66F3895D6A59908FDAE8BFBBC4FE932348A9BCC35CFAD0D2` | Missing | Separate-project policy; do not copy |
| `content_pipeline/docs/07_ROADMAP.md` | `901108ED8F279E38BA6AA9843FA90F0DB2004E08B9BB651372B4135FCC479B2F` | Missing | Separate-project roadmap; do not copy |

The candidate designs describe a distinct Godot subproject with its own roadmap and lifecycle, while the same-path project and README files have conflicting bytes. None is demonstrably required by the R09 PixelLab route, so importing them would create an ambiguous second source of project rules. Secondary originals remain untouched.

## PixelLab no-spend readiness

- `PIXELLAB_LOCAL_CREDENTIAL_STATUS`: `PIXELLAB_API_TOKEN_NOT_CONFIGURED`. The status helper and presence-only environment checks emitted no secret values; `PIXELLAB_API_TOKEN` and `PIXELLAB_SECRET` were absent in this shell. PixelLab Creator/MCP login is not local worker credential proof. No credit balance or account endpoint was queried.
- `PIXELLAB_SOURCE_ROUTE`: Pixel Art provider options expose `PIXELLAB` as Pro Flash. A single paid Generate/Regenerate action requires a confirmation dialog; CSV batch is blocked for PixelLab. The launcher records an operation before its one POST, prevents duplicate/uncertain operations from being resubmitted, and the adapter polls the returned job ID without automatic POST retry. It locally validates the returned PNG and imports the candidate under `level_factory/output/semantic-generated`, separate from the original owner 140 PNG path.
- Fixed 32×32 policy is now enforced in the Pixel Art UI on provider selection, size dialog, Generate, and paid confirmation. The local launcher also rejects a Pro Flash request with any other dimensions before dispatch. ALPIX dimensions remain unchanged.
- Pro Flash sends the canonical V3 16-color target palette with `max_colors=12`; local validation requires exact requested dimensions, opaque-or-fully-transparent pixels, canonical colors, and 3–12 used colors. There is no separate Style button in the inspected Pixel Art UI. PixelLab source validation checks the PNG byte signature, dimensions, palette, and alpha contract.
- During focused test execution, six previously passing-in-intent synthetic checks failed because the adapter tested a nonstandard PNG signature ending `\r\n`. The PNG specification signature ends `\n`; both response extraction and local validation were corrected. The same focused suite then passed.
- `PIXELLAB_INSTALLED_GUI`: `NOT RUN` (Godot invocation is prohibited by the consumed one-time R08 permission). Source and installed Release hashes differ for `factory_core_launcher.py`, `studio_extensions.py`, and `factory_studio_exact_ui.gd`. The existing `INSTALL_BLOCKED_MANIFEST_DRIFT` / missing `verify.py` receipt remains open; no Release file or manifest was changed. `PROCESS_QUIESCENCE_UNPROVEN` remains open. A source PASS is not installed GUI acceptance.
- `PIXELLAB_PAID_E2E_NOT_RUN`: no provider network, generation, credit use, or job submission occurred. The fixed cost and available credits remain unknown. One real 32×32 image still needs separate owner credit-spend approval after install readiness gates are resolved.

## Local verification

- `python -B scripts/codex/scrubbots_task_queue.py --json` — passed at the synchronized R09 task/prompt pins.
- `pytest --collect-only -q -p no:cacheprovider tests/unit/test_pixellab_pro_flash_v12.py` — collected 15 tests before adding two focused fixed-canvas tests.
- Initial offline subset — 6 failed, 5 passed; failure evidence identified the malformed PNG signature. No request reached the network; request callbacks were mocks.
- Corrected focused offline subset:
  `pytest -q -p no:cacheprovider -p no:tmpdir tests/unit/test_pixellab_pro_flash_v12.py::test_v3_palette_payload_is_exact_and_pro_flash_job_is_polled_without_resubmit tests/unit/test_pixellab_pro_flash_v12.py::test_old_palette_and_semitransparent_pixels_fail_closed tests/unit/test_pixellab_pro_flash_v12.py::test_older_attached_palette_is_not_misidentified_as_scrubbots_v3 tests/unit/test_pixellab_pro_flash_v12.py::test_provider_http_errors_are_truthful_and_redacted tests/unit/test_pixellab_pro_flash_v12.py::test_dimension_and_used_color_envelope_fail_closed tests/unit/test_pixellab_pro_flash_v12.py::test_dimensions_are_four_pixel_steps_and_no_submission_retries tests/unit/test_pixellab_pro_flash_v12.py::test_preferred_api_token_and_mismatched_legacy_secret_fail_without_network tests/unit/test_pixellab_pro_flash_v12.py::test_semantic_generation_dispatches_to_pro_flash_without_fallback tests/unit/test_pixellab_pro_flash_v12.py::test_semantic_generation_rejects_non_32x32_pro_flash_before_dispatch tests/unit/test_pixellab_pro_flash_v12.py::test_pixellab_pixel_art_ui_enforces_fixed_32x32_canvas`
  Result: **14 passed**. `-p no:tmpdir` prevented Windows TEMP-backed pytest fixtures; three tests requiring `tmp_path` were not run.
- No Godot/native test, CI/Actions, paid API, Release apply, batch job, original PNG, or Pool mutation was run.

**Final state:** zero-spend source preparation is implemented and locally tested, but production readiness is blocked by missing local credential, Release manifest drift, and unproven writer quiescence. No `TASKS.md`, prompt, or audit was edited.
