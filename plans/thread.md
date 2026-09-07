# Thread
<!-- Append-only log. See plans/FORMATS.md for protocol. -->

---
### Principal.BuildReview — 2026-09-06
Build Review for **B1** — "Are Salmon at Ballard Locks?"

**Outcome: APPROVED** — BUILD.md is ready for milestone planning.

Assessment: Purpose is clear and specific; scope in/out is well-defined and mirrors VISION §18 anti-scope; success criteria are measurable enough for an MVP; the M1–M5 breakdown is a reasonable, dependency-ordered progression. `size: full` is consistent with the 5-milestone count and with the genuine multi-repo, multi-component scope (VISION acknowledges multiple repos + several substantial components). Prose depth matches `full`. Faithful to the concept brief, including the §0 "reproduce workspace/devcontainer first" constraint and the pending human confirmation on the `workspace-AreSalmonAtBallardLocks` repo.

**REQUIRED changes (blocking):** None.

**SUGGESTED improvements (non-blocking):**
- S-1: `fish_count` uniqueness constraint — VISION §4.2 leaves `(date, species, source)` vs `(date, species)` to be chosen after inspecting source data. Defer to M2 as intended, but MilestonePlan should make "inspect source, then choose constraint" an explicit early step so the importer's idempotency contract isn't blocked.
- S-2: Crowd-report anti-abuse (rate limiting / basic spam resistance) is deferred per VISION §4.1 — reasonable for MVP, but worth logging to BACKLOG so it isn't forgotten before public QR-driven traffic arrives.
- S-3: Hosting/deployment for both frontend and the scheduled importer is implied but not called out as a deliverable. Fine to defer, but note it (likely M4/M5) so the "runs cheaply, covers its own costs" cost philosophy stays concrete.

**RISKS identified (for awareness):**
- R-1: Reuse of the `stencil-bible-guides` devcontainer pattern and `mjt-pub-api` "as-is" is an assumption; M1 may surface friction. Already flagged in BUILD Risks — carry into M1 planning.
- R-2: Public historical/official fish-count source quality and stability is the biggest data risk; bootstrap + importer must tolerate gaps, backfill, and source unavailability (VISION §5–6, §17). Already flagged.
- R-3: Forecast over-engineering risk — VISION §8/§20 explicitly want a simple, explainable model. Keep M3 deterministic; resist scope creep into ML.

---
### Human.ApproveBuild — 2026-09-06
**Decision: CHANGES REQUIRED** — routing back to Principal.BuildReview to revise BUILD.md before approval. Human reviewed VISION.md and README.md directly.

Requested changes for the next Principal.BuildReview pass:

1. **Frontend stack = vanilla HTML/CSS/JS.** VISION never names a stack; README.md inferred "Stencil" solely from the `stencil-bible-guides` workspace name — that inference is not the human's intent. The frontend is a plain static site (HTML/CSS/vanilla JS), no framework/build step, consistent with the "tiny, boring, one-frontend" philosophy (VISION §3.5, §20). BUILD.md should state the stack explicitly, and README.md's "Stencil-based web frontend" claim must be corrected (README is a Product.ProductVision output, editable by that role / on a re-derive — flag for correction; at minimum BuildReview should note the discrepancy so it isn't shipped).

2. **`stencil-bible-guides` is a REFERENCE/EXAMPLE, not a literal duplicate.** Reword BUILD.md Scope (currently "Reproduce the existing … pattern") and carry into M1 framing: use `stencil-bible-guides` as a reference model for the multi-root workspace/devcontainer setup and **adapt as needed** — do not clone it verbatim. (VISION §0 "reproduce"/"do not invent a new architecture" language should be read as "prefer the proven pattern, adapt," not "duplicate.")

3. **Fold S-1, S-2, S-3 explicitly into BUILD.md** (previously suggested-only):
   - S-1 → add to Scope/M2: inspect source data first, then choose the `fish_count` uniqueness constraint `(date, species, source)` vs `(date, species)` as an explicit early M2 step (importer idempotency depends on it).
   - S-2 → add crowd-report anti-abuse (rate limiting / basic spam resistance) to BACKLOG as deferred-but-tracked before public QR traffic.
   - S-3 → name hosting/deployment for both the static frontend and the scheduled importer as an explicit deliverable (likely M4/M5), to keep the "runs cheaply, covers its own costs" philosophy concrete.

Non-blocking note: `size: full` and the M1–M5 breakdown remain fine; the human did not request a size or milestone-count change. These edits are refinements within the existing structure.

---
### Principal.BuildReview — 2026-09-06 (pass 2)
Build Review for **B1** — re-review after Human.ApproveBuild returned CHANGES REQUIRED. Human explicitly authorized editing BUILD.md and README.md for this pass.

**Outcome: APPROVED** — all three requested changes applied; BUILD.md is ready for milestone planning.

Changes made:
1. **Frontend stack made explicit = plain static site (HTML/CSS/vanilla JS, no framework, no build step).** Added as a Scope bullet in BUILD.md with a note that `stencil-bible-guides` names the *workspace/devcontainer pattern*, not a frontend framework. Corrected README.md's "Stencil-based web frontend" line to the vanilla static-site description.
2. **`stencil-bible-guides` reframed as reference-to-adapt, not verbatim clone.** Reworded BUILD.md Scope, M1, and the Risks/assumptions line accordingly.
3. **S-1/S-2/S-3 folded in explicitly:**
   - S-1 → Scope + M2 now state: inspect source data first, then choose the `fish_count` uniqueness constraint (`(date, species, source)` vs `(date, species)`) as an early M2 step.
   - S-2 → added crowd-report anti-abuse (rate limiting / basic spam resistance) to BACKLOG.md as P1, deferred-but-tracked before public QR traffic.
   - S-3 → hosting/deployment for both the static frontend and the scheduled importer named as an explicit Scope deliverable and carried into M4 (frontend deploy) and M5 (confirm cheap deployment of both).

---
### Staff.DraftQuestions — 2026-09-06
Questions before executing B1-M1-P1 (steps S1–S5). Reference (`workspaces/stencil-bible-guides`: `.devcontainer/` + `dev.sh` + `.code-workspace` + `.gitignore`/`.gitattributes`/`README.md`) and `mjt-pub-api/requirements/dev.txt` all confirmed present on disk; the MILESTONE resolves stack, paths, remote, env model, and step order. Only two decision-oriented items remain — neither is answerable by inspecting the reference.

- **Q-001 — Initial workspace-repo push.** Blocking: No (important). S1 says `git init` the workspace folder and set `origin` to `https://github.com/michaeljthacker/workspace-AreSalmonAtBallardLocks.git`. Should the executor also `git push` the initial commit to that (empty) GitHub remote, or only `git init` + configure `origin` locally and leave the first push to the human? Pushing is outward-facing/hard-to-reverse; default recommendation is init + set-origin only, defer push — please confirm.

- **Q-002 — S5 "done" definition: hard acceptance criteria vs. Notes fallback.** Blocking: No (important). The S5 acceptance checkboxes are written as live requirements ("Inside the (re)built devcontainer… `python manage.py check` runs"; "`dev.sh` starts API/frontend, Ctrl+C stops both"), but the Notes say if a live rebuild can't be completed on the host, "note the exact gap in the S5 verification log." The agent cannot drive VS Code "Reopen in Container" / a live Docker rebuild non-interactively on the Windows host. For M1 completion, does authoring + static validation (valid JSON, scripts present/executable, deps path correct) + a documented rebuild/verify gap satisfy the milestone, or must a live container rebuild + both servers confirmed responding be performed (by the human) before M1 can close? This governs whether P1 can complete autonomously or pauses for a human-run verification.

`size: full` and the M1–M5 structure unchanged, per the human's note. No remaining REQUIRED changes. Risks R-1/R-2/R-3 from pass 1 still stand for M1–M3 planning awareness.

---
### Human.ApproveBuild — 2026-09-06 (pass 2)
**Decision: APPROVED** — BUILD.md (pass 2) accepted. All three change requests verified applied (vanilla static-site stack; `stencil-bible-guides` reframed as reference-to-adapt; S-1/S-2/S-3 folded into BUILD.md/BACKLOG). Routing to PM.StatusUpdate, then Principal.MilestonePlan.

**Resolves VISION §0 open item — workspace repo confirmed by human:**
- GitHub remote (already created, empty): `https://github.com/michaeljthacker/workspace-AreSalmonAtBallardLocks.git` (repo name keeps the `workspace-` prefix, since the unprefixed name is taken by this frontend repo).
- Local folder: `C:/Users/Micha/DevSpace/workspaces/AreSalmonAtBallardLocks` (unprefixed dir name — intentional; local dir name need not match the remote repo name).
- M1 approach: create the local `workspaces/AreSalmonAtBallardLocks` folder, then `git init` / add the above URL as `origin`. No longer "pending human confirmation" — M1 should treat this as decided. (This should be captured as a decision in DECISIONS.md during M1 planning/execution.)

---
### Human.ApproveMilestone — 2026-09-06
**Decision: CHANGES REQUIRED** — routing back to Principal.MilestonePlan to re-draft MILESTONE.md for B1-M1. Human reviewed the plan directly.

Requested changes for the re-draft:

1. **Collapse the phase count.** 4 phases is too much ceremony for pure scaffolding. Re-draft as **1 phase with multiple steps**, or **at most 2 phases**. Fold the current P1–P4 work (workspace folder/repo bootstrap, `.code-workspace`, devcontainer, `dev.sh` + placeholder frontend + verification) into that reduced structure. Keep acceptance criteria, but proportion the prose to the smaller structure.

2. **Devcontainer is the standard for `mjt-pub-api` — lean on it.** The backend is already developed inside a devcontainer in other projects, so do the same here (this is what makes venv management easy). Drop the "host-venv fallback" framing as the primary path; the devcontainer is the intended venv/dependency environment. The plan can still note a check to run, but should not present a parallel host-venv workflow as co-equal. This also simplifies the "devcontainer verification caveat" note.

3. **`mjt-pub-api` branching discipline (shared repo).** Feature work on the backend must branch off `main`. Because `mjt-pub-api` is shared and the human has other in-flight feature branches in other projects, stay cognizant of concurrent branches — don't assume this project owns the backend's working state. Capture this as a standing decision/standard when M1/M2 execute (belongs in DECISIONS.md or STANDARDS.md, and the shared_repos role note in config.json now records it too).

4. **`config.json` shared_repos — DONE (this action).** Human authorized the update; `mjt-pub-api` is now registered as a shared repo (`path: ../../projects/mjt-pub-api`) with a role note covering the branch-off-main / shared-awareness guidance. The re-draft should therefore **remove the "shared_repos is empty — flag for the human" note** from MILESTONE.md and instead reference the now-configured shared scope. (Config is normally human-owned; the human explicitly asked SAM to make this edit.)

5. **OPEN QUESTION — backend dependency hygiene (dependabot warnings): keep it OUT of this BUILD.** Human asked whether to fix `mjt-pub-api` dependency/dependabot warnings as part of standing up this project, or as a separate unrelated branch. **Recommendation: separate, wholly-unrelated `fix/` branch off `main`, NOT part of B1.** Rationale: (a) dependency hygiene on a shared repo affects every consumer, not just this project — coupling it to B1 muddies scope and review; (b) it's independently valuable and independently revertable; (c) B1 should be able to proceed against the backend as-is and not be blocked on a dependency-remediation effort. This keeps B1's blast radius to "add a webapp + workspace," not "also upgrade the shared platform." Do NOT add dependency remediation to any M1 phase. If the human agrees, this can be recorded as a DECISIONS.md entry (shared-repo dependency work is tracked/executed independently of feature builds). Awaiting human confirmation of this recommendation.

---
### Principal.AnswerQuestions — 2026-09-06
Answering the two open questions from Staff.DraftQuestions. Both resolve without a human decision — P1 is unblocked for Staff.ImplementationExecution.

- **Q-001 — Initial workspace-repo push. Answer: `git init` + set `origin` locally only; do NOT push.** The executor creates the workspace folder, `git init`, sets `origin` to the confirmed remote, and makes the initial local commit — but leaves the first push to the human. Rationale: pushing is outward-facing and hard-to-reverse, the remote is empty with nothing (CI, other consumers) depending on an immediate push, and deferring costs nothing. The human can push whenever convenient. One-off operational choice, not a durable decision — not recorded in DECISIONS/STANDARDS.

- **Q-002 — S5 "done" definition. Answer: authored + statically-validated artifacts + a documented rebuild/verify gap satisfy M1's *autonomous* completion.** The executor authors all artifacts (workspace repo, `.code-workspace`, `.devcontainer/*`, `dev.sh`, placeholder `index.html`, README/VERIFY docs) and statically validates what it can non-interactively: JSON validity of `.code-workspace` and `devcontainer.json`, scripts present + executable, backend deps path (`mjt-pub-api/requirements/dev.txt`) correct, exactly three roots with correct relative paths, no Stripe/LLM residue. The acceptance criteria that require a *live* container — devcontainer rebuild, venv usable, `python manage.py check`, both servers responding, Ctrl+C clean shutdown — are performed by the human (who can drive "Reopen in Container" interactively) and their outcome recorded in the S5 verification log; the executor must clearly mark in that log which criteria are agent-verified vs. pending human live-rebuild confirmation. Not a new ruling — it is the MILESTONE Notes' own instruction ("note the exact gap in the S5 verification log"). So P1 proceeds now; the live-rebuild confirmation surfaces at Principal.CodeReview / Human.PhaseApproval rather than blocking execution.
  - *Breadcrumb (engineering judgment):* the agent genuinely cannot drive an interactive "Reopen in Container" / live Docker rebuild non-interactively on the Windows host — tooling limitation, not a design choice, and not a one-way door. If the human would rather P1 *pause* for a live rebuild before M1 can close at all (stricter than the MILESTONE Note), say so and I will re-route; absent that, the documented-gap path stands.

- **Standing standard promoted (Human.ApproveMilestone item 3):** shared-repo branching discipline recorded in STANDARDS.md (Branching convention) — portable to any project using a shared repo, so STANDARDS over DECISIONS. Applies at M2 when backend code is first touched; M1 only bind-mounts `mjt-pub-api`.

- **Still pending human confirmation (Human.ApproveMilestone item 5), not recorded yet:** backend dependency-hygiene / dependabot work stays OUT of B1 as a separate `fix/` branch off `main`. Already reflected as out-of-scope in MILESTONE.md and blocks nothing in P1 (no M1 step touches it), so no DECISIONS entry is written until the human confirms. Not a P1 blocker.
  - **UPDATE (2026-09-06): human confirmed both open items.** (1) Live devcontainer rebuild stays at the end — documented-gap path stands; P1 does not pause for it. (2) Backend dependency hygiene stays OUT of B1 (separate `fix/` branch off `main`). Human noted this is plan-scoped, not a standing decision, so it is kept here / in MILESTONE.md rather than DECISIONS.md.
  - **UPDATE (2026-09-06): human confirmed both open items.** (1) Live devcontainer rebuild stays at the end (documented-gap path stands; P1 does not pause for it). (2) Backend dependency hygiene stays OUT of B1 — now recorded as a standing decision in DECISIONS.md.

---
### Staff.ImplementationExecution — 2026-09-06
**Review Request — B1-M1-P1** (Multi-root workspace + devcontainer scaffolding)

**What was implemented (S1–S5):** Stood up the multi-root workspace by adapting the `stencil-bible-guides` pattern, stripped of that project's Stripe CLI, Stripe webhook forwarder, and LLM worker. Created the workspace folder/repo (`git init`, `origin` set, initial commit — **not pushed**, per Q-001), the `.code-workspace` (three roots), the devcontainer (venv/deps owner), `dev.sh` (API + static frontend only), a temporary placeholder `index.html` in the frontend repo, and README/VERIFY docs. Per Q-002, all artifacts were authored + statically validated non-interactively; the live in-container rebuild + servers-responding checks are logged as pending human confirmation in `VERIFY.md`.

**Key files changed:**
- `workspaces/AreSalmonAtBallardLocks/AreSalmonAtBallardLocks.code-workspace` — three roots (`frontend`→this repo, `api`→`mjt-pub-api`, `workspace`→`.`), settings, extensions, Django/static tasks (no Stripe/LLM). *(separate workspace repo)*
- `workspaces/AreSalmonAtBallardLocks/.devcontainer/{devcontainer.json,postCreate.sh,postStart.sh}` — Py3.12 + Node LTS, binds all three roots, backend venv/deps from `mjt-pub-api/requirements/dev.txt`, ports 8000/8080 published to LAN, no Stripe-CLI step. *(separate workspace repo)*
- `workspaces/AreSalmonAtBallardLocks/{dev.sh,README.md,VERIFY.md,.gitignore,.gitattributes}` — runner (API :8000 + static :8080, clean shutdown), open-and-run guide, verification log, LF enforcement for `*.sh`. *(separate workspace repo)*
- `index.html` — temporary placeholder in **this** frontend repo, marked replaced-in-M4. *(primary repo — committed `ea659f8`)*
- No edits to `mjt-pub-api` (shared scope): bind-mounted only, per plan.

**Commits:** workspace repo `1f9c1aa` (scaffold); primary repo `ea659f8` (placeholder). Workspace repo `origin` set to `https://github.com/michaeljthacker/workspace-AreSalmonAtBallardLocks.git`, first push deferred to human.

**Acceptance criteria:**
- [x] Workspace folder exists, is a git repo, `origin` = confirmed remote (push deferred — Q-001).
- [x] `.code-workspace` valid JSON, exactly three roots with correct relative paths, forwards 8000/8080, no Stripe/LLM tasks.
- [x] `devcontainer.json` valid JSON, mounts all three roots; `postCreate.sh`/`postStart.sh` present + executable + LF, install from `requirements/dev.txt`, no Stripe-CLI/guide-worker.
- [~] Backend venv usable + `python manage.py check` inside container — **pending human live rebuild** (VERIFY.md).
- [~] `dev.sh` starts :8000/:8080, Ctrl+C stops both, both URLs respond — **pending human live rebuild** (VERIFY.md).
- [x] Placeholder `index.html` exists in frontend repo, marked temporary.
- [x] Workspace `README.md` documents open-and-run; `VERIFY.md` holds the verification log (static done, live pending).

**Tests:** No automated suite applies to pure environment scaffolding. "Verification" here = the static validation performed this action (JSON validity, 3-root resolution, mount sources + deps file exist, scripts present/LF, zero Stripe/worker/webhook residue) plus the deferred live-rebuild checklist in VERIFY.md.

**Risks / trade-offs:**
- Live devcontainer rebuild not exercised on the host (agent can't drive interactive Reopen-in-Container). Mitigation: documented-gap path (Q-002); human runs it once, result surfaces at CodeReview/PhaseApproval. Carries R-1 (reuse-of-pattern friction) from BuildReview.
- Path casing uses `../../Projects/...` (capital P) matching the reference; Windows is case-insensitive and config.json's `../../projects/mjt-pub-api` resolves identically.

---
### Principal.CodeReview — 2026-09-06
Review of **B1-M1-P1** (Staff.ImplementationExecution above). Scope: `code_review=every_milestone`; M1 has one phase (P1), so this covers all of M1. `review_strictness=balanced`, `size=full`.

**Outcome: APPROVED** — no REQUIRED changes.

Verified against acceptance criteria and on-disk facts:
- Workspace repo present (`1f9c1aa`), `origin` = confirmed remote, not pushed (Q-001) — correct.
- `.code-workspace` is valid JSON, exactly three roots (`frontend`→primary, `api`→`mjt-pub-api`, `workspace`→`.`) resolving on disk; ports 8000/8080; tasks are Django/static only — no Stripe/LLM. Correct.
- `devcontainer.json` valid JSON; binds all three roots; `appPort` publishes both ports to `0.0.0.0` (LAN); postCreate/postStart wired; no Stripe-CLI feature/step. Correct.
- `postCreate.sh`/`postStart.sh`/`dev.sh` present, executable, LF-terminated (`.gitattributes` enforces `*.sh eol=lf`). Confirmed on disk: backend repo, `requirements/dev.txt`, and `manage.py` all exist at `DevSpace/Projects/mjt-pub-api`; venv guard executes the interpreter (not just `[ -f ]`) and rebuilds with `--clear` — a genuinely correct resilience pattern for a bind-mounted venv across image patch bumps.
- Placeholder `index.html` in the frontend repo, clearly marked temporary/replaced-in-M4. Correct.
- `mjt-pub-api` bind-mounted only; no shared-repo code edits — consistent with the shared-repo branching standard (STANDARDS.md). Correct.

**REQUIRED changes (blocking):** None.

**SUGGESTED improvements (non-blocking):**
- CR-1: Path-casing inconsistency (cosmetic on Windows). Workspace/devcontainer use `../../Projects/...` (capital P, matching disk); config.json and README's `api` row use lowercase `projects`. All resolve on the case-insensitive Windows host, but standardizing on the real disk casing (`Projects`) removes a latent break if this ever runs on a case-sensitive host and fixes the README table’s internal inconsistency (frontend row capital, api row lowercase).
- CR-2: `dev.sh` `api()` runs `source .venv/bin/activate` with no existence guard; since `dev.sh` doesn’t use `set -e`, a missing venv would fall through to a confusing system-python error. postCreate/postStart make this unlikely, but a one-line guard (`[ -x .venv/bin/python ] || { echo "run in devcontainer / venv missing"; exit 1; }`) would fail fast with a clear message.

**Outstanding verification (not blocking this review, by prior ruling):**
- The live in-container gate — devcontainer rebuild, venv usable, `python manage.py check`, both servers responding, clean Ctrl+C shutdown — is authored and statically sound but not exercised (agent can't drive interactive Reopen-in-Container). Per the human-confirmed Q-002 ruling this is the documented-gap path; VERIFY.md holds the checklist. **Recommend the human run this once at Human.PhaseApproval** and record the result in VERIFY.md before M1 closes. This is the one open item; nothing in the static review contradicts the design.

---
### Staff.ReviewReconciliation — 2026-09-06
Posture: `last_action.result = approved` — no REQUIRED items. Both SUGGESTED items were quick and high-value, so implemented now (neither logged to BACKLOG).

**SUGGESTED items:**
- **CR-2 (implemented) — `dev.sh` venv fail-fast guard.** Added a one-line guard in `api()`: `[ -x .venv/bin/python ] || { echo "[API] .venv missing…"; exit 1; }`. Without it, a missing venv fell through `source .venv/bin/activate` (script isn't `set -e`) to a confusing system-python error. Now fails fast with a clear "start inside the devcontainer" message.
- **CR-1 (implemented, with one deliberate exception) — path-casing standardized on `Projects`.** Fixed the README three-roots table `api` row from `.../projects/mjt-pub-api` to `.../Projects/mjt-pub-api`, matching the `frontend` row and the real on-disk / `.code-workspace` / `devcontainer.json` casing (those functional artifacts already used capital `Projects`). **Left `config.json` unchanged:** its `shared_repos[].path` = `../../projects/mjt-pub-api` is human-owned config, is only consumed by SAM's case-insensitive scope routing (not by the devcontainer), and resolves identically on this Windows host. Editing human-owned config for a purely cosmetic alignment is out of this action's remit; if the human wants byte-level consistency they can flip that one path. No functional artifact remains inconsistent.

**DECISIONS/STANDARDS findings:** none. Both items are local implementation details (a defensive guard and a doc/casing tidy) — not durable project decisions or shared-platform standards, so nothing recorded per the 3b classification.

**Code changed (for targeted awareness, not full re-review):**
- shared scope: none. `mjt-pub-api` untouched.
- Workspace repo (`1d7b25c`): `dev.sh` (`api()` guard), `README.md` (casing). *(separate workspace repo, not primary)*

**Re-review decision (`re_review_trigger=auto`): no re-review → PM.StatusUpdate.** Rationale: the two changes are a cosmetic doc edit and a narrowly-scoped defensive guard. No control-flow change on the normal path, no public interface, nothing security-sensitive; `dev.sh` behaves identically when the venv exists. Mechanical/narrow per the auto guidance, so a targeted Principal re-review is not warranted.

**Outstanding:** unchanged — the live in-container gate (VERIFY.md) is still the one open verification, for the human to run at Human.PhaseApproval.

---
### Human.PhaseApproval — 2026-09-06 (BRIEFING — non-executable; human decides)
**MILESTONE APPROVAL REQUIRED — B1-M1 "Workspace/devcontainer scaffolding"**
(`formal_approval = every_milestone`; M1 has one phase P1, so this gate closes the whole milestone.)

This is a briefing only. The AI has NOT approved anything. The human reviews, runs the live rebuild, and records the decision + state.json updates below.

**What was built (P1 / all of M1):** Multi-root workspace + devcontainer scaffolding, adapted from `stencil-bible-guides` and stripped of Stripe CLI, Stripe webhook forwarder, and LLM worker. Deliverables (all in the **separate** workspace repo `workspaces/AreSalmonAtBallardLocks` unless noted):
- `AreSalmonAtBallardLocks.code-workspace` — three roots (`frontend`→this repo, `api`→`mjt-pub-api`, `workspace`→`.`), settings, extensions, ports 8000/8080, Django/static tasks only.
- `.devcontainer/{devcontainer.json,postCreate.sh,postStart.sh}` — Py3.12 + Node LTS, binds all three roots, backend venv/deps from `mjt-pub-api/requirements/dev.txt`, ports published to LAN, no Stripe-CLI.
- `dev.sh` — API :8000 + static :8080, prefixed output, clean shutdown, venv fail-fast guard.
- `README.md` / `VERIFY.md` — open-and-run guide + verification log.
- `index.html` — temporary placeholder in **this** frontend repo (primary, committed `ea659f8`), marked replaced-in-M4.
- `mjt-pub-api` (shared): bind-mounted only, no code edits.

**Review status:** Principal.CodeReview → **APPROVED**, no REQUIRED changes. Two SUGGESTED items (CR-1 casing, CR-2 dev.sh venv guard) implemented in Staff.ReviewReconciliation (workspace repo `1d7b25c`); no re-review needed. Writer.DocumentationUpdate refreshed the root README for M1.

**Commits:** workspace repo `1f9c1aa` (scaffold), `1d7b25c` (review fixes); primary repo `ea659f8` (placeholder).

**Acceptance criteria — verify:**
- [x] Workspace folder is a git repo, `origin` = confirmed remote (push deferred, Q-001). — agent-verified
- [x] `.code-workspace` valid JSON, exactly three roots + correct paths, ports 8000/8080, no Stripe/LLM tasks. — agent-verified
- [x] `devcontainer.json` valid JSON, mounts three roots; postCreate/postStart present+executable+LF, install from `requirements/dev.txt`, no Stripe-CLI. — agent-verified
- [ ] **Backend venv usable + `python manage.py check` inside the rebuilt container.** — ⚠ PENDING LIVE REBUILD (human)
- [ ] **`dev.sh` starts :8000/:8080, Ctrl+C stops both cleanly, both URLs respond.** — ⚠ PENDING LIVE REBUILD (human)
- [x] Placeholder `index.html` in frontend repo, marked temporary. — agent-verified
- [x] Workspace `README.md` + `VERIFY.md` document open-and-run + verification log. — agent-verified

The two ⚠ items are the known documented gap (Q-002): the agent cannot drive interactive "Reopen in Container" on the Windows host. **This is exactly what the human runs at this gate.** Record the outcome of the live rebuild in the workspace repo's `VERIFY.md`.

**Human action checklist:**
1. Rebuild in the devcontainer ("Reopen in Container"), then run `dev.sh`.
2. Confirm the backend venv is usable, `python manage.py check` passes against `mjt-pub-api`, both `http://127.0.0.1:8000/` and `:8080/` respond, and Ctrl+C stops both cleanly.
3. Record the result in the workspace repo `VERIFY.md`.
4. Enter the decision:

**If APPROVED — update `plans/state.json`:**
- `last_action` = `{ action_id: "Human.PhaseApproval", result: "approved", summary: "<note live rebuild passed>" }`
- `next_action_id` = `"PM.AdvancePhase"`
- `pause_type` = `"continue"`
- STATUS.md: SKIP (`status_updates = pm_only`).
- Commit with a plain human-readable subject (NOT `--AUTO-`), e.g. `Approve milestone B1-M1: workspace/devcontainer scaffolding`.

**If CHANGES REQUIRED — update `plans/state.json`:**
- `last_action.result` = `"changes_required"`
- `next_action_id` = `"Staff.ReviewReconciliation"` (or `"Staff.ImplementationExecution"` if the fix is substantial)
- Add feedback to `plans/thread.md`; STATUS.md SKIP (pm_only).

**Note for the in-container rebuild:** this chat will not survive the rebuild — this brief and instructions live here in `thread.md` (committed) so they're available inside the container.