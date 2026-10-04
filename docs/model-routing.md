# Outcome per token and model effort

Use deterministic tools to establish facts, then choose the least expensive
capable reasoning tier for the remaining uncertainty. These are roles/effort
levels, not a vendor model ranking or a promise of equal capabilities. The
operator selects an available model in their own client; workbench never routes
paid calls, buys tools or uploads context.

| Tier/role | Appropriate task | Packet and limit | Escalate when |
|---|---|---|---|
| Deterministic tools | Inventory, exact versions, hashes, ZIP parity, current assertions | CLI/check results and targeted Git/search output | A concrete fact remains unresolved; never ask a model to invent it |
| Bounded helper | Find a symbol, classify a short log, draft one checklist or translate reviewed text | One question, exact files/excerpts, fixed output format; no shared-file writing | One attempt cannot substantiate the answer, or a safety/API assumption is required |
| Standard implementer | One skill/component, check fixture or focused docs change | Current task, owned paths, acceptance, relevant source and baseline evidence | New cross-component ownership, repeated semantic failures or unclear native behavior |
| Deep reviewer/architect | Authority/lifecycle/security, shared schema, licensing-sensitive adaptation, difficult regression | Small reviewed diff, exact failed case, primary-source API facts and competing hypotheses | A native/controller/network experiment is needed; reasoning alone cannot certify it |
| Human/native acceptance | Physical input feel, real host/client, art readability and rights judgment | Bounded acceptance matrix plus exact build/package identities | Unknown scope, user authorization or physical observation is required |

For example, a cheap helper can locate a version constant, but a deterministic
parity check should establish its value. A standard implementer can add one
guard regression. A deep reviewer is justified for projectile authority and
cleanup, not for restating README text. Keep physical/controller/network
acceptance separate from every model tier.

## A compact current packet

```console
python -m ror2_workbench packet --root PROJECT --max-bytes 12000
```

The packet contains the current task, declared input hashes, observed Git
identity and a context fingerprint. It carries no source dump or raw logs and
fails rather than silently truncating requirements when the **actual UTF-8 byte
budget** is exceeded. Bytes are not tokens. Feed it with only the relevant
source/diff excerpts to your chosen agent. In Desktop Chat, attach/refresh the
curated packet manually; in a filesystem agent, read it from the repository.

Stable fingerprint means the **declared inputs/task/tool/Git identity** match.
It does not certify an external game/editor environment or every source file.
Add all relevant source files and a locally recorded environment/dependency
identity to `inputs`. Invalidate summaries, cached reasoning and passing
evidence when those inputs change. Do not reuse an old check merely because
its filename says "passed". Stable invariants belong in AGENTS.md; current
status belongs in the task, not an ever-growing instruction diary.

Before spending model context: inspect actual HEAD and diff, list the scoped
files, run existing checks, and search exact symbols. Git/search/CLI hashes cost
no model inference and avoid re-deriving the same environment. Prefer targeted
queries to dumping entire repositories, every log or all historical chats.
Keep a short dependency/source index with links/revisions rather than copied
frameworks. A failed evidence receipt is useful input to the next task.

## Bounded worker packet template

```text
Task: <id and one concrete outcome>
Current base/fingerprint: <observed values; unknown stays unknown>
Own: <exact paths>; shared changes go to <integrator>
Read: <small relevant files/symbols and current baseline receipt>
Acceptance: <named assertions and required evidence levels>
Budget: <one focused attempt/check cycle; agreed wall-time window>
Stop: <handoff after checks; escalate on the stated failure/risk>
Return: changed files, actual results, exact artifacts, unverified work, next action
```

After one failed focused attempt, use the concrete failure to narrow or escalate.
A second attempt is justified by a new hypothesis/input, not the same unchanged
prompt. Review a deep model's output before delegating implementation again.
Do not poll indefinitely, replay successful unchanged builds, or launch a large
native campaign when the user owns playtesting. One coordinator maintains the
current task and integrates bounded handoffs; it should return completed work
and current evidence, not an obsolete plan.

## Measure the outcome honestly

Record task start/end or elapsed seconds, checks actually run, failed attempts,
rework, artifact identities and acceptance reached. Optional client-reported
token/cost/model metadata can be added to a private task ledger **only when
measured and available**. This v0.1 does not claim token savings, fetch usage or
estimate prices. Compare repeated tasks by achieved acceptance and rework;
cheaper inference that increases debugging can be a worse outcome.

The testable reductions in repeated work here are deterministic preflight,
explicit current input identity, bounded context packets, fresh-output receipts
and exact package parity. Runtime provenance, token metering and automated
model choice are roadmap work, not implemented features.

## Adopt existing tools before expanding this layer

| Existing tool/project | Use/defer decision |
|---|---|
| Git + available text search | Use for exact source/diff/symbol facts; no new search service required |
| BepInEx + split [R2API](https://github.com/risk-of-thunder/R2API) | Use as the game integration layer; do not invent a loader/content framework |
| [HenryTutorial](https://github.com/ArcPh1r3/HenryTutorial) / character wiki | Consult survivor prior art; defer code copying until rights and current APIs are verified |
| [ThunderKit](https://github.com/PassivePicasso/ThunderKit) | Optional custom-asset lane; defer mandatory installation/editor coupling |
| [BepInExTemplate](https://github.com/Dnarok/BepInExTemplate) / Thunderstore CLI | Existing general scaffolding/packaging options; do not duplicate their entire workflow or vendor unverified licenses |
| AH64/Hollow offline checks | Run/adapt within their licensed source projects when appropriate; transfer the evidence pattern, not hero-specific code |
| Optional editor MCP/agent tools | Use only when a measured gap warrants setup and authorization; a connection status is not proof of live project access |

No missing plugin, toolchain download, subscription or public service blocks
the local v0.1. Broad interest in tooling is not blanket installation/payment/
sharing permission. Bring a concrete benefit, source/license and bounded
validation plan to the maintainer before adding one.
