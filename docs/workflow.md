# A bounded development loop

Start with one vanilla-body skill and placeholder art. State exact expected
behavior before implementing: tap, hold, release, re-press, stock/cooldown,
interruption, stun/death, scene change and host/client authority. Add content,
custom movement, art and audio only after the small loop has evidence.

## Coordinate current work

Use one integrator for registrations, config, versions, shared hooks, asset
outputs and package maps. Focused workers get disjoint paths and current base
identity. Give a short handoff with changed files, exact artifact, checks passed,
checks unverified, blockers and next action. The next worker reads actual HEAD,
diff and current task before old plans. Long coordination histories can become
obsolete even when work is already complete.

When the user owns playtesting, use build-only rapid feedback. Do not turn one
skill tweak into a huge unsolicited capture campaign. A capture needs a bounded
purpose, duration and acceptance assertion; successful process exit or a nice
screenshot is not terminal semantic evidence.

## Review implementation ownership

| Domain | Repeatable rule | Acceptance case |
|---|---|---|
| Native input | Use native InputBank/skills; preserve held/re-press behavior, movement and camera | Hold, release, re-press; controller + keyboard; altered bindings |
| Animation | One stable owner per transform; avoid competing Animator/LateUpdate writes | Locomotion/skill/skin transition and reset after interruption |
| Projectiles | Distinguish owning-client requests from server damage/lifetime; validate custom intent and sequence | Remote client's shot reaches server once; foreign/stale messages, disconnect, death, timeout, scene transition |
| Effects | Cosmetic lookup/playback failure must not abort authoritative gameplay | Missing optional effect still fires the skill; review any fallback |
| References | Publicized compile refs are not real method bodies/access rules | Separately scan against real legally installed game assemblies |
| Generated assets | Source identity and matching output identity are both necessary | Stale bundle/bank rejected; expected assets and licenses present |

These are extracted patterns, not drop-in gameplay implementations. API details
and animation/physics results still need current game evidence.

## Integrate one real skill

Treat selection, loadout, spawn and respawn as part of skill registration. A
prefab-time active-skill assignment alone does not establish the family/default
variant that a spawned body resolves. Register the required state/definition/
family through the chosen content integration before its catalogs initialize;
review slot families and defaults against the current game/reference adapter.
Keep cloned-body edits from mutating the stock survivor's shared family. The
native first-survivor example intentionally keeps stock skills, so it does not
demonstrate replacement-family acceptance.

Use an authority map per operation. In the inspected released Hollow skill,
the owning EntityState initiates a ProjectileManager request; direct damage
and replicated meter updates are server work. A universal requirement that
both owning-client authority and server-active be true can exclude a remote
player on both machines. Trace the chosen native helper or custom message
path, then separately assert request count, server hit count and remote visual
presentation. Do not apply that concrete native pattern blindly to a custom
projectile protocol. Compilation or a host-only scenario cannot prove it.

Before parallel art/code work, use the [asset interface checklist](asset-interface.md).
Build one tiny imported action through the intended pipeline before expanding
the clip set. Review normal-camera readability as well as isolated asset views.

## Keep evidence levels separate

- **Static:** metadata, source assertions, licensing declarations and packaging.
- **Offline:** current logic compiled with explicit test doubles; measure semantic
  state transitions and use mutations where useful. Doubles do not prove native APIs.
- **Build:** actual C# compile and warning baseline; record complete log and output hash.
- **Solo:** terminal in-game scenario and full-log review plus current assertions.
- **Controller:** physical device through the user's normal launch/input path;
  do not change bindings or Steam Input mode to mask failures.
- **Multiplayer:** actual host/client acceptance, authority, presentation and cleanup.
- **Visual:** observed render/animation/effect behavior with bounded captures.
- **Media:** public versioned assets and live player-facing browser render.

Classify every native warning/error across the full log. A known baseline issue
needs exact identity and impact, never a broad blanket exception. A successful
launcher with incomplete scenarios is still incomplete. Keep useful failed runs
as regressions. A historical passing assertion may drift from current tuning;
check expectations against current source instead of inheriting old totals.

Compare receipt coverage with every named task gate. A narrow passing receipt
can remain useful while its omitted gates stay pending. Close one phase only
after reviewing its required evidence and the exact artifact pair; retain the
previous pair's rollback identity before moving to the next phase. Do not infer
completion from a list of checks that never included the required scenario.

## Release sequence

Review rights and exact dependencies → build-only outputs → verify generated
assets → pins + allowlisted ZIP → exact ZIP parity → authorized clean-profile
test of that ZIP → controller/network acceptance → public versioned media →
live README browser check → explicit version-specific publication approval.

Contributor setup belongs in root README; skills, controls and player limits
belong in package README. Publish immutable/versioned media first and verify URLs
in the actual player-facing renderer before the ZIP upload. Local Git paths and
GitHub rendering do not prove Thunderstore media works. The workbench does not
fetch media, publish a branch, upload a package or claim browser validation.
