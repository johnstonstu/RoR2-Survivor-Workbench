# First survivor: Workbench Recruit

This original asset-free learning example closes the build/adoption gap. It
constructs a new survivor/body/master/display through a native content provider,
clones stock Commando prefabs at runtime, and retains native Commando skills,
movement, input and camera. It does not copy HenryTutorial, export game assets,
require a Unity project or install itself into any profile.

The source **compiled successfully** against the exact locked reference graph
with the installed .NET 10.0.302 SDK. Native game access, prefab resolution,
catalog selection, skin/loadout presentation, controller and host/client
acceptance remain pending. This is a build-verified recipe, not a tested release.
The current build retains one NU1701 warning: MMHOOK.RoR2's .NET Framework
target differs from netstandard2.1. No suppression or runtime waiver applies;
the build has zero errors.
`BUILD-VERIFICATION.json` is the reviewed compile summary. Identical DLL bytes
across checkout locations remain unverified; always bind your own artifact hash
to your build and package receipts.

## Build in the first session

Prerequisites: existing Python 3.11+ and a .NET SDK supporting netstandard2.1.
The validated SDK was 10.0.302; other SDKs need their own build receipt. From
the workbench repository root, run the explicit fixed build-only adapter:

```console
python scripts/build_first_survivor.py
```

That explicit command restores only the locked graph through the configured
official NuGet/BepInEx registries, then builds. It downloads dependency packages
when missing, **not tools**; use it only when that restore is authorized. To use
an existing local hierarchical NuGet feed/cache without networking:

```console
python scripts/build_first_survivor.py --offline-feed EXISTING_NUGET_CACHE
```

The implementation validation used this offline lane. SDK homes, package/http/
plugin caches and Windows application-data locations are isolated under root
`local/first-survivor-sdk/`, preventing a Windows restore from reading personal
NuGet settings. Telemetry, certificate generation and shared build servers are
disabled. Commands are fixed and bounded to 60 seconds each. No post-build or
profile deployment target exists. NuGet advisory lookup is disabled for this
bounded restore and is explicitly recorded as unrun, not a security pass.

The script seeds `local/task.json` once from `task.template.json`, never replaces
an active task, and writes new private build receipts/logs. It records exact
source/lock hashes, SDK command output, exit codes, elapsed seconds, warning/error
totals and the produced DLL's SHA256. Inspect the complete sanitized logs and
receipt; raw logs stay ignored. No generic task acceptance is silently marked done.

## Verify the package inputs

The committed `workbench.json` has complete package mappings and deliberately
null artifact pins. After reviewing the build/rights and package metadata:

```console
python -m ror2_workbench check --root examples/first-survivor
python -m ror2_workbench pin --root examples/first-survivor
```

Review `examples/first-survivor/local/workbench.pinned.json` and consciously adopt
it as `workbench.json`. It will become a local change. Then:

```console
python -m ror2_workbench check --root examples/first-survivor --release
python -m ror2_workbench package --root examples/first-survivor --output dist/review.zip --receipt local/package.json
python -m ror2_workbench verify --root examples/first-survivor dist/review.zip --receipt local/verify.json
```

Only original plugin/metadata/license bytes ship. NuGet/game/framework DLLs,
Unity packages, PDBs, extracted models/textures and any initialization bank are
outside the allowlist. A matching ZIP is still not runtime acceptance.

## Exact dependency baseline and rights

`Mod/FirstSurvivor.csproj` uses exact bracketed package versions.
`Mod/packages.lock.json` pins the resolved transitive graph and content hashes;
the build adapter uses `--locked-mode`. The deliberate cached compile baseline
is not a claim of being the newest runtime ecosystem:

| Reference | Version | Role/rights |
|---|---|---|
| BepInEx.Core | 5.4.21 | MIT metadata verified in package; external compile dependency |
| R2API.Core | 5.3.0 | MIT upstream; external dependency |
| R2API.Prefab | 1.1.1 | MIT upstream; native clone/network helper |
| R2API.Language | 1.1.0 | MIT upstream; name/description tokens |
| R2API.ContentManagement | 1.0.10 | MIT upstream; Prefab dependency, older than current 1.0.11 |
| RiskOfRain2.GameLibs | 1.4.1-r.0 | Proprietary publicized references; compile locally, never redistribute |
| MMHOOK.RoR2 | 2025.12.9 | External generated hooks; not shipped |
| RoR2BepInExPack | 1.41.0 | External compatibility reference, older than current runtime releases |
| UnityEngine.Modules | 2021.3.33 | External engine references; never redistribute |

BepInEx's [NuGet core](https://github.com/BepInEx/BepInEx) version differs from
the [Thunderstore BepInExPack](https://thunderstore.io/c/riskofrain2/p/bbepis/BepInExPack/)
version 5.4.2122. Runtime module dependency strings are recorded separately in
`Package/manifest.json`; verify the installed dependency set during native
acceptance. [Prefab documentation](https://thunderstore.io/c/riskofrain2/p/RiskofThunder/R2API_Prefab/)
confirms InstantiateClone's internal network registration, so no second explicit
registration call is made. The current
[ContentManagement changelog](https://thunderstore.io/c/riskofrain2/p/RiskofThunder/R2API_ContentManagement/)
records 1.0.10 and the newer 1.0.11. [R2API's pinned MIT license](https://github.com/risk-of-thunder/R2API/blob/fcb5752f7f3c4225a82934933183e63bf371c04a/LICENSE)
was inspected. No R2API implementation is vendored. Original example code and
plain placeholder icon use the workbench MIT contributor license.

## Before extending or playing it

1. Review the exact build output/logs, package parity and native member-access gate.
2. Obtain the separately bounded runtime window and one disposable profile owned
   by the runtime integrator. Test the exact ZIP with matching dependencies.
3. Verify selection/display, all native slots, held/re-press, movement/camera,
   stock loadout/skins and death/respawn. Missing native prefabs fail explicitly
   during content construction; compile success cannot establish their lookup.
4. Perform physical controller and actual host/client acceptance separately.
5. Only then replace one skill or add custom art. Give a state clear authority,
   interruption/cleanup and current semantic assertions; keep the native baseline.

Public versioned media, browser checks and version-specific publication approval
remain required for any later release. No part of this recipe grants those actions.
