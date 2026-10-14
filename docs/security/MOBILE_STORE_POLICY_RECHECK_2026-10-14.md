# Mobile Store Remote-Content Policy Recheck — 2026-10-14

Checked on 2026-10-14 UTC using the current official pages below. This is a dated engineering boundary summary, not legal advice, a store approval, or a release-specific compliance determination. Recheck the live sources against the final app and download flow before launch.

| Store | Official source | Relevant current text | Factory / remote-content implication |
| --- | --- | --- | --- |
| Google Play | [Device and Network Abuse](https://support.google.com/googleplay/android-developer/answer/16559646?hl=en) | Play prohibits self-updating outside Play and downloading executable code such as dex, JAR, or `.so` from outside Play. Runtime-loaded interpreted languages remain subject to policy. | Remote packs must remain fixed-schema data consumed by shipped game code. No scripts, modules, plugins, native code, or behavior changes. |
| Google Play | [Deceptive Behavior](https://support.google.com/googleplay/android-developer/answer/17006354?hl=en) | Additional game resources may be downloaded only when necessary; the app should prompt and clearly disclose download size before transfer. Hidden or undocumented features and review evasion are disallowed. | Any future asset/content delivery must be user-visible, necessary, accurately disclosed, and kept within the reviewed game contract. No delivery implementation is approved by this policy check. |
| Apple App Store | [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/) | Guideline 2.5.2 requires self-contained apps and bars downloaded, installed, or executed code that introduces or changes app functionality, with a limited educational-code exception. | Continue the declarative-data-only boundary. Do not classify levels or remote packs as mini-apps or use an exception without a new specific review. |

## Security decisions and open gates

- Payloads remain allow-listed declarative LevelData, supply plans and metadata. Executable/interpreted code, plugins, modules, autoloads, evaluator expressions and remotely activated features are denied.
- HTTPS is required for any future remote content transport. Transport security does not replace schema, digest, rollback and authenticity verification.
- SHA-256 detects accidental or unauthorized byte mismatch only when the expected digest is itself trusted. A publisher signature/keyed trust root would strengthen authenticity, but introducing key custody, rotation, client verification or signing changes requires a separate owner decision and security review; this recheck does not invent or install a signing system.
- No publishing secret is permitted in app bundles, source, manifests, logs or player data. No telemetry/privacy approval is inferred; the existing offline/no-telemetry default remains.
- Store policy freshness was checked for SB-CP09-001/002. Final platform policy review, app-specific assessment, independent security audit and any store submission remain open owner/reviewer gates.
