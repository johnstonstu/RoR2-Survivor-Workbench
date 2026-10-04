# Product decision and ownership

v0.1 is a workflow plus a small CLI. It can sit beside any survivor framework,
editor or agent without owning the game loop. The useful first slice is:

`project contract → metadata preflight → pinned allowlist → exact ZIP → receipt`

The CLI uses Python 3.11 standard-library APIs. JSON contracts contain data;
there is no shell expansion, plugin execution, provider SDK or all-purpose
orchestrator. Explicit relative paths replace environment discovery. Outputs
are new files, input/ZIP limits are bounded, and archives are never extracted.
Deterministic ZIP timestamps make identical pinned inputs produce identical
archive hashes. UTF-8 and UTF-16-LE scanning is a basic guard, with known limits.

| Area | Owner | Boundary |
|---|---|---|
| `ror2_workbench/core.py`, `contract.py`, `__main__.py` | Integrator | Shared schema, path rules and command behavior |
| `release.py` | Release-check contributor | Allowlist, PNG checks, byte parity |
| `evidence.py` | Evidence contributor | Result identity and evidence levels |
| `starter.py` | Scaffold contributor | Original generic generated files |
| `docs/`, `tests/`, `scripts/` | Assigned focused contributor | No concurrent writers on one file |
| Game/profile/editor resources | Runtime integrator | Outside v0.1; one shared serial lease |

This initial implementation used one writer, preventing schema/file collisions.
Future task assignments should retain this layout or agree on another explicit
ownership contract. Worktree isolation is source isolation, not runtime isolation.

## Next small increments

1. **Build provenance:** the first-survivor fixed adapter now captures its exact
   declared source/lock and output hashes, with no post-build profile copy.
   General project adapters, whole-tree provenance and DLL metadata remain next.
   Do not read arbitrary command strings from manifests.
2. **Runtime access:** compare member references against legally installed real
   game assemblies using a separately reviewed .NET tool. Publicized refs prove
   signatures, not native accessibility. Existing project checks can be invoked
   manually now; no such scanner is implemented here.
3. **Asset provenance:** Unity project version checks and source-tree → bundle
   receipts; Wwise source/version/bank validation without `Init.bnk`. Hash pins
   alone do not establish source freshness or bank compatibility.
4. **Safe staging:** synthetic filesystem tests first, then one marked
   disposable profile with explicit authorization, shared atomic lease, backup,
   hashes and rollback. Avoid broad all-profile deploy and fixed-profile deletion.
5. **Acceptance integrations:** bounded solo semantics/capture; separate physical
   controller and actual host/client playtests; measured visual review. A human
   can supply appropriately labeled receipts today.
6. **Optional survivor lane:** an original native body with stock skills and
   locked references is now compile-verified. Native acceptance and one custom
   state follow. Custom Unity/ThunderKit models and sound come after that loop.

A full runtime automation framework, mandatory editor plugin, AI orchestration
and cloud accounts are outside this product. Add an integration only when its
benefit can be demonstrated with a bounded failure and reviewable evidence.
