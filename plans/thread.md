# Thread
<!-- Append-only log. See plans/FORMATS.md for protocol. -->

---
### PM.ThreadMaintenance — 2026-09-07
B1-M1 is fully closed (code review, formal approval, documentation update, and milestone closeout have all run), so every `every_milestone` gate protecting M1 content has been satisfied. Pruned all M1 build-review, question, execution, review, and approval entries after promoting the durable content below.

**Promoted to plans/DECISIONS.md** (DECISIONS.md had never been populated — it still held template placeholder text, and both of these were explicitly marked "capture in DECISIONS.md" during M1 but never written):
- Frontend is a plain static site (HTML/CSS/vanilla JS, no framework, no build step).
- Workspace repo naming: `workspace-`prefixed remote, unprefixed local directory — deliberately mismatched.

**Proposed but rejected by the human (2026-09-07):** "`stencil-bible-guides` is a reference model to adapt, never a verbatim clone" — scoped to M1 only, not durable. Removed from DECISIONS.md.

**Promoted to plans/STANDARDS.md:**
- Development environment — the devcontainer is the standard environment for projects consuming `mjt-pub-api` and owns venv/dependency setup; no co-equal host-venv path.

**Dropped as implementation detail** (no durable rationale, or already captured elsewhere): Q-001 (defer first push) and Q-002 (static-validation + documented-gap definition of done) — both one-off operational rulings, now spent. Review items CR-1 (path casing) and CR-2 (`dev.sh` venv guard) — implemented, visible in the code. BuildReview S-1/S-3 and risks R-2/R-3 — already carried in BUILD.md Scope and Risks. S-2 (crowd-report anti-abuse) — already tracked in BACKLOG.md P1. R-1 (reuse-of-pattern friction) — retired; M1 shipped and the pattern held.

**Contradiction resolved:** two conflicting UPDATE lines had accumulated in the Principal.AnswerQuestions entry regarding backend dependency hygiene — one said it was "now recorded as a standing decision in DECISIONS.md," the other said it was plan-scoped only. DECISIONS.md contained no such entry, and MILESTONE.md records it as plan-scoped. Resolved as **plan-scoped, not a standing decision**; it remains captured in MILESTONE.md Notes (dependency remediation stays out of B1, tracked as a separate `fix/` branch off `main`). No DECISIONS.md entry written.

**Promotion proposals surfaced — awaiting human approval (see below). Nothing has been written to any shared repo.**

---
### PM.ThreadMaintenance — 2026-09-07 (promotions executed)
Human approved both shared-standard promotion proposals. Executed against the shared `mjt-pub-api` repo on branch `feat/salmon-ballard-locks` (verified checked out and clean before writing; branch previously confirmed to match `main`).

**Written to `mjt-pub-api/STANDARDS.md`** (root-level standards doc — the shared repo owns no `plans/`), matching that file's existing entry format and its "Promoted from ..." provenance convention:
- Branch feature work off `main`, never assume ownership of this repo's working state.
- The devcontainer is the standard development environment for projects consuming this repo (owns venv + `requirements/dev.txt` install).

Both source entries are **retained** in this project's `plans/STANDARDS.md` with a one-line cross-reference rather than deleted — each still governs this project's own behavior directly.

Blocker BL-001 cleared. Proceeding to Principal.MilestonePlan for B1-M2.
