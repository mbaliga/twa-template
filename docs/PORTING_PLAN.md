# twa-template — multi-platform porting plan

> Part of the constellation-wide porting program (`Personal-Tracker/PORTING_PROGRAM.md`, 2026-10-06).
> Status: **PLAN — nothing in this document has been built.** Every claim about a target platform is labelled with its
> evidence class (§0). Index-style plan, tier C: this repo is Android packaging, so each non-Android target is a reframe
> into that platform's own "wrap a PWA" artefact, never a port of code. Owned by the lead planning session; a platform
> track updates only its own §4 row. This file never writes a token in its double-brace form (§3).

## 0. Evidence labels (the master §2 set; this plan uses the subset below, verbatim)

`PLAN` (this document) · `CI (hosted VM) evidence` · `SIMULATOR` · `CI-APPROX — NOT DEVICE EVIDENCE` ·
`NEEDS-DEVICE-VALIDATION` (NDV) · `NEEDS-OWNER-VALIDATION` (NOV) · `NOT-APPLICABLE` (with reason) · `CONTAINER-BUILD-ONLY`.

## 1. What this repo is, in porting terms

- **Product.** The public Android Trusted Web Activity (TWA) scaffold that `play-publisher`
  (`asystemofcells-figma/packages/play-publisher`) is meant to clone per user, token-substitute and commit to the user's
  own repo, where `build.yml` builds an APK/AAB around their PWA. State `seeded` (`README.md` line 7; PR #1 merged
  2026-07-02; registry `Personal-Tracker/CONSTELLATION.md` §3). `README.md` is the only document (no CLAUDE.md, STATE or
  roadmap). The one consumer is a 36-line stub, no clone or substitution code (read 2026-10-06). Target: Android only.
- **Stack.** Groovy Gradle DSL (build files only), Android XML, JSON, Python 3 stdlib, GitHub Actions YAML. No Kotlin/Java,
  no native code: the UI is the user's PWA, rendered by Chrome via androidbrowserhelper 2.5.0's `LauncherActivity`.
  Gradle 8.9, AGP 8.5.2, JDK 17. Not a Hyle or KMP consumer, so the toolchain-pin question (OQ-17) does not touch it.
- **Size** (measured 2026-10-06): 22 files, 774 lines, 0 tests: `git ls-files | grep -v -e '^gradlew' -e 'wrapper.jar' | xargs wc -l`.

## 2. Portable core vs platform-bound layers

| Module / dir | Role | Portability | Approx LOC | Notes |
|---|---|---|---|---|
| `app/` + Gradle root | Android TWA shell: manifest, resources, signing config, wrapper | android-bound | 217 + 34 | No code; a port is a parallel per-platform shell, not a translation |
| `scripts/instantiate.py` | Executable contract: 14-token `CONTRACT`, `SAMPLE`, fail-loud substitution | portable (stdlib) | 97 | Scope is `TARGET_DIRS` (`app`, `.well-known`) + `twa-manifest.json`; other directories keep their tokens |
| `twa-manifest.json` | Bubblewrap source of truth | other | 40 | Android schema, but its fields (host, start URL, names, colours, icon, version) are what any web wrapper needs |
| `.well-known/assetlinks.json` | Asset Links statement the user publishes on their site | android-bound | 11 | Analogues: apple-app-site-association (iOS), windows-app-web-link (Windows); none on UT or Linux |
| `.github/workflows/` | `build.yml` (ships to user repos), `template-smoke.yml` (this repo's gate), `cleanup-artifacts.yml` | other | 221 | `build.yml` guard greps only `app/` and `twa-manifest.json`; every job is `ubuntu-latest` |

Platform-bound APIs that matter: the **TWA `LauncherActivity`** (`app/src/main/AndroidManifest.xml`) is the whole runtime and
exists only with Chrome on Android, so each target needs a different wrapper; **Digital Asset Links** is an Android-only trust
triangle, so other platforms need their own identity values (new tokens) or have none; **icons, shortcuts, FileProvider**
(`res/`) are Android formats, and README flow step 2 (generate icons from the icon URL) is specified but implemented nowhere.

## 3. Binding rules this port must not break

- Token names are `play-publisher`'s contract; `CONTRACT` in `instantiate.py` is canonical (`README.md` "Do not touch";
  Personal-Tracker D-M). New tokens go into plugin, script and README table in one change; none is renamed or removed.
  The Asset Links triangle changes in lockstep; `VERSION_CODE` stays unquoted; dependencies stay minimal.
- A new token-bearing directory must be added to `TARGET_DIRS` (see §2) and covered by a placeholder guard, either
  `build.yml`'s grep (today `app/` and `twa-manifest.json` only; it ships into user repos) or the new platform workflow's own
  guard; `build.yml` itself is not edited by a port (R3). Each new workflow says whether it ships (`README.md`).
- No keys, secrets, payment forms or ads in the template; signing lives in the user's CI secrets (`README.md`).
  asystemofcells-figma rule 5: Apple and Microsoft signing material never passes through the plugin.
- No telemetry or analytics SDK in any wrapper on any platform. Colour never carries meaning alone: the scaffold has no UI
  of its own, and any status a port adds is a word and a shape. Environment honesty: this container has no UT device,
  Clickable run, Xcode or Windows host, so every wrapper is `CI (hosted VM) evidence` at best and device behaviour is NDV/NOV.
  A reframe is never called a port (R12).
- D-I: no LICENSE here (`CONSTELLATION.md` §2, `STATE.md`); vendoring third-party templates waits on it. D-K: structural
  changes are PRs. Canonical path `mbaliga/twa-template`, never the org URL. The repo must stay usable as a GitHub
  template repository (owner action still open in `STATE.md`).
- Program R1-R3, R5, R6: disjoint directories, existing gate green, new workflow files only, nothing signed or stored;
  `template-smoke.yml`'s sample-APK upload and `cleanup-artifacts.yml` stay untouched.

## 4. Target matrix (owner's order)

| Target | Feasibility | Approach | Blockers | Effort (eng-weeks, estimate) | Evidence today |
|---|---|---|---|---|---|
| Ubuntu Touch | reframe | Nearest shape: a Lomiri web-app Click. A few token-substituted text files (manifest, `.desktop` running `webapp-container` with URL patterns confined to the host, AppArmor profile with `networking` + `webview`, icon), architecture `all`, built by Clickable in a CI Docker job. Waydroid (OQ-21) is the program's alternative; whether a TWA APK runs there is unknown | OQ-19; no UT device (OQ-1); Click name rules need a derived or new token; icon generator absent; 24.04-1.x webapps run Chromium 87 and 24.04-2.x Chromium 134, so declare a minimum; OpenStore publishing is outside the plugin stub | 1.5 | PLAN |
| Linux desktop | reframe | Nearest shape: a launcher, not an app. `.desktop` + hicolor icons + install script running `chromium --app=<start URL>`; needs an installed Chromium, no store listing. Heavier option, the owner's call: a Tauri window with a host allowlist, which would also serve macOS and Windows | Tauri adds Rust (sibling template, not this repo); WebKitGTK vs Chrome rendering unknown; no ownership-verification analogue; Flatpak/AppImage/deb choice (OQ-4) | 1.5 | PLAN |
| iOS / iPadOS | hard | WKWebView wrapper (PWABuilder's open iOS template is the reference shape): generated plist, settings, entitlements and apple-app-site-association, built on a macOS runner with the user's own certificates. **Recommend deferring.** Honest alternative: Safari Add to Home Screen needs no wrapper | App Review 4.2 routinely rejects thin wrappers, per end user; Apple Developer Program per user (OQ-2); secrets never via plugin; macOS runner minutes; new identity tokens; no Xcode here | 4 | PLAN |
| macOS | reframe | Today's answer: Safari 17+ Add to Dock installs a PWA with no artefact. An optional `.app` wrapper would reuse the Tauri scaffold (WKWebView); signing and notarisation exist only as disabled templates (R6) | Per-user Developer ID and notarisation secrets (OQ-3); no Mac on record (OQ-5), so device gates are NOV; Mac App Store carries the 4.2 risk | 1 | PLAN |
| Windows | reframe | Nearest shape: the MSIX hosted PWA (PWABuilder's Windows package): a generated AppxManifest + asset folder that registers the PWA with Edge, no WebView code. Built on `windows-2025` with PWABuilder's CLI or makeappx; the Store re-signs MSIX, so Store distribution needs no certificate secret | Partner Center account per user (fee status: `porting/platforms/windows.md` item 14, verify at use); publisher and package-identity values become new tokens; icon asset set; MSIX tooling is Windows-only | 1.5 | PLAN |

Estimates are master §5's, not additive (icon generator and contract extension are shared, §6), and exclude store
automation in the plugin. The profile sized a thin `.desktop` alone near 0.5 week and the Tauri variant at 1.5; OQ-19 settles which.

## 5. Tier and sequencing

**Tier C** (thin or reframe), per master §5: no application to port, only packaging and a 97-line substitution script, and
all value is downstream of `play-publisher` becoming real. Master §7 lists no twa-template deliverable in any wave, so nothing
is scheduled; the table says which wave each row would join if OQ-19 is ruled yes. Gates for every row: the consumer stub
grows a real cloner; `docs/` joins the plugin's carry-over exclusion list (today only `template-smoke.yml` is named, in
prose); `template-smoke.yml` stays green (R2).

| Target | Wave it would join | Extra gate before it starts |
|---|---|---|
| Ubuntu Touch | P-UT a (web clicks) | F7's webapp template exists, else this repo builds a second one; OQ-1 or a written CI-only waiver |
| Linux desktop | P-LX | If Tauri: after the Tauri lane's pilot (F10) |
| iOS / iPadOS | P-iOS, last | OQ-2 plus a written acceptance of the 4.2 risk; otherwise `NOT-APPLICABLE` by decision |
| macOS | P-mac | Linux-side scaffold if a wrapper is wanted; OQ-3; device gates wait on OQ-5 |
| Windows | P-win | OQ-3 route; the R3 path lint. Proposal, not a ruling: needs no wrapper engine, so it could be built before Linux and macOS (§8 Q9) |

## 6. Work breakdown

**Placement (OQ-19).** Option S, proposed default: sibling template repos (working names `click-webapp-template`,
`pwa-desktop-template`, `pwa-windows-template`; unregistered, so R11 applies), leaving this repo with only this plan.
Option I: `ubuntu-touch/`, `packaging/linux/`, `packaging/windows/`, `apple/` here, each with its own new workflow and
placeholder guard (so `build.yml` is not edited, R3), plus one edit to existing code, `TARGET_DIRS`, under D-M lockstep.

| Step | Work and placement (`<dir>` is the chosen directory) | Done-when | Verifiable in this container? |
|---|---|---|---|
| S-0 | Owner rules OQ-19; recorded as a Personal-Tracker DECISIONS entry (proposed, id owner-assigned) | Ruling written | n/a |
| S-1 | If a target needs identity values: working tokens for Click name, MSIX publisher/identity, Apple team, added to plugin, `CONTRACT` and README together, after NAMES.md rows (R11) | `--sample` reports 0 tokens left; smoke green | No; `CI (hosted VM) evidence` |
| S-2 | Icon generator from the three icon URLs into per-platform sets; home unresolved (§7) | Sets emitted from the sample icon in CI; the look is NOV | No |
| UT-1 | `<ubuntu-touch>/`: manifest, `.desktop`, AppArmor, icon (hosted URL only, no bundled server, minimum OS stated) + `ubuntu-touch.yml`: placeholder guard, instantiate, Clickable build in F7/F9's digest-pinned image, click lint, no upload (R6) | Generates with 0 tokens left; green run, `CI (hosted VM) evidence` | Files only; no Clickable run |
| LX-1 | `<linux>/`: `.desktop`, icons, install script, README saying "desktop launcher, needs Chromium" (R12) + `desktop-linux.yml`: `desktop-file-validate`, tarball, compile-only on PRs. Tauri variant only on the owner's word | Green run, `CI (hosted VM) evidence` | Files only |
| WIN-1 | `<windows>/`: AppxManifest template + asset folder (the user publishes their own windows-app-web-link) + `windows-msix.yml` on `windows-2025`, R3 path lint on ubuntu first, unsigned, nothing stored | Pack succeeds, `CI (hosted VM) evidence` | Files only |
| MAC-1 | Document Add to Dock in the per-platform README; wrapper only after LX-1 and a Tauri ruling | Docs only | n/a |
| IOS-0 | Decision record (OQ-2, 4.2). If yes: generator emits an Xcode project and association file, `macos-latest` compile-only, signing off | NOV; nothing runs here | No |
| DEV | Owner installs on a UT device, the Steam Deck, the Dell while it is Windows; Partner Center and OpenStore submission are the user's steps | NDV (UT, Linux), NOV (Windows) | No |

## 7. Shared foundation this repo consumes or provides

- **Consumes.** F7: its shared webapp-container template should be the source of the UT tree, with the contract's tokens as
  the delta, so the constellation holds one webapp template, not two (OQ-24 picks the sharing mechanism; a generator
  emitting into the consumer is the program's default). F9, F10: SHA-pinned workflow conventions, the R3 path lint,
  Clickable and MSIX/XcodeGen conventions. F11: evidence record and device checklists. F12: the PWA manifest and icon
  family these tokens mirror. None of F1-F6 or F8 (no Kotlin, Hyle or native code).
- **Gap.** The master has no F-item for an icon generator; F12 is nearest. A proposal for the owner, not ruled.
- **Provides.** The token schema and `instantiate.py` as reference substitutor (D-M), reusable by F7/F10 generators; nothing
  for non-Android targets today. Per platform the plugin would need a substitutable tree, an `instantiate.py` scope
  covering it, a workflow shipping into the user repo and a smoke workflow.

## 8. Open questions for the owner

1. **Topology (OQ-19).** Wrappers inside this repo, or sibling templates sharing the contract? Proposed: siblings (Option I
   widens the carry-over surface and cuts against the minimal-dependency rule). Blocks S-0 and all of §4.
2. **Product scope (OQ-19).** Are OpenStore, Microsoft Store and desktop packages in scope for a plugin named and sold as a
   Play publisher; does it get renamed? Blocks the plugin side and any per-platform consumer.
3. **iOS (OQ-2).** Accept the 4.2 risk and per-user Apple cost, or declare iOS out and document Safari Add to Home Screen?
   Blocks IOS-0 onward.
4. **Licence (OQ-12).** Which licence for this public repo (D-I open)? Blocks vendoring PWABuilder or any third-party
   template; until then they are references, not copies.
5. **Template flag.** Is the repo marked a GitHub template repository (open in `STATE.md`; unverifiable from disk)? Blocks
   the "Use this template" path only.
6. **UT device and series (OQ-1).** Which 24.04-x device and series do you have? Blocks the UT device gate; the 1.x vs 2.x
   webapp engine split decides the declared minimum.
7. **Runner budget (OQ-20).** The repo is public so hosted minutes are free, but storage is exhausted and each instantiated
   repo pays its own. Which lanes run here, which are manual dispatch? Blocks the UT, Linux and Windows workflows.
8. **figma-shell.** Is `mbaliga/figma-shell` (empty on disk) the intended non-TWA WebView fallback shell? Blocks nothing now.
9. **Order (R10, OQ-28).** May this repo build Windows before Linux and macOS? Blocks only build order.
10. **Contract extension (D-M, OQ-25).** Approve per-platform tokens (or derived values) and NAMES.md rows? Blocks S-1, UT-1, WIN-1.
11. **Signing and carry-over (OQ-3, OQ-22).** Confirm no signing material passes through the plugin and that `docs/` and
    non-Android trees join its exclusion list; the GitHub template button still copies `docs/`: accept, or move this plan to
    `Personal-Tracker/porting/`? Blocks hygiene only.

## 9. Sources read

This repo: `README.md`, `twa-manifest.json`, `settings.gradle`, `build.gradle`, `gradle.properties`, `app/build.gradle`,
`app/src/main/AndroidManifest.xml`, `app/src/main/res/{values/strings.xml,xml/filepaths.xml,xml/shortcuts.xml}`,
`.well-known/assetlinks.json`, `scripts/instantiate.py`, `.github/workflows/*.yml`, `.gitignore`. Elsewhere:
`Personal-Tracker/{CONSTELLATION,DECISIONS,STATE,PORTING_PROGRAM}.md`, `Personal-Tracker/porting/platforms/{ubuntu-touch,windows}.md`,
`asystemofcells-figma/CLAUDE.md`, `asystemofcells-figma/packages/play-publisher/src/`.

## Owner rulings and the proposed line (added 2026-10-07)

Status: PLAN. Nothing here is built, run on a device, signed or submitted. The program-level plan is Personal-Tracker `PORTING_PROGRAM.md` ([PR #10](https://github.com/mbaliga/Personal-Tracker/pull/10)), which holds the owner's rulings and section 5A, the proposed port / no-port line. The cells, estimates and open questions above are this repo's original plan and are unedited. Where the owner has since answered a question, the answer is below. Section 5A is a proposal; the owner has not yet confirmed it.

### Where twa-template sits in the proposed line (program section 5A.3, a proposal)

| Target       | Verdict | Weeks and flags |
| ------------ | ------- | --------------- |
| Ubuntu Touch | no-port | -               |
| Linux        | no-port | -               |
| iOS/iPadOS   | no-port | -               |
| macOS        | no-port | -               |
| Windows      | no-port | -               |

Key: `follows` means it ports only as far as the products that depend on it; `exists` means the program reads it as already running there, unverified (finish, verify and sign); flags: `g` gated on a prerequisite, `r` re-estimate or floor, `o` its own program, `s` scope note. The program's P4, P8, P12 and P13 gate whole columns or repos and are not flagged per cell. A port verdict counts the deliverable in the line; where this repo's plan calls a deliverable a reframe (program rule R12) it keeps that label. Tests cited in the reason: (a) the owner said it is needed there; (b) its job is really done on that OS by real users; (c) that OS is where it is sold or its audience is; it has no reason to exist if (x) its surface is absent or untouchable, (y) the capability is forbidden or impossible, or (z) the only form is a thin wrapper or a different product nobody asked for. P-numbers and OQ-numbers refer to the program plan (Personal-Tracker `PORTING_PROGRAM.md`, sections 5A.5 and 8).

Reason: A scaffold for Android Trusted Web Activities; its output is the thing that runs elsewhere, not the scaffold.

### Owner rulings that apply here

- None changes this repo's disposition. The program-wide rulings are in Personal-Tracker `PORTING_PROGRAM.md`, section Owner rulings.

### Prerequisites and open questions that touch this repo (program sections 5A.5 and 8)

No program-level prerequisite is named for this repo.

Owner questions in the program register that concern this repo (status as of 2026-10-07):

- OQ-12 (open): Licences for repos without a LICENSE (plan Q4: no LICENSE here; the register names this repo in its older gap list)
- OQ-19 (open): play-publisher scope beyond Android

When the owner confirms or changes the line, this repo's original cells above stay as the engineering detail; only the verdicts and re-costs in program section 5A change.
