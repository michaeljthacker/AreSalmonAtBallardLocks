# Thread
<!-- Append-only log. See plans/FORMATS.md for protocol. -->

---
### PM.ThreadMaintenance — 2026-09-07
B1-M1 is fully closed (code review, formal approval, documentation update, and milestone closeout have all run), so every `every_milestone` gate protecting M1 content has been satisfied. Pruned all M1 build-review, question, execution, review, and approval entries after promoting the durable content below.

**Promoted to plans/DECISIONS.md** (three entries; DECISIONS.md had never been populated — it still held template placeholder text, and two of these were explicitly marked "capture in DECISIONS.md" during M1 but never written):
- Frontend is a plain static site (HTML/CSS/vanilla JS, no framework, no build step).
- `stencil-bible-guides` is a reference model to adapt, never a verbatim clone.
- Workspace repo naming: `workspace-`prefixed remote, unprefixed local directory — deliberately mismatched.

**Promoted to plans/STANDARDS.md:**
- Development environment — the devcontainer is the standard environment for projects consuming `mjt-pub-api` and owns venv/dependency setup; no co-equal host-venv path.

**Dropped as implementation detail** (no durable rationale, or already captured elsewhere): Q-001 (defer first push) and Q-002 (static-validation + documented-gap definition of done) — both one-off operational rulings, now spent. Review items CR-1 (path casing) and CR-2 (`dev.sh` venv guard) — implemented, visible in the code. BuildReview S-1/S-3 and risks R-2/R-3 — already carried in BUILD.md Scope and Risks. S-2 (crowd-report anti-abuse) — already tracked in BACKLOG.md P1. R-1 (reuse-of-pattern friction) — retired; M1 shipped and the pattern held.

**Contradiction resolved:** two conflicting UPDATE lines had accumulated in the Principal.AnswerQuestions entry regarding backend dependency hygiene — one said it was "now recorded as a standing decision in DECISIONS.md," the other said it was plan-scoped only. DECISIONS.md contained no such entry, and MILESTONE.md records it as plan-scoped. Resolved as **plan-scoped, not a standing decision**; it remains captured in MILESTONE.md Notes (dependency remediation stays out of B1, tracked as a separate `fix/` branch off `main`). No DECISIONS.md entry written.

**Promotion proposals surfaced — awaiting human approval (see below). Nothing has been written to any shared repo.**

---
### PM.ThreadMaintenance — 2026-09-07 (PENDING: shared-standard promotion proposals)
`workspace.shared_repos` includes `mjt-pub-api`. Two STANDARDS.md entries meet all three promotion tests (rationale generalizes beyond this project, concerns code/contracts owned by the shared repo, and is stable rather than under active negotiation). Both are proposed for promotion into the shared repo so other consuming projects inherit them:

```
Promotion proposal 1:
  entry: "Feature work in a shared repo (e.g. `mjt-pub-api`) branches off `main`, and this
          project does not assume ownership of that repo's working state — other projects
          have concurrent in-flight branches. Rebase/branch from `main`, not from whatever
          happens to be checked out. (2026-09-06)
          **Why this matters long-term:** shared repos are consumed by multiple projects at
          once; assuming exclusive ownership of the working tree or basing work off an
          unrelated branch silently entangles this project's changes with another's,
          producing merge conflicts and cross-project regressions that are expensive to
          untangle."
  source: plans/STANDARDS.md  (### Branching convention)
  target_repo: mjt-pub-api
  target_path: ../../Projects/mjt-pub-api/STANDARDS.md
  rationale: The rule is about mjt-pub-api's own branching contract and binds every consuming
             project equally, not just this one. Living only in this project's plans/ means
             each new consumer must rediscover it — and this milestone already hit the failure
             mode it prevents (the backend was sitting on another project's feature branch).

Promotion proposal 2:
  entry: "The devcontainer is the standard development environment for projects consuming
          `mjt-pub-api`: it owns Python venv creation and dependency installation (from the
          backend's `requirements/dev.txt`), and verification runs inside it. Do not maintain
          a co-equal host-venv workflow as a documented parallel path. (2026-09-06)
          **Why this matters long-term:** the shared backend pins a specific Python version
          and dependency set, and each consuming project would otherwise reproduce venv
          management slightly differently on its host — the exact drift that makes 'works on
          my machine' bugs expensive across a multi-project, multi-repo setup. Documenting a
          host fallback as co-equal guarantees it will be used, and then diverge. If a live
          container rebuild genuinely can't be run, record the gap in a verification log
          rather than substituting a host path."
  source: plans/STANDARDS.md  (### Development environment)
  target_repo: mjt-pub-api
  target_path: ../../Projects/mjt-pub-api/STANDARDS.md
  rationale: This describes how the shared backend's own venv and dependency set are meant to
             be consumed — it is a property of mjt-pub-api, not of the salmon project. The
             backend is already developed this way in other projects; writing it down in the
             shared repo makes the existing convention discoverable instead of tribal.
```

**Human response options:** `approve all` / `approve 1` / `approve 2` / `reject all` / `approve with edits: <text>`. On approval, the next PM.ThreadMaintenance run appends the approved entries to `mjt-pub-api/STANDARDS.md` (no `plans/` wrapper — shared repos never get one) and cross-references them here. On rejection, the entries simply stay in this project's STANDARDS.md.

**Note:** writing to `mjt-pub-api` means committing to the shared repo. Per the branching standard itself, that write should land on a branch off `main`, not on whatever is currently checked out.

**After this is resolved, proceed to Principal.MilestonePlan for B1-M2.**
