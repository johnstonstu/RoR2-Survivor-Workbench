# v0.1.1 validation record

The implementation was checked on Windows using the existing Python 3.11.15
interpreter. No tool installation, external provider call, game/profile write
or editor launch was needed. The optional survivor build restored only existing
cached dependency packages into an isolated local SDK/package environment.

After two independent reviews and the survivor recipe, 50 tests ran: 49 passed and one
filesystem-symlink creation case was skipped because the host denied creating
symlinks. ZIP symlink rejection was exercised independently. Linux/Windows CI
configuration is prepared but was not executed remotely.

The end-to-end synthetic demo creates a scaffold, adds original synthetic data,
pins it, checks release inputs, builds a deterministic allowlisted ZIP and
independently verifies its exact entries/bytes. The archive's known synthetic
payload is explicitly not a playable mod.

Review corrections included validating raw ZIP names before Windows/NUL
normalization, unsupported compression rejection, new-output ancestor collision
checks, same-byte result parsing, concurrent source change detection, and
Git observation with optional index writes/fsmonitor disabled. Each concrete
issue has a regression check. The review was source-based; the reviewer did
not claim independent native/runtime validation.

The second independent review supplied concrete repros for JSON-escaped private
paths, nonentry ZIP payloads, source string/comment confusion, whitespace around
license/provenance sentinels and omitted instructions/locks in fingerprints.
All were fixed with bounded regression fixtures. Archive verification now also
requires canonical whole-container bytes. The C# identity guard is explicitly
limited and fails closed on interpolation/preprocessor conditionals.

Packet verification exercises a bounded context response and proves a changed
declared source invalidates its fingerprint. Verification receipts record
measured check elapsed seconds; no token usage, price or savings is invented.

Run `python scripts/verify_tool.py` for a new local receipt and complete check
logs under ignored `local/verification-<timestamp>/`. Source hashes bind this
tool check to actual code/docs. Skips are recorded in the complete unit log.
Keep these operational logs local; this document is the public summary.

The original first-survivor example compiled with .NET SDK 10.0.302 against its
exact resolved lock: one retained NU1701 warning and zero errors, 10,752-byte WorkbenchRecruit
DLL. Its actual source/output receipt is separate from package verification.
Full SDK/restore/build logs were reviewed; no broad warning waiver was applied.
MMHOOK.RoR2 2025.12.9 targets .NET Framework while this example targets
netstandard2.1; NU1701 reports that compatibility remains uncertain. The project
does not suppress it. Compile success leaves that native compatibility gate open.
The public BUILD-VERIFICATION summary binds the final repository build. A prior
checkout produced different DLL bytes from the same declared sources; identical
build output across checkout locations is unverified. Deterministic ZIP parity
is verified against each selected artifact, not assumed from compiler settings.
No C# survivor was launched. Unity/Wwise artifacts, native member access,
prefab/catalog presentation, controller feel, actual multiplayer, media browser
rendering and survivor release remain unverified. The MIT contributor notice
covers original project work; third-party adoption rights remain separate
maintainer review items for future integrations or survivor releases.

The subsequent local workflow refinement adds six synthetic acceptance-coverage
regressions: unrelated results, wrong evidence levels, fully attested coverage
without task mutation, retained failed gates, changed-task identity and duplicate
gate ids. The complete current suite runs 56 tests: 55 pass and the same one
host-dependent symlink case is skipped. Source/privacy scan and synthetic demo
pass. No survivor rebuild or additional runtime/editor test was necessary;
the compile record above remains a historical build bound to its own inputs.
