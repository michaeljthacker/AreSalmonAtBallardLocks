# STANDARDS
<!-- See plans/FORMATS.md for expected structure. Every entry requires a "Why this matters long-term" line — if you can't write a meaningful one, the entry doesn't belong here. -->

### Branching convention
- Feature work in a shared repo (e.g. `mjt-pub-api`) branches off `main`, and this project does not assume ownership of that repo's working state — other projects have concurrent in-flight branches. Rebase/branch from `main`, not from whatever happens to be checked out. (2026-09-06)
  **Why this matters long-term:** shared repos are consumed by multiple projects at once; assuming exclusive ownership of the working tree or basing work off an unrelated branch silently entangles this project's changes with another's, producing merge conflicts and cross-project regressions that are expensive to untangle.
