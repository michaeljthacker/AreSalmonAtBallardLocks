# DECISIONS
<!-- See plans/FORMATS.md for expected structure. Every entry requires a "Why this matters long-term" line — if you can't write a meaningful one, the entry doesn't belong here. -->

## Standing decisions

- **Frontend is a plain static site — HTML/CSS/vanilla JS, no framework, no build step.** The `stencil-bible-guides` name that seeded this project refers to the *workspace/devcontainer pattern* only; it does not imply Stencil or any frontend framework. (2026-09-06)
  **Why this matters long-term:** the workspace name actively misleads — an early README inferred "Stencil-based web frontend" from it, and any future contributor (or agent) reading the lineage will draw the same wrong conclusion. This project's whole cost/complexity argument rests on a zero-build static site, so re-introducing a framework would quietly break the "tiny, boring, runs cheaply" premise that scopes M4 and the hosting choice in M5.

- **Workspace repo naming: remote is `workspace-`prefixed, local directory is not.** Remote `https://github.com/michaeljthacker/workspace-AreSalmonAtBallardLocks.git`; local folder `DevSpace/workspaces/AreSalmonAtBallardLocks`. The names intentionally differ. (2026-09-06)
  **Why this matters long-term:** the unprefixed GitHub name was already taken by this frontend repo, so the mismatch is deliberate, not drift. Without this recorded, a future contributor is likely to "correct" one side to match the other and break the workspace's `origin` or the `.code-workspace` relative roots, which resolve against the local directory name.

## Deprecated decisions

- None.
