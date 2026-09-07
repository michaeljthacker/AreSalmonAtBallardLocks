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

---
### Human.ApproveMilestone — 2026-09-07 — changes_required
Human reviewed the 6-phase B1-M2 plan and requested it be shrunk before execution.

**Rejected — P1 as a code-free phase.** "No code" does not justify the administrative overhead of a full SAM phase. Merge P1 into P2. Target **3 phases** for the whole milestone if plausible.

**Approved as planned:**
- `ImportRun` third table stays (P6 as drafted).
- Turnstile / real bot resistance stays deferred in BACKLOG P1.

**Changed — report endpoint protection.** Human *does* want the public write key, with a stated purpose I had planned against: it is a **minor speed bump against casual/idle posting**, not a defense against a determined spammer. My "a secret in a public static page protects nothing" objection answered the wrong threat model. Also: **throttle harder than a default anon rate** — a genuine visitor should click the button roughly once per visit to the Locks, so the rate can be far tighter than a normal API endpoint's.

**Corrected — shared-repo branch caution was unfounded.** MILESTONE.md P2/Notes warned to rebase `feat/salmon-ballard-locks` on `main` and to check for migration-number collisions from other projects' in-flight branches. `git diff --stat main..HEAD` shows the only difference is this project's own STANDARDS.md promotion commit. No other project is contending for this branch. Removing both cautions; the standing `plans/STANDARDS.md` branching rule is unaffected (it governs where feature work *starts*, which was already satisfied).

Routing back to Principal.MilestonePlan to re-draft at 3 phases.

---
### Staff.DraftQuestions — 2026-09-07

Next execution unit: **B1-M2-P1** — source inspection, then `apps/salmon` models, migrations, admin (shared scope: `mjt-pub-api` on `feat/salmon-ballard-locks`; `docs/data-sources.md` in this repo).

The build half of P1 is well specified. The questions below are all about the *schema* half — each one is a fork the inspection cannot resolve on its own, and P1's own plan calls the constraint, the species vocabulary, and the URL prefix one-way doors. Q-003 and Q-005 in particular are model-field decisions, so they must be settled before `models.py` is written rather than discovered in P2/P3.

**Q-003 — Do aggregate/"total" rows get stored in `FishCount` at all, and is steelhead in the canonical vocabulary?**
Blocking: **Yes.** The Ballard Locks series conventionally reports per-species ladder counts alongside a season/period total, and it reports steelhead (not a salmon) in the same table. If a `TOTAL` pseudo-species and per-species rows coexist under the same `(date, species, ...)` constraint, every `SUM(count)` in P2's `counts/` and `seasonality/` endpoints double-counts, and the bug is invisible until the numbers are wrong on the public page. Options: (a) reject aggregate rows at import and derive totals in SQL; (b) store them under a reserved species value that every read endpoint must explicitly exclude. Ruling needed on both the aggregate question and whether steelhead is a first-class vocabulary member, since M3's answer is about *salmon*.

**Q-004 — Is `count` the value as published, or a derived daily figure?**
Blocking: **Yes.** If the source publishes a cumulative season-to-date number rather than a daily increment, then `count` means two different things depending on which the importer writes, and P2's `seasonality/` per-bucket totals are only meaningful for one of them. Preference is to store exactly what the source published (auditable against `source_url`) and derive deltas at read time, but this needs to be an explicit ruling recorded in `plans/DECISIONS.md` alongside the constraint, because it is equally expensive to reverse once P2 loads the history.

**Q-005 — How does a hand-corrected `FishCount` row survive the next importer run?**
Blocking: **Yes.** P1 registers both models in admin specifically so "the handful of anomalies VISION §5 anticipates" can be corrected by hand, and P3's importer upserts against the same constraint — so as drafted, a correction is silently reverted on the next scheduled run. Either the importer must never update an existing row (insert-only, which P3's backfill-tolerance criterion may already imply), or `FishCount` needs a field marking a row as manually corrected and the importer must skip those. The second is a model field, which makes this a P1 decision.

**Q-006 — What history depth should the bootstrap target?**
Blocking: No. VISION §5 says "best available public source" without bounding years, and the Locks series runs decades deep. Depth drives the size of P2's committed fixture and the year coverage `seasonality/` can report. Requesting a target (all available vs. a bounded recent window such as the last 10–15 years) so P1's report can name it rather than leaving P2 to pick.

**Q-007 — If the live sources cannot be reached from the devcontainer, does P1 block or proceed with a documented gap?**
Blocking: No. P1's acceptance criteria require per-source field names, species vocabulary, granularity, history depth, and observed backfill behavior — all of which are claims about live pages, and the standing `plans/STANDARDS.md` verification rule forbids substituting an unverified path for a container run. Asking for the ruling in advance so it isn't improvised mid-phase: block on network access, or record the unreachable sources as an explicit gap in `docs/data-sources.md` and proceed on documented knowledge.

---
### Principal.AnswerQuestions — 2026-09-07

All five questions ruled on; P1 is unblocked. Three rulings are model-field decisions and are recorded in `plans/DECISIONS.md`; two are milestone details and go to `plans/MILESTONE.md`. Q-005's answer adds two fields VISION §4.2 does not list — that is deliberate and noted below.

**Q-003 — Aggregates are never stored; steelhead is stored but is not a salmon.**

*Aggregates:* option (a). `FishCount` stores **only atomic per-(date, species) observations**. A published season/period total is parsed, used as a checksum, and then discarded — never written as a row. Rejecting option (b) on purpose: a reserved `TOTAL` species that every read endpoint must remember to exclude is a correctness landmine whose failure mode is a silently inflated public number, and each new consumer (M3's forecast, M5's charts) is a fresh chance to forget the filter. Derived values get derived.

Enforce this structurally rather than by convention, because the admin is hand-editable and the importer is machine-written:
- `species` is a `TextChoices` in `constants.py` with **no aggregate member**, plus a DB-level `CheckConstraint` restricting `species` to the vocabulary. A `TOTAL` row then cannot be inserted by a buggy parser or a mis-click in admin, not merely shouldn't be.
- The importer must **compare the source's published total against the sum of its own parsed per-species rows** and fail the run loudly on mismatch. That converts the discarded total into a parser self-check instead of throwing the information away — it is the cheapest available detector for "the source changed its table shape."

*Steelhead:* yes, a first-class vocabulary member — stored, not dropped. Dropping is lossy and irreversible (recovering it means re-extracting years of history), storing costs nothing, and M5's seasonality charts and Sources page can legitimately show it as context. But it is not a salmon and must never enter the salmon answer, so the distinction is a named constant, not a per-query literal: `constants.py` carries the full observed vocabulary **plus a separate explicit `SALMON_SPECIES` tuple** (the three VISION §21.1 species) that every salmon-facing aggregate filters on. M3's answer is about salmon; `SALMON_SPECIES` is what makes that checkable in one place.

*Catch-all:* an `OTHER` member for unrecognized labels, with the raw published label preserved in `source_metadata`. `OTHER` is in the vocabulary but **not** in `SALMON_SPECIES`, so an unknown label can never inflate the salmon number. The importer maps unrecognized labels to `OTHER` and continues (VISION §6 tolerance) but must name them in the `ImportRun` message, so a vocabulary change gets noticed rather than absorbed.

The concrete member list stays P1's to write after inspection — P1's acceptance criterion already requires the vocabulary entry to name the source data that decided it, and I am not going to pre-empt that with a list I have not verified. What is recorded now is the structural rule that does not depend on what the inspection finds.

*Breadcrumb:* this makes `species` a closed, DB-enforced vocabulary — adding a species later is a migration. That is the intended tradeoff, not an oversight: a new species at the Locks is a schema-level event worth being forced to notice.

**Q-004 — `count` is the daily increment, always. The raw published value is preserved alongside it.**

`count` means "new passage counted for this species on this date" in every row, unconditionally. If the source publishes cumulative season-to-date figures, the importer **normalizes to daily at write time**; if it already publishes daily (the likely case for the Locks ladder tables), normalization is the identity and this ruling costs nothing.

This overrides the preference stated in Q-004 ("store exactly what the source published"), and I want the reason on the record because it is the reverse of the usual store-raw/transform-on-read default:
- Deltas computed from stored cumulative rows are wrong across any gap — a missing publication day silently folds its passage into the next day's delta, with no way to detect it after the fact.
- VISION §21.3 explicitly requires distinguishing "no published data" from "a reported count of zero" and forbids interpolation. Cumulative storage makes that distinction unrepresentable.
- Source revisions shift every subsequent cumulative value, so P3's "insert what's missing" comparison would become "update whatever changed" — which runs straight into Q-005.
- Three separate consumers (the `counts/` endpoint, M3's forecast, M5's charts) would each have to re-implement delta logic identically and correctly.

Auditability is preserved without coupling `count`'s meaning to the source's presentation format: the row keeps `source_url`, and `source_metadata` carries the raw published figures (published daily and/or published cumulative, plus the raw species label). For the historical bootstrap, P2's committed fixture is itself the audit trail. So we get the audit without the ambiguity.

*Zero vs. missing:* a published zero is stored as a row with `count = 0`. A date with no publication gets **no row at all**. Never insert a placeholder zero — that rule is what makes §21.3 satisfiable downstream.

*One-way door:* yes. Reversing this after P2 loads the history means migrating every row. Recorded in `DECISIONS.md` accordingly.

**Q-005 — A `manually_corrected` latch the importer must not cross. Not insert-only.**

`FishCount` gets `manually_corrected` (bool, default `False`) and `correction_note` (text, blank). The importer upserts normally but **skips any row where `manually_corrected` is `True`**.

Rejecting insert-only: VISION §6 says the source may publish late, backfill, or revise. If the importer can never update an existing row, a revised official figure can never land, and we would serve a superseded number permanently with no path to correct it except by hand — strictly worse than the problem being solved. The importer needs to be able to update; it just needs one thing it will not overwrite.

Make the audit trail non-optional with a `CheckConstraint`: `manually_corrected = False OR correction_note != ''`. A latched row that disagrees with the source and carries no stated reason is precisely the artifact that confuses someone six months from now. One line, structural, done.

P3 must also count latched-and-skipped rows in the `ImportRun` message. A correction that the source has since fixed should eventually be un-latched by a human; surfacing the count is enough for M2, and no dashboard is in scope.

Staff's read is correct that this is a P1 decision. Note that it adds two fields beyond VISION §4.2's suggested list — §4.2 is explicitly a suggestion and the admin-correction workflow it does not anticipate is mandated by P1's own plan, so this is a deliberate extension. P1 and P3 acceptance criteria updated in `MILESTONE.md`.

**Q-006 — Take all readily available years; floor of 10 complete years, cap at ~15 if each year costs a separate manual extraction.**

If the source exposes its archive cheaply (one download, or one table/CSV per year), take everything it has. If each additional year is a separate hand extraction, stop at the most recent 15 and record the cutoff and the reason in `docs/data-sources.md`.

The floor is statistical, not budgetary: §21.1's seasonality curve and §21.2's "this year vs. typical" comparison are per-day-of-year averages, and under roughly 10 years a single anomalous run year visibly distorts a weekly bucket. The soft cap is also not budgetary — beyond ~15–20 years, run timing has genuinely shifted (hatchery policy, the Lake Washington sockeye decline), so the oldest years arguably degrade the prior rather than smoothing it. Either way, depth is bounded by extraction effort and data relevance, **not** by storage: four species across a roughly June–November publication season for 15 years is well under 15k rows.

*One note forward to P2:* at that row count a Django `loaddata` JSON fixture is needlessly bulky. `MILESTONE.md` P2 already specifies a custom `load_historical_fish_counts` command rather than `loaddata`, so commit the data as **CSV** and read it in the command. Don't reach for JSON out of habit.

**Q-007 — Proceed; block only if *no* source can be verified live. Egress is confirmed working.**

I checked from this container before ruling: `https://wdfw.wa.gov/` returns 200 and the Socrata catalog API is reachable, so general outbound HTTPS works and the premise of the question is mostly moot. `www.nwd.usace.army.mil` returned 403, which is a WAF/user-agent rejection rather than a network block — a normal browser user-agent is the first thing to try, and if a specific source stays blocked that is a **source finding to record**, not an environment failure.

The split:
- **Egress works, one candidate source unreachable or shape-changed** → first-class inspection finding. Record the exact URL, status code, and observation date in `docs/data-sources.md`, and proceed on the sources that did respond. P1 needs only *one* authoritative series to settle the constraint.
- **No source verifiable live at all** → stop and raise a blocker. Do not write a constraint or a species vocabulary from recollection. Those are exactly the one-way doors P1 exists to close, and the standing verification rule in `plans/STANDARDS.md` forbids substituting an unverified path for a real one.

Separately: the `pytest` / `makemigrations --check` / `migrate` verification has no network dependency and must still run in the container regardless. No exceptions there.

**Recorded to `plans/DECISIONS.md`:** the atomic-observations-only rule with the `SALMON_SPECIES` subset (Q-003), `count` as daily increment with raw values in `source_metadata` and no placeholder zeros (Q-004), and the `manually_corrected` latch (Q-005). **Recorded to `plans/MILESTONE.md`:** history depth and CSV fixture format (Q-006), the live-verification ruling (Q-007), and the two new `FishCount` fields in P1/P3 acceptance.

*Breadcrumb:* "never store aggregate rows alongside atomic rows in the same table" is plausibly portable to any `mjt-pub-api` app that imports a time series, so it is a future promotion candidate for the shared `STANDARDS.md`. Leaving it as a project decision for now — there is exactly one instance, and promoting on first sighting is how a standards file fills up with speculation. `PM.ThreadMaintenance` can propose it later if a second case appears.

---
### Staff.ImplementationExecution — 2026-09-07

**Review Request — B1-M2-P1** (source inspection, models, migrations, admin)

**What was implemented**

Inspection first, then the schema it decided.

*Inspection.* Verified live from the devcontainer on 2026-09-07. The authoritative series is WDFW's "Lake Washington salmon counts" page, and behind its on-page chart sits an undocumented JSON feed (`pssp-count.wdfw-fish.us/salmon_counts_ballard.json`, found in the page's `drupal-settings-json` blob) carrying **17 seasons of daily sockeye counts in one download**. Full findings in `docs/data-sources.md`.

*Build.* `apps/salmon` with the standard layout, in `INSTALLED_APPS`, `/salmon/` wired into the root URLconf with empty `urlpatterns`. `SightingReport` and `FishCount` per VISION §4.1/§4.2 plus the two Q-005 correction fields. Three DB-level constraints, all verified present in the generated DDL: unique `(date, species)`, `species` restricted to the vocabulary, and a correction note required whenever `manually_corrected` is set. Both models in admin — `FishCount` editable for anomaly correction, `SightingReport` read-only.

**Findings that change downstream plans — the important part of this entry**

1. **Chinook and coho have no obtainable multi-year daily history.** The JSON feed is **sockeye only** and the HTML page carries **current season only**. So P2's bootstrap will produce ~15 sound years of sockeye against **one season** of Chinook and coho. Getting more means a separate hand extraction per year per species from archived snapshots — exactly what the Q-006 soft cap exists to prevent. No schema impact (`(date, species)` handles uneven depth fine), but **M3's per-species seasonality baseline for Chinook and coho will rest on a single year**, and M5's charts will show it. P2/M3 should plan for this rather than discover it.

2. **The JSON's year keys are relative, not calendar.** `count_Nyear` means `current_year − N`, and `count_current` is this year — so `count_1year` is *last* year, and the same key name means a different calendar year next season. Verified, not assumed: summing each series over June–August and comparing against the independent annual-totals table puts the 2017 and 2013 spikes (129k and 177k against a ~25k baseline) at exactly `count_9year` and `count_13year`; every off-by-one alternative fails by an order of magnitude.

3. **Blank cells are pre-rendered for the entire season and must not be read as zero.** The page emits a row for every date up front. The coho table is the clean proof — blank daily cells sitting next to a carried-forward running total. Reading blanks as zeros would manufacture ~30 fake zero-passage days per species per season, which is the exact conflation VISION §21.3 forbids.

4. **Range rows exist and cannot be stored.** The first row of the Chinook and coho tables is a multi-day bucket (`6/12-8/31` = 420 coho). `FishCount.date` is a single day, so these are skipped — accepted data loss, because the alternatives are interpolation (forbidden) or a fake single-day spike. P3 must name skipped range rows in `ImportRun` rather than drop them silently.

5. **The recent-window question dissolved.** The page serves the whole current season in one document and states twice that published counts are preliminary and subject to revision. So the answer is **re-parse the full current season every run** — a rolling N-day window costs the same single request and deliberately ignores revisions the source warns about. 212 rows as observed.

6. **A better checksum than expected.** Q-003 anticipated a season total; the source gives a per-row `Running Total`, so the check can be per date (`running_total[n] − running_total[n−1] == daily_count[n]`), catching a parser error the day it appears instead of at season end.

**Two prior assumptions corrected** (both recorded in `docs/data-sources.md`; the first also annotated on the DECISIONS entry it affects, to avoid leaving a standing contradiction):
- **Steelhead is not published at this ladder.** Q-003 made it a first-class vocabulary member on the assumption it shared the source table. It does not appear in either source, so no `steelhead` member was created — a vocabulary member for nonexistent data is speculation frozen into a DB constraint. The structural half of the ruling stands and is implemented: `SALMON_SPECIES` remains a named subset distinct from the full vocabulary, so a future non-salmon species becomes a member without becoming a salmon.
- **`(date, species)` is the constraint, and the evidence made it stronger than "only one series exists."** The two retrieval routes *overlap* on current-season sockeye, so including `source` in the key would let one real-world observation insert twice and inflate every `SUM` — the exact failure mode the atomic-observations decision exists to prevent.

**Key files changed**
- shared scope (mjt-pub-api): `apps/salmon/` — `models.py`, `constants.py`, `admin.py`, `apps.py`, `urls.py`, `serializers.py`/`views.py` (documented stubs, P2 fills), `migrations/0001_initial.py`, `tests/test_models.py`, `tests/test_admin.py`
- shared scope (mjt-pub-api): `mjt_pub_api/settings.py` (one `INSTALLED_APPS` line), `mjt_pub_api/urls.py` (one `urlpatterns` line) — the two append-only files flagged in MILESTONE Notes as `feat/bible-guides` conflict points
- project scope: `docs/data-sources.md` (new, 313 lines), `plans/DECISIONS.md` (2 new entries + 1 amendment)
- Commit: `a709172` on `feat/salmon-ballard-locks`. Not pushed.

**Acceptance criteria**
- [x] `docs/data-sources.md` records per source: stable URL, format, field names/types, species vocabulary, granularity, history depth, cadence, revision/backfill behavior, known gaps, attribution/terms
- [x] States one authoritative series with the evidence; names S1 (all species) and S2 (sockeye history) for P2/P3; states the recent-window size (full current season) derived from observed revision behavior
- [x] `plans/DECISIONS.md` carries the `(date, species)` choice and the vocabulary incl. the `other` catch-all, each naming the source data that decided it, each with its "Why this matters long-term" line
- [x] `apps/salmon` has the standard layout, is in `INSTALLED_APPS`, `/salmon/` included in `mjt_pub_api/urls.py`
- [x] `SightingReport` matches §4.1 field-for-field (asserted by test); `FishCount` matches §4.2 plus the two Q-005 fields and no others; carries the `UniqueConstraint`; both reference `constants.py`
- [x] `makemigrations --check --dry-run` → "No changes detected"; `migrate` applies cleanly on a genuinely fresh DB (dev sqlite moved aside, then restored and re-migrated)
- [x] Both models registered in admin; both change lists render 200
- [x] History depth recorded: 17 seasons sockeye (2010–2026) from one download, ~15 sound after exclusions; Chinook/coho current season only, with the reason
- [x] `pytest apps/salmon` — 24 passed. Covers duplicate-`FishCount` violation (varying only `source`, proving provenance ≠ identity), nullable `quantity`/`species`, negative `count` rejected, out-of-vocabulary `species` rejected at the DB level, `manually_corrected=True` with empty note rejected
- [x] No throwaway inspection scripts committed — all inspection ran from `/tmp`; `git status` clean after commit

**Risks / trade-offs**
- **Full `pytest` suite not run this phase** — deferred to milestone end per human direction mid-phase. Honest caveat: this phase *did* change two files outside `apps/salmon` (the additive `INSTALLED_APPS` and `urlpatterns` lines). Both are exercised by `manage.py check`, which passes, and by app loading in the 24 salmon tests. The residual untested risk is cross-app interaction, which is what P3's full-suite criterion covers.
- **`other` + `(date, species)` can collide.** Two *different* unrecognized labels on the same date both map to `other` and contend for one row. P3 must treat that as a loud error, not a silent overwrite. Flagged for P2/P3; no P1 schema change proposed, since widening the key to fix it would reintroduce the double-counting this constraint exists to prevent.
- **S2's 2016 is unexplained.** 81 rows summing to 23,834 against an annual total of 58,583. The plausible reading is a run extending past the file's August 31 cutoff, but that is unverified. Recorded as suspect; P2 should quarantine it at bootstrap rather than average it in.
- **2022 is half-missing** from S2 (38 of 86 rows). Exclude, don't interpolate.
- **`robots.txt` note for P3.** WDFW's `User-agent: *` group does not disallow the counts path, but the file does carry `Disallow: /` groups naming AI-training crawlers including `anthropic-ai`. P3's importer must send an honest project-identifying User-Agent. Disclosed in `docs/data-sources.md`: a browser User-Agent was used during inspection to probe the USACE WAF, and the committed importer must not carry that forward.
- **USACE page returns 403** (WAF, both default and browser User-Agent). Per Q-007 that is a source finding, not an environment failure — S1 and S2 both returned 200 from the same shell. Nothing is lost; WDFW is the counting authority. USACE still needs attribution on M5's Sources page as ladder operator.
- **No open data license.** WDFW pages carry a bare "all rights reserved" footer with no terms for these tables. Stance taken: store counts as facts, always attribute WDFW + Muckleshoot Indian Tribe, always link the source, never republish the pages. Worth a human sanity check before M5 ships publicly.

---
### Staff.ImplementationExecution — 2026-09-07 (correction)

**Correcting finding 1 of the P1 review request above. It was wrong.** Human
challenged it ("There's no other source of data for the various species? This
is a MAJOR change vs. expectation") and the challenge was right — I had
concluded "no obtainable multi-year daily history for Chinook and coho" after
checking only four candidates, and never checked the obvious fifth.

**Archived snapshots of the WDFW page do carry complete multi-year daily
tables for all three species.** The page is rewritten each season but is not
truncated at season end, so a post-season snapshot holds that year's full,
fully-populated tables. Verified by fetching and parsing seven of them
(2019–2025): the 2024 snapshot's sockeye running total ends at 23,188,
matching the independent annual-totals table for 2024 exactly.

Corrected coverage:

| Species | Seasons | Route |
|---|---|---|
| Sockeye | 17 (2010–2026) | PSSP JSON, one download |
| Chinook | 7 (2020–2026) | archived snapshots, one fetch per year |
| Coho | 8 (2019–2026) | archived snapshots, one fetch per year |

So "one season" was wrong by a factor of seven or eight. Cost is one HTTP
fetch per year, programmatic — **not** the per-year-per-species manual
extraction that the Q-006 soft cap exists to prevent, which is the specific
reasoning error: I invoked that cap without checking whether the cost it
guards against was actually the cost in front of me.

Chinook and coho still fall short of Q-006's 10-year floor (7 and 8), so the
floor question is live but is now a near-miss rather than a wall.

**Also ruled out along the way:** the PSSP host has exactly one other feed
(`salmon_counts.json`), and it is the Baker River trap — a different project.
So the JSON route really is sockeye-only, as originally stated.

**New unexplored lead, deliberately left open.** The legacy pre-redesign WDFW
site had a counts section at `wdfw.wa.gov/fishing/counts/sockeye/` with
archive records back to **2010**, including `archives.html` plus
`chinook_chart.jpg` and `coho_chart.jpg`. Not fetched. If `archives.html`
holds tables it could push Chinook/coho past the 10-year floor; if the only
artifacts are chart JPEGs it is unusable. Worth an hour before P2 writes the
bootstrap — not a blocker, since 7–8 seasons is enough for P2 to proceed.

**Known limits of the archived route** (recorded in `docs/data-sources.md`):
coho publishes daily only from ~9/1 each year with the earlier run folded
into an unstorable range row; the page's shape drifts across years (table
`id`s absent before ~2025, heading order changes, four date formats, and the
2019 coho table has four columns instead of three), so the bootstrap needs a
per-year parser with per-year row-count and running-total validation rather
than one parser assumed to fit all years.

**No code or schema change.** `(date, species)` and the vocabulary are
unaffected — uneven per-species depth was always fine, and the three species
are unchanged. The P1 commits stand as reviewed. What changed is P2's
bootstrap scope (it now has a real Chinook/coho source to load) and M3's
baseline, which no longer rests on a single year for those two species.

**Session paused here at human request.** Picking up in the morning. State is
unchanged: still routing to `PM.StatusUpdate` for B1-M2-P1, nothing pushed.

---
### PAUSED — Project shelved 2026-09-07

Human decision: **shelve the project**, on the grounds that less quality data
is available than the concept assumed. This entry is the pick-up point. No
further SAM actions should run until a human un-shelves.

## Why it stopped

The B1-M2-P1 source inspection was the first step in this Build that made
contact with the real data, and the data is thinner than VISION assumed. It is
worth being precise about *which* part is thin, because it is not all of it:

| Species | Daily history obtainable | Route |
|---|---|---|
| Sockeye | **17 seasons** (2010–2026) | one JSON download |
| Chinook | 7 seasons (2020–2026) | one archived fetch per year |
| Coho | 8 seasons (2019–2026) | one archived fetch per year |

- **Sockeye is genuinely well served** and on its own clears the 10-complete-
  year floor that VISION §21.1's seasonality curve and §21.2's "this year vs.
  typical" comparison need.
- **Chinook and coho do not clear that floor** — 7 and 8 seasons — and coho is
  thinner than the season count suggests: every year publishes coho daily
  counts only from ~September 1, with the earlier run folded into a single
  multi-day range row that cannot be attributed to any date.
- **There is no second authoritative source to fill the gap.** One count
  series exists (WDFW with the Muckleshoot Indian Tribe at the Ballard Locks
  ladder). USACE operates the ladder but does not publish counts and its site
  returns 403. The one other feed on WDFW's counts host is the Baker River
  trap — a different watershed. Details per source in `docs/data-sources.md`.

The product promise is a 7-day forecast of **total salmon**, which means all
three species. A forecast whose sockeye component rests on 17 years and whose
Chinook and coho components rest on 7 and 8 — with coho blind before
September — is a weaker product than the concept described, and VISION §3.3
explicitly forbids implying precision the data does not have.

**One lead was left unexplored and is the first thing to check on un-shelving.**
The legacy pre-redesign WDFW counts section, `wdfw.wa.gov/fishing/counts/sockeye/`,
is archived back to **2010** and contains `archives.html` alongside
`chinook_chart.jpg` and `coho_chart.jpg`. It was never fetched. If
`archives.html` holds tabular data it plausibly lifts Chinook and coho over
the 10-year floor and removes the reason for shelving; if the only artifacts
are chart images, it confirms it. **This is a roughly one-hour check and it
determines whether the project is viable as conceived.** Do it before
re-planning anything.

## What exists and works

B1-M1 (workspace/devcontainer scaffolding) is complete and approved.
B1-M2-P1 is implemented, committed, and **passing** — but has **not been
code-reviewed or human-approved**, because `code_review = every_milestone` and
M2 has two more phases.

Shared repo `mjt-pub-api`, branch `feat/salmon-ballard-locks`, commit
`a709172` — **not pushed**:
- `apps/salmon/` — `SightingReport` and `FishCount` models, `constants.py`
  (closed species vocabulary + `SALMON_SPECIES` subset), admin for both,
  `migrations/0001_initial.py`, 24 passing tests. `serializers.py`/`views.py`
  are documented stubs; `urls.py` has empty `urlpatterns`.
- Three constraints verified present in the generated DDL: unique
  `(date, species)`, `species` restricted to the vocabulary, and a required
  correction note whenever `manually_corrected` is set.
- `mjt_pub_api/settings.py` and `mjt_pub_api/urls.py` — one additive line each.

Project repo, `main`, commits `fb13a04` / `8cf2567` / `83e2c37` — not pushed:
- `docs/data-sources.md` — the full source inspection, and the most valuable
  artifact produced by this Build. Independently useful even if the project
  never resumes.
- `plans/DECISIONS.md` — the `(date, species)` and species-vocabulary rulings.

Verification status at the pause: `pytest apps/salmon` 24 passed;
`makemigrations --check` clean; `migrate` applied to a genuinely fresh
database; `manage.py check` clean. The **full backend suite was deliberately
not run** — deferred to milestone end per human direction, and P1 did touch
two files outside `apps/salmon`.

## What was never built

- **B1-M2-P2** — write + read endpoints, and the one-time historical
  bootstrap. Not started.
- **B1-M2-P3** — the scheduled idempotent importer. Not started.
- **B1-M3** — aggregation rule and 7-day forecast. This is the milestone the
  data shortfall actually threatens.
- **B1-M4** — frontend MVP. The `index.html` placeholder from M1 is untouched.
- **B1-M5** — seasonality visualizations, Sources/Methodology pages, deployment.

## Routing state at the pause

`plans/state.json` is left **exactly where P1 finished**, deliberately not
edited into any paused state — SAM has no shelved `pause_type`, and inventing
one would corrupt the schema:

- `build_id: B1`, `milestone_id: M2`, `phase_id: P1`
- `next_action_id: PM.StatusUpdate`, `pause_type: continue`, `blockers: []`

So a naive "run the next action" **will resume the Build** by writing a status
update. That is the intended behavior if the project is un-shelved and nothing
has changed. If the shortfall changes the plan instead, do not run
`PM.StatusUpdate` — go to `Principal.MilestonePlan` (or re-open VISION) after
checking the legacy-archive lead above.

## Open questions carried forward

1. **Does the legacy archive hold tables or only images?** Decides viability.
2. **Is a sockeye-strong / Chinook-coho-weak forecast still the product?**
   Options if the legacy lead fails: narrow the promise to sockeye (which the
   data fully supports), keep all three but disclose per-species confidence,
   or drop the forecast and ship the current-status answer plus seasonality
   only. This is a VISION-level product call, not a plan-level one.
3. **`other` + `(date, species)` can collide** — two different unrecognized
   labels on one date contend for one row. P3 must error loudly rather than
   overwrite. Unresolved, no code affected yet.
4. **No open data license.** WDFW pages carry a bare "all rights reserved"
   with no terms for these tables. The stance taken (store counts as facts,
   always attribute WDFW + Muckleshoot Indian Tribe + USACE, never republish)
   deserves a human sanity check before anything ships publicly.
5. **`feat/bible-guides` conflict.** `settings.py` and `urls.py` are
   append-only conflict points between that branch and this one; the longer
   `feat/salmon-ballard-locks` sits unmerged and unpushed, the likelier the
   collision.
