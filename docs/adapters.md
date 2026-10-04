# Optional editor and provider setup

`AGENTS.md` is the canonical project instruction file. `CLAUDE.md` contains only
`@AGENTS.md`, using Claude Code's file import rather than a Windows symlink.
Codex reads scoped AGENTS.md files; other assistants can be given the same file
manually. Check each editor's actual instruction loading behavior.

## Claude Desktop

Desktop Chat and Desktop Code are different workflows. In Desktop Chat, provide
a curated context packet: current AGENTS.md, task, relevant source excerpts and
redacted evidence summary. Uploaded files are snapshots and do not automatically
track repository changes. Do not promise filesystem execution or automatic
AGENTS.md loading unless the user has configured an appropriate tool connection.
Desktop's Code tab uses the Claude Code engine and can use the repository
workflow; see the [official Desktop guide](https://code.claude.com/docs/en/desktop).

No supported Claude history connector was available during this implementation.
Project notes on disk can be inspected with explicit scope, but private app
databases, credential stores and session internals are outside this workflow.
An optional later handoff can be curated using
[Claude's own chat search](https://support.claude.com/en/articles/11817273-use-claude-s-chat-search-and-memory-to-build-on-previous-context):
ask for decisions, constraints, failed approaches, unresolved questions and
source chat links for this modding project. Reconcile that historical summary
with current source/evidence before using it. Keep raw exports outside public
repos. An [account export](https://support.claude.com/en/articles/9450526-export-your-claude-data)
is optional and user-driven; selected excerpts are usually easier to review.
No export, authentication flow, public chat link or MCP setup is triggered here.

## Filesystem agents and optional clients

The [Codex guide](https://developers.openai.com/codex/guides/agents-md) and
[Claude Code memory guide](https://code.claude.com/docs/en/memory) describe their
native loading rules. Avoid independent copies that drift. Keep stable rules
compact; put active task and evidence in ordinary ignored files. Inspect current
source state before trusting a stale plan or a summarized conversation.

GPT, Claude, Codex and other model names do not change the workbench interface.
The operator's own editor/client handles providers, credentials, rate limits
and billing. This repository contains no provider configuration or secrets and
does not invoke an agent automatically.

For a client using OpenRouter, follow the
[official quickstart](https://openrouter.ai/docs/quickstart) and
[provider logging guidance](https://openrouter.ai/docs/guides/privacy/provider-logging).
Keep keys in the client's environment/secret store, never this repository.
Model/tool capabilities and provider privacy differ; choosing a routing service
does not establish equivalent behavior or confidentiality. No workbench feature
requires it. Review what source/log context your client sends before enabling it.

Unity/Blender/Wwise bridges are optional future manual integrations. A bridge
reporting "connected" may only prove its server starts; make a harmless read of
the intended live project to verify access. Tools executing code inside an
editor have user-level filesystem access and should follow the same ownership
and authorization rules as a shell. No bridge configuration is generated here.
