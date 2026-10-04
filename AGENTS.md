# Agent contract

This repository is a local workflow/checking tool for survivor developers.
Read README.md, docs/architecture.md, and the current task before editing.
Use docs/model-routing.md: deterministic facts, bounded packets/helpers, standard
implementation and deeper review only when concrete uncertainty warrants it.
Inspect actual HEAD, working changes and current evidence before old plans.

- Keep the core standard-library-only and provider-neutral. Never execute a
  command from JSON, call models, upload, publish, install tools or incur costs.
- One integrator owns shared CLI/schema changes, versions and release artifacts.
  Focused contributors own disjoint files and provide a compact current handoff.
  Do not start agents unless the current request asks for delegation.
- Treat project/profile/editor/runtime resources as shared across worktrees.
  v0.1 has no staging or game launcher. Read docs/runtime.md before adding one.
- Test guards against meaningful synthetic failures in temporary directories.
  Run `python -m unittest discover -s tests -v` and `python scripts/demo.py`.
- Preserve evidence levels: static/offline/build/solo/controller/multiplayer/
  visual/media. Compilation and process exit do not establish runtime acceptance.
- Never copy personal logs, chats, memory, session stores, credentials, local
  machine paths, proprietary assemblies, extracted assets or unlicensed code.
- Update docs when the contract/CLI changes. Generated scaffolds must clearly
  distinguish working tooling from game integration still to be built.

Task metadata describes scope; it does not grant runtime or publication approval.
