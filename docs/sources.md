# Sources, reusable patterns and licensing

Research snapshot: 2026-10-04. These references explain the product decision;
they are not a promise that any external version remains current. The new CLI,
docs, scaffold, icon and test fixtures were written independently. No survivor
code, private operational log, asset, decompiled game source or template was
copied into this repository.

## Inspected project tooling

Read-only inspection distinguished current worktrees from accepted release
revisions. Public source anchors are AH64 `68fa124` and Hollow Saint
`20a821abb9f0f254d966536da82052007e734c1e`; the latter project's local v09 branch
was not treated as its public main. Recorded claims below are project evidence,
not tests rerun by the workbench author.

| Public anchor | Reusable finding | v0.1 treatment |
|---|---|---|
| [AH64 pack.ps1](https://github.com/johnstonstu/ror2-ah64/blob/68fa124/tools/pack.ps1) | Source/manifest parity, exact input allowlist, bundle freshness check, no Init bank, forward-slash ZIP names | Independent JSON/byte checks; bundle source freshness remains manual |
| [AH64 Stage-Build.ps1](https://github.com/johnstonstu/ror2-ah64/blob/68fa124/tools/dev-profile/Stage-Build.ps1) | Marked disposable target, game closed, canonical exclusive lease, identity/provenance validation before writes | Documented staging design; no staging implementation |
| [AH64 release lessons](https://github.com/johnstonstu/ror2-ah64/blob/68fa124/docs/development/RELEASE-1.3.0-LESSONS.md) | Explicit terminal status, current assertions, classified full logs; source worktrees share runtime resources | Evidence-level validation and focused task contract |
| [AH64 Hellfire check notes](https://github.com/johnstonstu/ror2-ah64/blob/68fa124/tools/HellfireChecks.README.md) | Production logic against explicit doubles; authority/sequence/release/lifecycle checks; runtime remains separate | Generic review patterns; no copied missile logic |
| [Hollow package script](https://github.com/johnstonstu/ror2-hollow-saint/blob/20a821abb9f0f254d966536da82052007e734c1e/tools/release/Make-Package.ps1) | Pinned bundle, literal version, language check, exact ZIP entries and private-path scans | Independent pinning and UTF-8/UTF-16 guard |
| [Hollow controller acceptance](https://github.com/johnstonstu/ror2-hollow-saint/blob/20a821abb9f0f254d966536da82052007e734c1e/docs/controller-acceptance.md) | Physical native-input acceptance distinct from art harness/solo traces | Separate controller evidence level |
| [Hollow shared kit authority](https://github.com/johnstonstu/ror2-hollow-saint/blob/20a821abb9f0f254d966536da82052007e734c1e/HollowSaintMod/FoundationKit/KitShared.cs), [ArcBolt state](https://github.com/johnstonstu/ror2-hollow-saint/blob/20a821abb9f0f254d966536da82052007e734c1e/HollowSaintMod/FoundationKit/ArcBolt/ArcBoltState.cs) | Owning-state projectile request differs from server-only damage/meter work | Explicit operation authority review; no copied implementation or runtime certification |
| [Hollow skill registration](https://github.com/johnstonstu/ror2-hollow-saint/blob/20a821abb9f0f254d966536da82052007e734c1e/HollowSaintMod/KitRegistration.cs) | Registered skill families/variants and slot binding matter beyond a prefab-time active skill | Loadout/spawn/respawn checklist; no generated registration code |

Source licenses inspected: AH64 MIT with separate CC0 audio notices; Hollow
Saint MIT. MIT permits compatible reuse with retained notices, but their
license files do not establish rights to every external game/template dependency.
This version does not adapt code or assets from either. Credits are for prior
work and engineering patterns, not an implied authorship claim on this tool.

Hero-specific helicopter hover, guidance math, spear/halo animations, art, tuning
and large survivor-framework modules stay upstream. The transferable practices
are ownership, native input, authoritative lifecycle, nonfatal cosmetics,
offline/runtime distinctions, release parity and current handoffs.

## Ecosystem primary sources

- [RoR2 character guide](https://risk-of-thunder.github.io/R2Wiki/Mod-Creation/Assets/Character/): survivor ecosystem and template routes; no new framework is needed here.
- [Unity version guide](https://risk-of-thunder.github.io/R2Wiki/Mod-Creation/Unity-Version/): dated engine family information; check actual installed versions.
- [R2API](https://github.com/risk-of-thunder/R2API) and [ExamplePlugin](https://github.com/risk-of-thunder/ExamplePlugin): split modules and example references; resolve a pinned current graph before game work.
- [Thunderstore package requirements](https://wiki.thunderstore.io/mods/creating-a-package): root metadata, PNG dimensions, manifest fields and renderer differences.
- [HenryTutorial](https://github.com/ArcPh1r3/HenryTutorial): useful survivor prior art; no explicit root redistribution license was verified, so no vendoring.
- [ThunderKit](https://github.com/PassivePicasso/ThunderKit): optional editor/toolchain lane, with its own licensing; not included or installed.
- [Community code of conduct](https://github.com/risk-of-thunder/CoC): community context; review asset/code redistribution independently.

## License rationale

MIT is small and compatible with the inspected MIT project tooling and common
contributor workflows. `LICENSE` uses the RoR2 Survivor Workbench collective
contributor notice rather than asserting ownership for an unconfirmed individual
or third party. It covers original project contributions; external dependency/
asset rights still need their own review for any later survivor release.

Generated placeholders carry this original MIT license. New survivor source,
template adaptations, meshes, textures, audio and generated assets need their
own source/revision/license/provenance records. Do not infer rights from public
availability or from AI generation. Do not ship proprietary game assemblies,
Unity packages, Wwise SDK content/Init bank, private paths or credentials.

No external download/install was needed to implement/test this tool. Runtime,
Unity, Wwise, multiplayer and physical-controller validation were deliberately
left to separately authorized work.
