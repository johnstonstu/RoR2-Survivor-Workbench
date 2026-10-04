# Shared runtime ownership

Worktrees isolate source files. They do **not** isolate installed profiles, game
processes, saves, Unity, Wwise, editor bridges or generated outputs. Use one
integrator and one short atomic runtime lease across cooperating projects.
No runtime tool is implemented or executed by workbench v0.1.

## Requirements for a future staging adapter

1. Target one explicit disposable profile and one owned plugin subtree. Require
   a profile marker and resolve/canonicalize every parent; reject links/junctions,
   escapes, unknown touched files and production/save/config/binding paths.
2. Verify the game is closed. Use a fixed shared coordination location agreed by
   all runtime owners; it must sit outside individual worktrees. For a game-global
   resource, lease the game/session too, not merely the target profile.
3. Atomically create a new lease (exclusive create) with owner, task/run id,
   resource identities and creation time. An existing, partial or unreadable
   lease is occupied. Never steal by age. The same owner token must release it.
4. Validate the complete input set, provenance, versions, dependency lock and
   native access before the first write. Snapshot current state and hash every
   touched file. Recheck input identity after any intervening build.
5. Back up only files to be replaced. Stage only allowlisted owned files, verify
   destination hashes, and record previous/new hashes, created files and exact
   restore steps. A partial failure must restore or explicitly report the state.
6. Recheck game-closed immediately before writes. Keep writes and any authorized
   runtime capture short and serial. Release only after owned runtime processes
   have stopped. Retain the receipt and backups until acceptance is complete.

Never glob-deploy across profiles. Never delete a fixed "clean" profile to make
a test look fresh. Create a uniquely named disposable profile only when that
action is authorized; preserve user saves/settings. Test the exact package, not
an old profile silently fed by a post-build copy. Unity/Wwise need their own
shared ownership and expected-version checks before an editor opens a project.

The process check/lease alone cannot prevent a human or unrelated tool from
launching the game concurrently. An eventual adapter must document that residual
race and its coordination contract. Do not present a lease file as a complete
operating-system isolation guarantee.
