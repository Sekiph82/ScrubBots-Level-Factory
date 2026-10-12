# R09-R02 Independent Strict Audit V01: Offline Native Proof vs Studio Owner Windows UI

Document role: CHATGPT INDEPENDENT AUDIT. Date: 2026-10-12. Source repo: Sekiph82/ScrubBots-Level-Factory main.

## 1. VERDICT
CONDITIONAL. Offline one-level native SOLVED, replay WIN, Difficulty V1, QA and separately capped same-winner load-check READY: builder evidence accepted narrowly as OFFLINE_ONE_LEVEL_VALIDATED_CP_X002_PENDING, not independently re-executed. The installed Factory Studio GUI LIVE PIPELINE implementation FAILS owner acceptance: user's actual Windows screenshot reports MONITOR MISMATCH and Backend response and durable activity terminal event do not agree, Details still Solver: Awaiting pipeline. No Release Pool entry or live Family APK release; parent R05 OPEN.

## 2. CONTRACT RECOVERY
Owner approved a genuinely live scrollable chronological event feed in blank LEFT LEVEL FACTORY WORKSPACE, between Level/3/4/5/Max Robots/Background controls and existing bottom Run Pipeline. Original three masters PIXEL ART / LEVEL FACTORY / RELEASE POOL preserved. Earlier three-master written design V03 was explicitly excepted for that left rectangle. Owner did not request a long raw debug-information label.

## 3. BRANCH / HEAD / DIFF SCOPE
Verified product/docs/tests commit c7f896798594b4a231eb7d7b9b4f51107d3a800b (LF UI, gateway, Python activity writer, extension, tests, UI master exception, R09 shared preflight). Extra viewport test 119c63defa9352ce042e3c099dcd43b893c1b288; R05 builder-log terminal ea722bac2b07a9ce2dd221e04ba9dc5338f4f1c3. Builder claims main 0/0 and no tracked diff; GPT checked GitHub source, not local owner disk.

## 4. ACCEPTANCE MATRIX
A: Shared true-input PRE_NATIVE_READY with 0 dry-run Godot calls, PASS builder evidence.
B: One genuine pinned native candidate r09-s17018-p01-m0 SOLVED, 52 visited, 74.531s under 90s cap, replay WIN, Difficulty V1 and conservation, PASS builder evidence only.
C: Optional one native same-winner shipping load-check READY in 65.531s, three loader/validator gates PASS, PASS builder evidence only.
D: CPX-002 full-game shipping replay, NOT DONE; Release Pool eligibility FALSE, no cloud publish.
E: Activity panel exists in approved physical left gap, PARTIAL layout.
F: Live event stream truth/reason, FAIL user Windows MONITOR MISMATCH.
G: Scrollable per-stage timestamped concise history, FAIL: single fixed text Label.
H: Details updated on genuine failure, FAIL: Awaiting pipeline.
I: Earlier four imported PNGs still visible, FAIL user expectation: current bottom says 1 PNG / 1/1; historical files NOT proven deleted.
J: Owner visual Windows acceptance, FAIL.
K: No R2/STAGING/PRODUCTION mutation, PASS builder report.

## 5. BUILDER CLAIMS VS REPOSITORY
The code does contain a Godot Thread pipeline worker, bounded SHA-chained Python events, and panel; screenshot demonstrates failure for the actual user click. Focused Godot suite proved panel geometry, tab isolation and no spurious run on tab navigation; it did not prove real click-to-terminal event fidelity. The separately run offline R09 solver success DOES NOT mean clicked Studio Run Pipeline succeeded. Builder log admits owner in-session visual acceptance and real event stream were pending.

## 6. SOURCE / SYMBOL EVIDENCE
F01: factory_studio_exact_ui.gd _poll_pipeline_activity reads the entire JSONL file from byte zero every _process frame but retains _activity_seen_sequence and _activity_previous_sha256 across frames. Once seq=1 was consumed, subsequent poll re-sees seq=1 expecting seq=2. This fails the chain and blocks new terminal event intake; a cursor/offset or verified-skip strategy is REQUIRED.
F02: studio_extensions.py run_pipeline emits initial SOURCE events, but early source invalid/structural-stopped return branch (including possible VOID_CAPABILITY_UNAVAILABLE or absent current game authority) builds and returns UNAVAILABLE/PARTIAL STOPPED without emitting final PIPELINE activity record. Errors before writer setup also leave no terminal. _complete_level_pipeline then sets MONITOR MISMATCH instead of displaying actual backend disposition/error/rejection code. Exact trigger for this user's run needs read-only inspection of local JSONL and returned backend payload.
F03: _activity_display_text renders long complete source ID, run ID and one last stage/message in a single 308x224 Label; no ScrollContainer, per-stage history or scroll-follow. Screenshot shows the long source wrapping consumes panel space.
F04: _refresh_live_data maps empty primary to Solver: Awaiting pipeline and ignores final pipeline disposition, error and stages reasons.
F05: _imported_sources is a volatile in-memory array and _upsert_imported_source populates it only when selecting/importing PNGs; no verified on-launch restore. User's screenshot shows 1 imported/reused while earlier screenshot showed 4. First verify immutable installed source records are present; never assume files deleted or re-import automatically.
F06: _complete_level_pipeline has duplicate _last_pipeline, _report and _operation_running block at end.
F07: Python activity writer hashes canonical sorted compact JSON while reader uses Godot JSON.stringify; cross-language canonicalization/UTF-8 must be proven using realistic payload and newline append events, not only Python emitter isolated tests.

## 7. FOCUSED TEST EVIDENCE
Builder log reports 2 new Python focused checks PASSED, activity Godot headless/display suite PASS after revised viewport assertion, one graphical Release viewport capture, shutdown RID/ObjectDB warnings. Missing: live staged delayed mock worker across multiple Godot polls, terminal event on early-stop and launcher exceptions, reason surfacing, reopened real import selection, long text fit/scroll. GPT did NOT re-run code or native Godot.

## 8. REGRESSION EVIDENCE
Prior R09/R08/M14/M18 accepted builder tests not repeated, appropriate. No comprehensive regression requested. Owner screen is the first actual installed interaction test and fails.

## 9. SECURITY / SAFETY
Builder claims installed Release three original files replaced + one activity-writer file added with backups in LF approved output; manifest changed 2077 to 2078 managed files. Old launcher/shortcut unchanged, game repo untouched, 57 protected owner roots. Screenshot captured running application; future edit must not force close or overwrite active process; require owner close safely before narrow file copy. No extra cloud/solver authority granted by UI remediation.

## 10. ARCHITECTURE CONSISTENCY
Current Python writer can support honest streaming once terminal/failure always emits and Godot reader uses stable incremental cursor. The pinned LF-only offline mini-runtime used for R09 is separate from installed Studio's standard source/game rule route and from full-game CPX-002 replay. No fake READY/automatically copied offline result into release panel.

## 11. TRACKER / LOG TRUTH
One R05 builder log contains proof chronology and correct CPX-002 pending statement. A historical log subsection predating R09-R02 says Release untouched; later R09-R02 section correctly states installed update. Don't misquote earlier subsection as latest result. GPT alone updates TASKS and audits.

## 12. FINAL REPOSITORY STATE
R09-R02 log published at ea722bac2b07a9ce2dd221e04ba9dc5338f4f1c3 (builder 0/0). Subsequent GPT audit/tracker changes may advance GitHub main; no implied new installed version.

## 13. OPEN CROSS-MILESTONE FINDINGS
Live Studio source pipeline blocked or malfunctioning, exact underlying cause not yet identified because generic mismatch. Four-to-one visible import queue discrepancy. Offline one-level proof exists but no CPX-002 current full-game replay/Release Pool eligibility/R2. R05 OPEN.

## 14. DEFECTS BY SEVERITY
BLOCKER UI-F01 incremental reader re-reads old events; BLOCKER UI-F02 missing mandatory terminal record on early-stop/error, hides true reason; MAJOR UI-F03 text dump not requested timeline; MAJOR UI-F04 Details stale; MAJOR UI-F05 four visible imports become one on new session; MINOR UI-F06 duplicate final result/report; NOTE UI-F07 cross-language hash parity unverified.

## 15. TECHNICAL DEBT / OPPORTUNITIES
Introduce monotonic event tail cursor + bounded chronological scroll list; guaranteed once-only PIPELINE terminal on all normal/exception branches; persistent verified import queue; explicit run/source identity, last genuine event, elapsed, stage/reason; asynchronous UI preserved. No extra owner-facing screens.

## 16. UNVERIFIED
User's actual installed JSONL events and backend JSON payload are not accessible from GitHub. MONITOR MISMATCH screenshot alone cannot determine whether Python failed specifically at SCRUBBOTS_PROJECT, VOID, catalog, hash mismatch, or worker transport. Screenshot cannot establish active process state. Immutable previously imported source records may still exist.

## 17. REGRESSION RISK
High for false READY, threaded UI errors, stale events, worker duplication and overwrite of running Release; medium for source selection/catalog/resize; low for prior solved offline candidate when not rerun.

## 18. CONFIDENCE
High on verified published GDScript/Python code defects and screenshot; medium on builder-only offline native solver/load-check proof; low on exact installed runtime failure until actual event files/result are inspected.

## 19. FINAL VERDICT
CONDITIONAL; offline native one-level result technical PASS on builder evidence, installed owner Studio PIPELINE ACTIVITY and real clicked pipeline FAIL. No owner's visual approval or Family APK production readiness.

## 20. REQUIRED REMEDIATION
One focused R09-R02-R01 OWNER-WINDOWS Studio-only fix: read failed run events and backend result read-only; fix file cursor/hash handling and terminal contract, display real backend reason, replace single Label with compact header + timestamped scrollable event list in same approved rectangle, preserve layout/import queue across restarts, update Details coherently; new focused fake asynchronous tests, safe narrow installed Release update with byte backups, real owner screenshot acceptance. ZERO new R09 native solver attempts, no CPX-002, no R2, no full regression or old suite reruns.
