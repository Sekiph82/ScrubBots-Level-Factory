# Apple App Store Remote-Content / Code Policy Recheck — 2026-11-06

Checked on 2026-11-06 against the live first-party App Review Guidelines and Apple Developer Program License Agreement. This is an engineering boundary review, not legal advice, an app-specific compliance determination, or App Review approval. Recheck the actual final iOS binary, account agreement, content flow, disclosures, payment model, and distribution route before submission.

## Current Apple sources

| Official source | Current text relevant to the Factory / SCRUBBOTS goal | Engineering implication |
| --- | --- | --- |
| [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/), 2.5.2 | Apps should be self-contained and may not download, install, or execute code that introduces or changes app features or functionality. | Keep remote levels and packs as declarative data consumed by shipped game code. Do not deliver scripts, plugins, executable content, or remote feature changes. |
| [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/), 4.2.3(ii) | If additional resources are needed for the app to function on initial launch, disclose the download size and prompt users before downloading. | If first-launch gameplay depends on remote resources, verify the actual user prompt and accurate size disclosure in the shipped iOS flow. This text is specific to initial-launch resources; it does not establish a blanket rule for every optional later download. |
| [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/), 3.1.1 | Digital content such as game levels or premium content that unlocks app features/functionality generally requires In-App Purchase, subject to the current guideline and applicable storefront-specific terms. | Do not add an in-app paid-level or unlock flow without an explicitly approved payment design and a current storefront/region review. This project review does not establish any sales model. |
| [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/), 5.1.1 | Apps must link an accessible privacy policy in App Store metadata and in the app; it must identify data collected, collection/use, and third-party sharing. | Any future telemetry or service-mediated personal-data flow needs a product-specific inventory and matching disclosures. No Factory review establishes the iOS app’s actual data flow or privacy policy. |
| [Apple Developer Program License Agreement](https://developer.apple.com/support/terms/apple-developer-program-license-agreement/), 3.3.1(B)-(C) | Executable-code downloads are generally prohibited. Interpreted-code and programming-environment exceptions have specific limits; features/functionality generally may not be enabled through other distribution mechanisms without Apple approval or an identified exception. | The remote-content contract stays data-only. Do not rely on an interpreted-code exception, a feature flag, or a pack to introduce additional app functionality. |

## Existing boundary mapping

- The Content Platform’s approved remote families are declarative level data, `scrubbots.level_supply_plan.v1`, and publisher metadata. Existing CP09-003/004 evidence keeps executable expressions and behavior-changing payload surfaces outside that contract.
- This review does not use Guideline 4.7 as an exception for levels or packs as mini-apps, mini-games, plug-ins, or other software.
- No current iOS game binary or client behavior was inspected. Repository evidence does not prove container use, download prompts/size, payment implementation, privacy-policy presentation, or third-party data sharing.

## Result and remaining gates

The current Apple text supports retaining the data-only remote-content boundary and requires a final product-specific review of initial-launch resources, digital-content payment, privacy, and distribution. This record does not establish app compliance, account agreement status, or App Review acceptance. iOS client/runtime review, final binary and user-flow evidence, storefront-specific payment review, privacy disclosures, developer-account agreement status, and App Review remain unverified. Google Play remains separate in `docs/security/MOBILE_STORE_POLICY_RECHECK_2026-11-06.md`.