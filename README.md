# RoR2 Survivor Workbench

Local contracts, release checks and honest evidence for building custom **Risk of
Rain 2 survivors** with any editor or AI assistant. Source repository:
[johnstonstu/RoR2-Survivor-Workbench](https://github.com/johnstonstu/RoR2-Survivor-Workbench).
The v0.1.1 core and subsequent local refinements are a workflow starter;
native survivor acceptance remains separate.

The workbench helps a human and focused agents agree on what is current, what
they own and what actually passed. It catches packaging failures before the
expensive game loop. It works without an AI account, game install or Unity.
Its central workflow is [outcome per token](docs/model-routing.md): deterministic
facts first, compact current context, bounded helpers, standard implementation
and deeper review only when the uncertainty warrants it.

## Start in 15 minutes

Use an existing **Python 3.11+** interpreter. No third-party packages, install
step, account, downloads, network calls or provider SDKs are required. Run these
commands from this repository; PowerShell, cmd and POSIX shells are supported.

```console
python -m ror2_workbench --help
python -m unittest discover -s tests -v
python scripts/demo.py
python -m ror2_workbench init local/MySurvivor --name MySurvivor
python -m ror2_workbench check --root local/MySurvivor
python -m ror2_workbench status --root local/MySurvivor
python -m ror2_workbench packet --root local/MySurvivor
```

The demo prints a verified synthetic ZIP receipt inside a temporary directory,
then deletes that temporary fixture. It is **not a mod**. `init` creates a new
asset-free development workspace; it never overwrites an existing directory.
`check` defaults to metadata/task checks and says so in its output. A release
check on this scaffold deliberately fails because no game binaries exist yet.

During minutes 5–15, open the generated `AGENTS.md`, `workbench.json` and
`local/task.json`. Write one skill's expected tap/hold/release behavior, choose
one integrator, and give each contributor disjoint owned paths. For a concrete
first build, use the original [native survivor recipe](examples/first-survivor/README.md)
with locked references, complete package mappings and an opt-in build-only script.
For other frameworks, see [the adoption guide](docs/adoption.md). Feed the contract to Codex,
Claude, GPT, OpenRouter-compatible clients or your editor. The workbench never
calls them.

## Working v0.1

| Command | What it does |
|---|---|
| `init DEST --name NAME` | Creates provider-neutral instructions, task, identity source, package metadata, placeholder icon and runtime policy |
| `check --root PROJECT` | Validates strict schema, source/manifest identity and task consistency |
| `check --root PROJECT --release` | Requires all allowlisted inputs, SHA256 pins, declared provenance and package metadata |
| `pin --root PROJECT` | Writes a new candidate contract with measured hashes for human review; never replaces the active contract |
| `package --root PROJECT --output dist/review.zip --receipt evidence/package.json` | Builds a deterministic ZIP, verifies exact bytes, creates a receipt; no build or deploy |
| `verify --root PROJECT dist/review.zip --receipt evidence/verify.json` | Rechecks an existing ZIP against the current pinned inputs without extraction |
| `identity --root PROJECT` | Prints the exact declared inputs to bind a result record to current bytes |
| `record --root PROJECT local/result.json --receipt evidence/result.json` | Validates operator-supplied results and reports coverage of named task ids/evidence levels |
| `status --root PROJECT` | Prints the active task and declared acceptance states; does not rerun them |
| `packet --root PROJECT --max-bytes 12000` | Creates bounded current context with an input fingerprint; no source/log dump or model call |

Exit codes: `0` means the requested scope passed; `1` means a valid evidence
record contains failed, blocked or unrun checks (receipt still saved); `2`
means invalid input or an operation failed. Every output/receipt is a new file.
Select a new filename for each iteration. Run from the workbench checkout with
`--root` pointing at your survivor repository; no installation is needed.

## What remains manual

The generic `init` C# file is an identity placeholder, not a plugin. The separate
native survivor example is compile-verified with stock skills; game acceptance
is pending. Custom models, network test runners, runtime leases, deployment,
Wwise authoring, provider integration and publishing remain outside this version.
The core checks source version constants; **they do not inspect DLL metadata or
establish build provenance**. The optional fixed build adapter captures its actual
source/lock and resulting DLL identities. Hashes establish byte
identity, not rights, bundle freshness, game behavior or runtime API access.

Declare all relevant source/artifact files in `inputs` and `files`; evidence
identity covers that explicit list, not an automatically discovered source
tree. Logs and human observations are attestations, not independently replayed
tests. Review the full logs and retain failed results. Controller comfort,
multiplayer presentation and live README media require their own acceptance.

## Why this form

The released AH64 and Hollow Saint projects already demonstrate survivor
frameworks, project-specific offline checks, bundle/bank tools and capture
helpers. Their reusable need is coordination plus verifiable release inputs.
The [source notes](docs/sources.md) distinguish inspected tools and recorded
lessons from runtime work not rerun here. We did not vendor their code or
assets. This layer complements BepInEx/R2API and community survivor templates.

- [Adopt an existing/new survivor project](docs/adoption.md)
- [Build the original first survivor example](examples/first-survivor/README.md)
- [Manifest, package and evidence contracts](docs/contracts.md)
- [Development and acceptance workflow](docs/workflow.md)
- [Asset/code names, timing, exits and gameplay-camera handoff](docs/asset-interface.md)
- [Runtime ownership and safe staging design](docs/runtime.md)
- [Provider/editor adapters](docs/adapters.md)
- [Model effort, bounded task packets and stop rules](docs/model-routing.md)
- [Architecture and roadmap](docs/architecture.md)
- [Sources, credits and licensing](docs/sources.md)
- [Validation scope and review corrections](docs/validation.md)

MIT covers original workbench code/docs and placeholders under the collective
RoR2 Survivor Workbench contributor notice. Game, Unity, Wwise and
third-party assets retain their own rights. This is an unofficial community tool.

The Python module `ror2_workbench` and existing receipt identifier
`ror2-agent-workbench` remain stable for compatibility. The repository/display
name does not require renaming an existing local checkout.
