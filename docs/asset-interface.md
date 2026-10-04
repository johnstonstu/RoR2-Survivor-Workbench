# A small asset/code handoff

Agree on one concrete action before different contributors author its code,
animation and effects. This checklist is a manual interface agreement, not a
new workbench schema or automatic Unity validator. Add the agreed document and
actual source/output identities to the project's declared inputs.

| Agreement | Record before authoring |
|---|---|
| Ownership | One integrator for controller, generated bundle/bank and package map; disjoint source paths for contributors |
| Identity | Exact case-sensitive asset, clip, state, layer, parameter and socket names that the loader/code expects |
| Spatial basis | Export/import axes, units, pivot, rig revision, attachment transform and intended scale; verify one round trip |
| Transform ownership | Animator layer/mask and any procedural writer; one owner per transform; native motor owns movement |
| Timing | Start/hold/release/end, loop policy, gameplay event timing and attack-speed scaling; do not rely on an artist's preview duration |
| Exit/reset | Normal completion, early release, interruption, death, unequip and scene change; recovery state and cleanup owner |
| Failure | Required gameplay content fails clearly during construction; optional cosmetics fail without preventing the skill |
| Evidence | Source and generated-output hashes, declared checks, exact capture purpose and remaining native gates |

For a synthetic example, agree on `ChargeStart`, `ChargeHold` and `ChargeEnd`
before authoring. Specify whether the hold loops, which layer/mask plays it,
which socket supplies the effect origin, when gameplay releases, and how an
interruption returns to the native locomotion pose. Code and asset writers
must reconcile those names/times with the imported controller rather than
independently guessing. Placeholder animation names remain unverified until
the importer, controller and runtime call sites agree.

Review the smallest loop from the **normal gameplay camera**: starting, holding,
releasing and recovering while standing, moving and aiming up/down. Record
whether the hand/prop silhouette, charge growth and release direction are
visible with the normal HUD and body occlusion. A front turntable or isolated
editor render answers a different question. Do not alter native camera/input
settings to manufacture a favorable acceptance view. Keep captures bounded
and distinguish offline preview from observed gameplay.

If an optional editor bridge is used later, perform a harmless read that names
the intended live project/scene and instance before issuing a mutation. Resolve
a mismatch with the tool owner instead of starting duplicate servers or
inventing a router. This document configures no bridge, installs nothing and
grants no editor/runtime authorization.

The inspected [released animation plan](https://github.com/johnstonstu/ror2-hollow-saint/blob/20a821abb9f0f254d966536da82052007e734c1e/docs/animation-plan.md)
describes a tiny clip import before the larger pipeline and layered gestures.
[Published playtest notes](https://github.com/johnstonstu/ror2-hollow-saint/blob/20a821abb9f0f254d966536da82052007e734c1e/docs/dev/PLAYTEST.md)
separate normal-camera readability checks from preview evidence. These are
source-grounded workflow examples; their recorded runs were not repeated here.
