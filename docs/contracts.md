# Contracts and receipts

`workbench.json` schema 1 is strict: unknown/duplicate fields fail, versions are
numeric triples, paths are relative forward-slash names, links/junctions are
rejected, and destination names cannot collide even by case or prefix. Run
`init` to get a complete editable example rather than assembling it from snippets.

| Field | Meaning |
|---|---|
| `mode` | `scaffold` cannot package; `fixture` is synthetic; `mod` requires plugin DLL and dependencies |
| `identity` | Thunderstore package `name` and numeric `version` |
| `plugin` | C# `source` file and literal `version_constant` name |
| `inputs` | Exact files included in evidence identity; explicitly declare all relevant inputs |
| `package` | `manifest`, `readme`, `icon`, `changelog`, `license` source paths |
| `files` | Exact `source` → `destination`, `sha256`, declared `license` and `provenance` for each entry |
| `coordination` | Active `task` JSON and `runtime_policy` document paths |

The five metadata mappings must land at `manifest.json`, `README.md`, `icon.png`,
`CHANGELOG.md`, `LICENSE` at ZIP root. This project's policy requires license and
changelog even though Thunderstore's baseline only requires the first three.
The icon validator deliberately supports noninterlaced 8-bit RGB/RGBA PNG only;
re-export other valid PNG variants. Payload limits are 128 MiB/file and 256 MiB
total. These are v0.1 tool limits, not Thunderstore limits.

Verification requires the **entire canonical archive bytes** produced by the
current workbench, not just matching entries. Comments, extra metadata, prefixes
and trailing data are rejected. Repackage archives created by older versions or
other archivers; this command is intentionally not a generic external ZIP validator.

Source parity uses a bounded lexical guard, not a C# compiler. Regular and
verbatim literals are supported for the version; comments and other regular,
verbatim/raw literals cannot fake declarations. Interpolated or conditional
identity sources fail closed: use a dedicated simple identity file instead.
Escaped version expressions/raw-string version constants are not supported.
Compilation and emitted DLL identity remain separate checks.

Private directories, `.env*`, `Init.bnk`, Unity packages, PDBs, keys and familiar
game/framework DLL names are denied even when explicitly allowlisted. Renaming
a prohibited binary does not make it legitimate; human provenance review is
required. Pattern scans cannot inspect compressed assetbundle internals.

Decoded JSON keys/string values are scanned too, so JSON escaping does not hide
private paths or known credential forms. Named JSON inputs fail closed on
malformed/duplicate-key data. Fingerprints include existing AGENTS.md/CLAUDE.md;
new scaffolds also declare an unresolved local dependency lock. Adopted projects
must declare their actual lock, relevant source and environment identity inputs.

## Current task

The generated `local/task.json` describes `id`, `goal`, full `base` SHA or null, `status`,
one `integrator`, `owned_paths`, `acceptance` and `next_action`. Each acceptance
has an id, evidence level, status and relative evidence file or null. Each id
must be unique within that task. Duplicate ids are rejected so distinct
required gates cannot collapse into one result mapping. A passed
declaration needs a file; a done task needs every listed acceptance passed.
`status` only reports declarations and never independently validates their truth.
The task remains ignored and is an operational artifact, not an instruction diary.
An authorization-looking field would not be real user authorization; none is
defined. Ownership paths do not grant filesystem permissions.

## Record a result

Capture `identity --root PROJECT` **before** running the relevant checks. Copy
the returned `input_hashes` map into an operator result JSON. It must still match
when recorded. Add actual tool versions and a full-log review. Example check:

```json
{
  "id": "native-held-repress",
  "level": "solo",
  "status": "not_run",
  "terminal": false,
  "exit_code": null,
  "assertions": 0,
  "full_log_review": "not_run",
  "log": null,
  "observations": "Requires the separately authorized in-game acceptance window."
}
```

The complete result object has `schema: 1`, matching `task_id`, `input_hashes`,
`tool_versions` (name → measured version), `checks` and `limitations` (strings).
Use `record ... --receipt evidence/unique.json`. A passed check requires terminal
completion, at least one current assertion, passed full-log review and an
existing log. Nonzero exit cannot be a pass. Manual checks can use null exit
codes. Failed/blocked/not_run checks are preserved with exit code 1. No waiver
status exists. Logs are read for identity/scanning but are not copied into receipts.

Receipts have tool version, timestamp, declared mode, current Git commit/dirty
status when available, exact declared input hashes and operation scope.
Package receipts include every ZIP entry's byte count/hash plus whole ZIP hash.
They always say runtime compatibility is unverified. Result receipts explicitly
label observations as operator attestations. They do not update task acceptance,
so the integrator must review and update the task deliberately.

`record` also returns and stores `acceptance_coverage`: required ids, matching
passed checks, missing checks, evidence-level mismatches, nonpassing required
checks and unrelated ids. Matching requires both the exact id and level from
the current task. A successful unrelated offline check cannot cover a named
multiplayer gate. `all_required_reported_passed` concerns this single result's
validated operator attestations; it does not independently approve observations,
merge older receipts or update the task. Changed acceptance invalidates input identity.

Exit code 0 and `all_reported_checks_passed` still concern the supplied checks.
Inspect coverage separately: a valid passing build-only receipt may leave solo,
controller and multiplayer gates missing. Preserve that useful scoped result
instead of relabeling it as overall acceptance or manufacturing unrun checks.

Ignored receipts can still contain observations and sensitive paths in log
filenames; redact and review before sharing. The scanner is a guardrail. It does
not replace a rights review, credential review or reading the full native log.
