# STANDARDS
<!-- See plans/FORMATS.md for expected structure. Every entry requires a "Why this matters long-term" line — if you can't write a meaningful one, the entry doesn't belong here. -->

### Branching convention
- Feature work in a shared repo (e.g. `mjt-pub-api`) branches off `main`, and this project does not assume ownership of that repo's working state — other projects have concurrent in-flight branches. Rebase/branch from `main`, not from whatever happens to be checked out. (2026-09-06)
  **Why this matters long-term:** shared repos are consumed by multiple projects at once; assuming exclusive ownership of the working tree or basing work off an unrelated branch silently entangles this project's changes with another's, producing merge conflicts and cross-project regressions that are expensive to untangle.
  Promoted to `mjt-pub-api/STANDARDS.md` on 2026-09-07 — retained here because this project applies the rule directly whenever it touches the backend.

### Development environment
- The devcontainer is the standard development environment for projects consuming `mjt-pub-api`: it owns Python venv creation and dependency installation (from the backend's `requirements/dev.txt`), and verification runs inside it. Do not maintain a co-equal host-venv workflow as a documented parallel path. (2026-09-06)
  **Why this matters long-term:** the shared backend pins a specific Python version and dependency set, and each consuming project would otherwise reproduce venv management slightly differently on its host — the exact drift that makes "works on my machine" bugs expensive across a multi-project, multi-repo setup. Documenting a host fallback as co-equal guarantees it will be used, and then diverge. If a live container rebuild genuinely can't be run, record the gap in a verification log rather than substituting a host path.
  Promoted to `mjt-pub-api/STANDARDS.md` on 2026-09-07 — retained here because this project's own dev environment is governed by it.

