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

`size: full` and the M1–M5 structure unchanged, per the human's note. No remaining REQUIRED changes. Risks R-1/R-2/R-3 from pass 1 still stand for M1–M3 planning awareness.

---
### Human.ApproveBuild — 2026-09-06 (pass 2)
**Decision: APPROVED** — BUILD.md (pass 2) accepted. All three change requests verified applied (vanilla static-site stack; `stencil-bible-guides` reframed as reference-to-adapt; S-1/S-2/S-3 folded into BUILD.md/BACKLOG). Routing to PM.StatusUpdate, then Principal.MilestonePlan.

**Resolves VISION §0 open item — workspace repo confirmed by human:**
- GitHub remote (already created, empty): `https://github.com/michaeljthacker/workspace-AreSalmonAtBallardLocks.git` (repo name keeps the `workspace-` prefix, since the unprefixed name is taken by this frontend repo).
- Local folder: `C:/Users/Micha/DevSpace/workspaces/AreSalmonAtBallardLocks` (unprefixed dir name — intentional; local dir name need not match the remote repo name).
- M1 approach: create the local `workspaces/AreSalmonAtBallardLocks` folder, then `git init` / add the above URL as `origin`. No longer "pending human confirmation" — M1 should treat this as decided. (This should be captured as a decision in DECISIONS.md during M1 planning/execution.)