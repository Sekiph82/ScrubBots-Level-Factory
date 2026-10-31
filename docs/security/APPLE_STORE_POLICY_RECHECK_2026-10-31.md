# Apple App Store Remote-Content / Code Policy Recheck — 2026-10-31

Checked on 2026-10-31 against current first-party Apple policy and agreement pages. This is an engineering boundary review, not legal advice, an app-specific compliance determination, or App Review approval. Recheck against the final iOS binary, content flow, disclosures, and distribution route before launch.

## Current Apple sources

| Official source | Relevant current rule | Factory / SCRUBBOTS implication |
| --- | --- | --- |
| [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/), 2.5.2 | Apps should be self-contained in their bundles and may not read or write outside their designated container area, or download/install/execute code that introduces or changes app features or functionality. The narrow educational-code provision has its own conditions. | Remote levels must remain data consumed by shipped game code; do not deliver scripts, plugins, executable content, or remote feature changes. This does not establish that a proposed client implementation is acceptable. |
| [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/), 4.2.3(ii) | If the app needs additional resources to function on initial launch, disclose the download size and prompt the user before downloading. | If initial gameplay depends on a remote resource, the final iOS flow must be checked for necessity, prompt, and accurate size disclosure. The guideline is specific to initial-launch resources; this review does not infer a universal approval rule for all optional later downloads. |
| [Apple Developer Program License Agreement](https://developer.apple.com/support/terms/apple-developer-program-license-agreement/), 3.3.1(B)-(C) | Executable-code downloads are generally prohibited, with a limited interpreted-code provision subject to purpose/security/storefront conditions. Additional features or functionality generally may not be enabled through mechanisms outside the specified distribution routes without Apple’s prior written approval or an identified exception. | Keep packs within the already shipped game purpose and feature set. Do not rely on the interpreted-code provision or a remote flag to add functionality. The current declarative-data contract remains the intended boundary. |
| [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/), 5.1.1 | Privacy-policy information must identify data collected, collection methods and uses, and applicable third-party sharing; the policy must be accessible in App Store metadata and within the app. | Any future telemetry or provider-mediated personal-data flow needs a product-specific inventory and matching disclosures. This Factory review does not establish an iOS privacy policy or app data flow. |
| [Apple update announcement, 2026-06-08](https://developer.apple.com/news/?id=a233fmpw) | Apple announced revisions to the App Review Guidelines and Developer Program License Agreement on 2026-06-08, including changes to sections other than the remote-code passages listed above. | The current live full texts were checked on 2026-10-31. Recheck again immediately before a real submission; do not treat this dated review as a permanent policy guarantee. |

## Existing boundary mapping

- The Content Platform’s approved remote families are declarative level data, supply plans, and metadata. Existing CP09-003/004 source evidence keeps executable expressions and behavior-changing payload surfaces outside the contract.
- Apple Guideline 4.7 is not used as an exception for SCRUBBOTS levels or packs as mini-apps, mini-games, plug-ins, or other software. Any future proposal in those categories needs separate owner, privacy, legal, and App Review analysis before implementation.
- No current iOS game binary or client behavior was inspected. The repository evidence does not prove the actual client’s container use, download prompt/size display, privacy-policy presentation, or data-sharing behavior.

## Result and remaining gates

The current Apple text supports retaining the data-only remote-content boundary and requires careful review of any initial-launch resource download and personal-data flow. No implementation or distribution approval follows from this policy mapping. iOS client/runtime review, final binary and user-flow evidence, privacy disclosures, developer-account agreement status, and App Review remain unverified. Google Play policy is tracked separately in `docs/security/MOBILE_STORE_POLICY_RECHECK_2026-10-31.md`.

