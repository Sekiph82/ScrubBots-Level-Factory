# Mobile / Store Policy Boundary V01

Document role: M11 policy-boundary evidence

## Scope and conclusion

This report re-checks first-party Apple and Google Play policy sources on
2026-10-04 UTC and maps them to the M11 Content Platform architecture present
in this repository. The review is limited to the architecture boundary; it is
not legal advice or a store review decision.

The current M11 design is **architecturally consistent with a declarative
remote-data boundary**: its eligible remote families are fixed-schema data,
and remote executable or behavior-changing surfaces remain outside the
accepted boundary. The reviewed policies do not establish that any particular
app or future delivery implementation will be accepted. Store policies can
change.

M15/M16 runtime work and M18 provider work remain unimplemented or separately
unverified by this report. M20 owns the final pre-production re-check:
`SB-CP09-001` and `SB-CP09-002` must re-fetch the then-current official Google
Play and Apple policies before production launch. Any future executable or
interpreted-code capability requires explicit new owner authorization and a
policy/security review. This report does not rely on Apple Guideline 4.7 as a
silent basis for serving SCRUBBOTS levels as mini-apps or mini-games.

## Official sources checked

All URLs below are first-party pages and were retrieved on 2026-10-04 UTC.
Paraphrases are concise summaries of the indicated sections.

| Platform | Official page and exact URL | Checked (UTC) | Section identifiers | Policy paraphrase | SCRUBBOTS relevance and M11 disposition | Future dependency |
| --- | --- | --- | --- | --- | --- | --- |
| Google Play | Device and Network Abuse — <https://support.google.com/googleplay/android-developer/answer/16559646> | 2026-10-04 | Device and Network Abuse; full-policy executable-code restriction; runtime-loaded interpreted languages | The policy bars self-updating outside Play and downloading executable code such as dex, JAR, or native shared objects from outside Play. It describes an interpreter/virtual-machine nuance and requires runtime-loaded interpreted code to avoid policy violations. | Supports keeping executable payloads out of the remote-content contract. M11 rejects executable markers and authorizes only the listed declarative data families; it does not attempt to use the interpreter nuance. | M20 `SB-CP09-001` must re-fetch this policy before production; any proposed runtime loader needs a separate review against its exact behavior and distribution path. |
| Google Play | Deceptive Behavior — <https://support.google.com/googleplay/android-developer/answer/17006354> | 2026-10-04 | 3.1; 3.2; 5 Behavior Transparency | The policy calls for accurate disclosures about app functionality and content. Additional app resources must be necessary for use and users must be prompted with the download size disclosed. Hidden, dormant, or undocumented features, review evasion, and remote code that adds functionality absent during review are disallowed. | M11 data must stay within the app's disclosed game/content contract; it cannot activate hidden functionality. No asset download is implemented. Any later remote resource flow must meet applicable disclosure and content requirements. | M20 `SB-CP09-001` must re-fetch before production; M15/M16 must be reviewed against the actual user-visible runtime and download flow. |
| Google Play | Policy Archive — <https://support.google.com/googleplay/android-developer/answer/13386702> | 2026-10-04 | Past Policy Versions; latest listed version: August 26, 2026 | Google states that policies are regularly updated and the archive lists dated prior versions. On the check date, August 26, 2026 was the latest listed version. This page supplies change-history context; the current live policy pages above supply the substantive rules summarized here. | Confirms policy drift is expected and a dated snapshot cannot be treated as a standing release determination. | M20 `SB-CP09-001` must check the current live policy and archive context again before production. |
| Apple | App Review Guidelines — <https://developer.apple.com/app-store/review/guidelines/> | 2026-10-04 | 2.5.2; 4.7; 4.7.1–4.7.5 | Guideline 2.5.2 expects apps to be self-contained and bars downloaded, installed, or executed code that introduces or changes app features or functionality, with a limited educational-code provision. Guideline 4.7 covers specified non-embedded software categories and adds requirements for software offered under that rule. | Fixed-schema level and supply data is the M11 intent; it contains no application code. This is an architecture-level mapping only. M11 does not characterize levels as mini-apps and does not invoke 4.7 as an exception. | M20 `SB-CP09-002` must re-fetch the current Guidelines. Any future content that is software or changes app behavior needs owner authorization and a dedicated policy/security review. |
| Apple | Apple Developer Program License Agreement — <https://developer.apple.com/support/terms/apple-developer-program-license-agreement/> | 2026-10-04 | 3.3.1(B) Executable Code; 3.3.1(C) Additional Features or Functionality | The agreement generally bars downloading or installing executable code, constrains downloaded interpreted code so it does not alter the advertised purpose or bypass OS security, and restricts enabling additional functionality through other distribution mechanisms absent prior written approval or an identified exception. | Reinforces the M11 rule that remote payloads provide data within the shipped app contract, never code, plugins, or a remote feature switch. No runtime provider is present to assess actual delivery behavior. | M20 `SB-CP09-002` must re-fetch the current agreement before production; proposed delivery and monetization behavior require review in their implemented context. |

## M11 architecture mapping

| Surface | Current repository contract | Boundary disposition |
| --- | --- | --- |
| LevelData V1 | Fixed allow-list of version, identity, difficulty, dimensions, palette, and integer palette-index cells; payload parsing does not import or execute content. | Declarative data only. |
| `scrubbots.level_supply_plan.v1` | Versioned fields describe level supply batches and constraints; unknown or executable-bearing fields fail closed. | Declarative data only. |
| `scrubbots.level.metadata.v1` | Versioned publisher metadata and file digests; it has a fixed field allow-list. | Declarative data only. |
| CP003 payload validation | Strict JSON, descriptor and digest binding, resource bounds, and executable/script/resource marker rejection. | Executable or smuggled behavior payloads are rejected. |
| CP007 dry-run planning | Local deterministic plan; the dry-run result fixes `remote_mutation_performed` to false. | No remote mutation. |
| CP008 provider abstraction | Provider-neutral protocols and capability declarations; no concrete network or storage provider is shipped. | Future provider behavior is not yet verified. |
| CP006 credential boundary | Secret references are opaque; repository configuration contains no credential retrieval or secret values. | No publishing credentials in Git/project data. |
| Runtime manager | No remote runtime manager or content downloader exists in this repository. | Runtime delivery and enforcement remain unverified. |

## Forbidden by the current Content Platform boundary

The following remain outside the authorized boundary: remote `.gd`, `.cs`,
dex, JAR, native libraries, DLL/SO/dylib, WASM, or other executable code;
downloadable plugins, addons, or autoloads; remote scenes, resources, or
shaders used to supply application behavior; eval/exec or interpreted-code
payloads; remote activation of hidden or dormant functionality; dynamic
feature injection that changes behavior beyond the reviewed app contract; and
review-environment detection or evasion. Apple Guideline 4.7 is not a blanket
exception for SCRUBBOTS levels. Any future declarative exception for a currently
forbidden surface needs explicit owner authorization and policy/security
review before implementation.

## Release and evidence limits

The snapshot at
`content_pipeline/policy/mobile_store_policy_boundary_v1.json` records the
source check and boundary vocabulary. It is a dated architecture snapshot, not
a continuing policy monitor. No web scraper is part of product code. A policy
or architecture change, runtime downloader, concrete provider, executable or
interpreted-code feature, hidden activation path, or store-specific release
plan requires a fresh policy review. M20 retains the pre-production check for
`SB-CP09-001` and `SB-CP09-002`.
