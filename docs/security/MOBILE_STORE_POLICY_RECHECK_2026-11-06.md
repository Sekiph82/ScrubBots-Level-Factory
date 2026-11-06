# Google Play Remote-Content / Code Policy Recheck — 2026-11-06

Checked on 2026-11-06 against current first-party Google Play policy pages and the October 29, 2026 policy announcement. This is a dated engineering boundary review, not legal advice, an app-specific compliance determination, or store approval. Recheck against the final shipped application and actual download flow before launch.

## Current first-party sources

| Official source | Current text relevant to remote content | Factory / SCRUBBOTS implication |
| --- | --- | --- |
| [Device and Network Abuse](https://support.google.com/googleplay/android-developer/answer/16559646) | Play-distributed apps may not self-update outside Play or download executable code such as dex, JAR, or `.so` from other sources. Runtime-loaded interpreted languages must not enable potential policy violations. | Keep remote packs as fixed-schema declarative data consumed by shipped game code. This does not create a remote-code exception. |
| [Deceptive Behavior](https://support.google.com/googleplay/android-developer/answer/17006354) | Additional resources such as game assets may be downloaded only when needed; the app should prompt and clearly disclose download size before downloading. Hidden or dormant functionality and review-evasion are disallowed. | A future pack flow needs a necessary, visible download with accurate size disclosure. Remote content must not introduce hidden behavior. No downloader or deployment is approved by this review. |
| [Policy Archive](https://support.google.com/googleplay/android-developer/answer/13386702) | The newest archived policy version listed on the check date is September 30, 2026, followed by August 26, 2026. | Replace the prior October 31 snapshot's August 26 latest-archive note; keep the live policy pages authoritative for current rules. |
| [Policy Deadlines](https://support.google.com/googleplay/android-developer/table/12921780) and [October 29, 2026 announcement](https://support.google.com/googleplay/android-developer/answer/18100766) | Newly listed deadlines include AppFunctions on 2027-04-14 and Local Network / Manage Contacts permissions on 2027-08-25. The announcement also reports a 2027-01-27 deadline for ongoing-eligibility subscription disclosures and clarifies other existing policies. | These changes do not establish that the game needs those permissions or APIs. Check target SDK and actual features before any Android release; avoid requesting permissions absent a real feature need. |

## Existing boundary mapping

- The Content Platform contract permits declarative `LevelData`, `scrubbots.level_supply_plan.v1`, and publisher metadata. Existing CP09-003/004 source evidence rejects executable or script-bearing payload surfaces. This recheck found no new basis to relax that boundary.
- The asset-download disclosure remains relevant: the eventual client must prompt users and disclose the exact download size before starting a necessary additional-resource download.
- The current Factory source and these policy pages do not prove that a shipped Android game downloads packs, how it presents consent/size, how its target SDK interacts with future permission requirements, or how Play reviewers will see the final flow.

## Result and remaining gates

The current first-party code restriction and asset-download disclosure remain consistent with the existing declarative-only design. This review is not an app-specific compliance finding or store approval. Actual game/client behavior, target SDK and permissions, download prompt and size disclosure, signed release artifact, store listing, and final review remain unverified. Recheck the live sources again immediately before launch. Apple policy remains separate under `SB-CP09-002`.