# Security and privacy

No manifest field is executable. The core does not extract archives, run builds,
discover provider credentials, call providers, upload data or modify profiles.
It refuses linked inputs, portable path violations and unexpected ZIP entries.
The separate first-survivor script is an explicit fixed build-only adapter; it
uses a locked reference graph and isolated SDK settings, never manifest commands.

Pattern scanning catches common credential/private-path forms in UTF-8 and
UTF-16-LE bytes and decoded JSON strings; it is not a complete secret detector, malware scanner, rights
checker or sandbox for game binaries. Compressed bundle contents and obfuscated
secrets need independent review. Metadata checks alone do not scan all source.

Keep machine configuration, credentials, raw game logs and evidence local and
ignored. Share a redacted summary with hashes after review. Do not attach a
suspected credential or personal log to a public issue; contact the maintainer
through an independently verified private channel. No support mailbox or
security contact is configured for this project.

Before a public push, review every reachable commit and tracked blob, including
author/committer identities and content removed in later revisions. Ignoring a
file does not remove it from history. Keep private work/history backups local;
publish only the reviewed branch and use a GitHub no-reply commit address.
Synthetic sensitive-pattern test fixtures are fictional and deliberately
constructed; review their purpose rather than deleting the privacy regressions.
