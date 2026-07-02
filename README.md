# twa-template

**A minimal, working Trusted Web Activity (TWA) scaffold — the public template the
[A System of Cells](https://mdhv.xyz) `play-publisher` Figma plugin clones, per user, to
wrap a PWA as an installable Android app.**

`state: seeded` · public · canonical path **`mbaliga/twa-template`**
(the deprecated `asystemofcells/twa-template` redirects here) ·
registry: [`Personal-Tracker/CONSTELLATION.md`](https://github.com/mbaliga/Personal-Tracker/blob/main/CONSTELLATION.md)

> This repo is meant to be a **GitHub _template repository_** (Settings → *Template repository* ✓ — owner action).
> `play-publisher` instantiates it by copying the tree, substituting the `{{TOKENS}}` below, and
> committing the result to the end user's own repo, where GitHub Actions builds the APK/AAB.

---

## The instantiation contract

`play-publisher` performs a **literal string substitution** of these tokens across every file in
the tree (they appear in `twa-manifest.json`, `app/build.gradle`, the manifest, and `res/`). The
token names are the contract — **renaming or removing one breaks the plugin's substitution step**
(see *Do not touch*).

| Token | Meaning | Example |
|---|---|---|
| `{{APP_ID}}` | Android `applicationId` / package (also the FileProvider authority prefix) | `xyz.mdhv.myapp` |
| `{{APP_NAME}}` | Full app name (store + launcher label) | `My App` |
| `{{LAUNCHER_NAME}}` | Short home-screen label (≤ 12 chars ideal) | `MyApp` |
| `{{HOST}}` | PWA origin host, no scheme — drives Digital Asset Links + deep links | `app.example.com` |
| `{{START_URL}}` | Full launch URL | `https://app.example.com/` |
| `{{THEME_COLOR}}` | Status-bar / theme color (`#RRGGBB`) | `#0B0B0F` |
| `{{BACKGROUND_COLOR}}` | Splash background (`#RRGGBB`) | `#0B0B0F` |
| `{{NAV_COLOR}}` | Navigation-bar color (`#RRGGBB`) | `#0B0B0F` |
| `{{ICON_URL}}` | 512×512 source icon; instantiation generates adaptive + raster launcher icons from it | `https://app.example.com/icon-512.png` |
| `{{MASKABLE_ICON_URL}}` | Maskable variant (falls back to `{{ICON_URL}}`) | … |
| `{{MONOCHROME_ICON_URL}}` | Monochrome/themed-icon variant (optional) | … |
| `{{VERSION_NAME}}` | Human version | `1.0.0` |
| `{{VERSION_CODE}}` | Integer version code (**unquoted** in `app/build.gradle`) | `1` |
| `{{SHA256_FINGERPRINT}}` | SHA-256 of the signing cert — for `.well-known/assetlinks.json` only | `AB:CD:…:EF` |

**Instantiation flow (what the plugin/CI does):**
1. Copy the tree, substitute the tokens above.
2. Generate launcher icons from `{{ICON_URL}}` (adaptive `mipmap-anydpi-v26` + raster `mipmap-*dpi`
   for API 21–25) — the committed vector `ic_launcher` is a build-safe placeholder until this runs.
3. Commit to the user's repo; GitHub Actions (`.github/workflows/build.yml`) builds the debug APK,
   and a signed AAB once the signing secrets are set.
4. Publish `.well-known/assetlinks.json` (with the real `{{SHA256_FINGERPRINT}}`) at
   `https://{{HOST}}/.well-known/assetlinks.json` so Android verifies ownership and hides the URL bar.

`twa-manifest.json` is the [Bubblewrap](https://github.com/GoogleChromeLabs/bubblewrap) source of
truth — `bubblewrap update` regenerates the Android project from it, so power users can bypass the
plugin and drive it by hand.

---

## Build

```bash
./gradlew :app:assembleDebug     # debug APK, no signing needed
./gradlew :app:bundleRelease     # signed AAB (needs keystore.properties — see Signing)
```

Requires JDK 17 and the Android SDK (`compileSdk 34`, `minSdk 21`). The Gradle wrapper is committed,
so CI and users need no local Gradle install.

### Signing

Release signing reads a **git-ignored** `keystore.properties` at the repo root:

```properties
storeFile=/absolute/path/to/upload.keystore
storePassword=…
keyAlias=…
keyPassword=…
```

In CI, set repo secrets `KEYSTORE_BASE64`, `KEYSTORE_PASSWORD`, `KEY_ALIAS`, `KEY_PASSWORD`; the
release job decodes them and skips itself cleanly if they're absent. **No keys or passwords are ever
committed** — `keystore.properties`, `*.keystore`, `*.jks` are in `.gitignore`.

---

## What's in here

```
twa-manifest.json              Bubblewrap manifest (regeneration source of truth)
settings.gradle · build.gradle · gradle.properties · gradlew(.bat) · gradle/wrapper/
app/
  build.gradle                 AGP 8.5.2 · androidbrowserhelper 2.5.0 · androidx.browser 1.8.0
  proguard-rules.pro
  src/main/
    AndroidManifest.xml        LauncherActivity (TWA) + asset_statements + deep-link filter
    res/values/                strings · colors · styles (framework translucent theme, no AppCompat dep)
    res/drawable/              ic_launcher + splash (vector placeholders, replaced at instantiation)
    res/xml/                   shortcuts · filepaths
.well-known/assetlinks.json    PUBLISH ON THE SITE (not bundled) — proves app↔site ownership
.github/workflows/build.yml    debug APK on push; signed AAB when secrets present
```

---

## Do not touch

- **The `{{TOKEN}}` names are `play-publisher`'s contract.** Renaming/removing one silently breaks
  instantiation. Add new tokens by updating the plugin and the table above in the same change.
- **The Digital Asset Links flow** (`asset_statements` string ↔ `.well-known/assetlinks.json` ↔ the
  `autoVerify` deep-link filter) must stay intact — it is what makes the app a *Trusted* Web Activity
  (no URL bar). Changing the package, host, or fingerprint requires updating all three in lockstep.
- **`{{VERSION_CODE}}` is unquoted** in `app/build.gradle` (Gradle needs an integer literal) — keep it so.
- Keep the dependency surface minimal (`androidx.browser` + `androidbrowserhelper`); the framework
  translucent theme deliberately avoids an AppCompat dependency.

## Brand

Instantiated apps are the user's own; this template itself is published under **A System of Cells**
and links to [mdhv.xyz](https://mdhv.xyz) + Instagram [@asystemofcells](https://instagram.com/asystemofcells).
No payment forms, ads, or secrets live in the template.
