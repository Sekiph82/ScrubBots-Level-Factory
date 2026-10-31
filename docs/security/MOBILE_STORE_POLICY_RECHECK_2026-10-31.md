# Google Play Remote-Content / Code Policy Recheck — 2026-10-31

Checked on 2026-10-31 against current first-party Google Play policy pages. This is a dated engineering boundary review, not legal advice, an app-specific compliance determination, or a store approval. Recheck against the final shipped application and actual download flow before launch.

## Current policy sources

| Official source | Relevant current rule | Factory / SCRUBBOTS implication |
| --- | --- | --- |
| [Device and Network Abuse](https://support.google.com/googleplay/android-developer/answer/16559646), full policy | An app distributed through Play may not modify, replace, or update itself outside Play's update mechanism, and may not download executable code such as dex, JAR, or `.so` from another source. Runtime-loaded interpreted languages must not enable potential policy violations. | Remote level packs must remain fixed-schema data interpreted by shipped game code. The interpreter wording is not a blanket exemption for remote code or feature changes. |
| [Deceptive Behavior](https://support.google.com/googleplay/android-developer/answer/17006354), sections 3.2 and 5 | Additional app resources (including game assets) may be downloaded only when needed; the app should prompt and clearly disclose download size before the download. Hidden, dormant, or undocumented features and review-evasion techniques are disallowed. | Any future pack/asset download needs a necessary, user-visible flow with an accurate size disclosure. A remote pack must not activate undisclosed behavior. This policy review does not approve a downloader or deployment. |
| [Policy Archive](https://support.google.com/googleplay/android-developer/answer/13386702) | On the check date, the archive page listed 26 August 2026 as its newest archived policy version. The archive is change-history context; the live full-policy pages above remain the sources for current substantive rules. | The previous 2026-10-14 snapshot's latest-archived-version statement remains consistent with the opened archive page. |
| [Policy Deadlines](https://support.google.com/googleplay/android-developer/table/12921780) | The page also listed new 2026-10-29 announcements for future 2027 requirements, including Local Network and Manage Contacts permissions and AppFunctions. These do not alter the remote-content/code passages reviewed above. | Recheck any applicable permission requirement against the final Android target/API and actual app features. No such permission or AppFunctions implementation is established by this Factory review. |

## Existing boundary mapping

- The existing Content Platform contract permits declarative `LevelData`, `scrubbots.level_supply_plan.v1`, and publisher metadata; existing CP09-003/004 source evidence rejects executable/script-bearing payload surfaces. No new remote-code exception is inferred.
- The current factory source/policy documents do not establish that an Android game build downloads these packs, how the client prompts or discloses byte size, or how store reviewers will experience the final flow. The actual game client, signed release artifact, store listing, and user-facing flow were not audited in this task.
- Keep the remote-content boundary data-only and preserve the existing no-hidden-feature rule. Any future delivery must be necessary for gameplay, accurately disclosed, and reviewed in the actual client context before launch.

## Result and remaining gates

The relevant current code-download restriction and additional-resource disclosure passages remain consistent with the existing declarative-only design. This is a narrow policy-source recheck, not a claim that the app is compliant or approved. The final game/client review, actual download-flow and size-disclosure proof, current policy review immediately before launch, and independent security/store review remain open. Apple policy review is separate under `SB-CP09-002`.

