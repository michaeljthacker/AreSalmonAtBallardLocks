# MILESTONE — B1-M2

## Goal
Build the backend data layer in `mjt-pub-api`: the `sighting_report` + `fish_count` models (source data inspected first), the report-submission and read endpoints, a one-time historical bootstrap, and a scheduled idempotent importer.

## Scope note
Backend **only**. No aggregation rule, no forecast, no real frontend — M3 computes current-status and the 7-day forecast on top of these endpoints, M4 builds the UI, M5 confirms deployment. M2 delivers durable local data plus the reads M3–M5 query. The placeholder `index.html` from M1 is untouched.

## Known facts (decided, do not re-litigate)
- **All M2 code is shared scope** — it lands in `mjt-pub-api` (`../../Projects/mjt-pub-api`, a registered `shared_repo`) on `feat/salmon-ballard-locks`. That repo gets **no `plans/` directory**. Project-scoped decisions *about* this backend code (notably the uniqueness constraint) go in this repo's `plans/DECISIONS.md`.
- **Environment:** devcontainer-first. Verification (`pytest`, `manage.py check`, `makemigrations --check`) runs inside the container against `mjt-pub-api/requirements/dev.txt`.
- **Backend stack:** Django 5.2 + DRF + drf-spectacular, Python 3.12, `apps/<name>/` layout, `pytest` with `--strict-markers` and the markers already declared in `pytest.ini`. Prod DB is Postgres on Heroku; scheduled jobs are management commands under Heroku Scheduler (precedent: `docs/DEPLOYMENT_DIGEST.md`).
- **Precedent for the public write endpoint:** `apps/analytics` `EventCreateView` — `AllowAny` + `authentication_classes = []` + throttle + optional shared-secret header, posture overridden per-view and never globally.
- **The write key is in scope** (human-confirmed 2026-09-07). Its purpose is a **minor speed bump against casual/idle posting**, not defense against a determined spammer. Real bot resistance (Turnstile) stays deferred in BACKLOG P1.
- **Throttling is deliberately tight** (human-confirmed 2026-09-07): a genuine visitor taps once per trip to the Locks, so the anon rate is set far below a normal API endpoint's.
- **`ImportRun` is in scope** (human-confirmed 2026-09-07) as a third table beyond VISION §20's two, because §17 requires distinguishing "source published nothing" from "importer is broken."
- **Constraint choice is deferred to P1's first step by design:** `(date, species, source)` vs `(date, species)` is decided only after looking at real source data (BUILD.md In-scope; VISION §4.2).
- **Backend dependency remediation stays out of B1** (separate `fix/` branch off `main`; plan-scoped ruling carried forward from M1).

## Phases

### P1 — Source inspection, models, migrations, admin
**What:** Inspect the real data, then encode what it says — one continuous session, because the inspection's only purpose is to settle the schema.

*First, inspect.* Identify the public Ballard Locks / Lake Washington fish-count sources (WDFW's Ballard Locks publications and any Army Corps / co-manager series covering the same ladder) and record, per source: retrieval method and stable URL, format (HTML table / CSV / PDF), field names and types, the species vocabulary actually used, date granularity, history depth, publication cadence, whether the source backfills or revises published days, gaps/anomalies, and attribution/terms. Whether more than one authoritative series must be stored side by side is what decides the constraint. Throwaway fetch/inspect scripts are fine and are not committed. Findings go to `docs/data-sources.md` in **this** repo (project scope — also the raw material for M5's Sources page); the constraint and species-vocabulary rulings go to `plans/DECISIONS.md`.

*Then, build.* Create `apps/salmon` following the existing app layout (`apps.py`, `models.py`, `constants.py`, `admin.py`, `serializers.py`, `views.py`, `urls.py`, `migrations/`, `tests/`), register it in `INSTALLED_APPS`, and wire `path("salmon/", include("apps.salmon.urls"))` into `mjt_pub_api/urls.py` (empty `urlpatterns` is fine here).

- `SightingReport`: `reported_at`, `saw_salmon` (bool), `quantity` (nullable `TextChoices` band), `species` (nullable, canonical vocabulary), `created_at`. No identifying fields — VISION §4.1 defers anti-abuse/diagnostic metadata.
- `FishCount`: `date`, `species`, `count`, `source`, `source_url` (nullable), `source_metadata` (nullable JSON), `retrieved_at`, `created_at`, `updated_at`, plus `manually_corrected` (bool, default `False`) and `correction_note` (text, blank) — two fields beyond VISION §4.2's suggested list, added per the Q-005 ruling so P3's importer has something it will not overwrite. Carries the chosen `UniqueConstraint`, a `CheckConstraint` restricting `species` to the canonical vocabulary, a `CheckConstraint` requiring a non-empty `correction_note` whenever `manually_corrected` is set, and indexes sized for the actual reads (recent-window scans by `date`; per-species history scans for seasonality).
- Canonical species live in `constants.py` (precedent: `apps/homecare/constants.py`), with **no aggregate/`TOTAL` member**, an `OTHER` catch-all for unrecognized labels, and a separate named `SALMON_SPECIES` subset (the three VISION §21.1 species) that every salmon-facing aggregate filters on — steelhead is stored but is not a salmon (Q-003 ruling). Both models registered in Django admin so imported data can be eyeballed and the handful of anomalies VISION §5 anticipates corrected by hand.

*One-way door:* the uniqueness constraint, the canonical species vocabulary, and the `/salmon/` URL prefix are all expensive to reverse later — the first two mean migrating the whole history once P2 loads it, the third becomes public surface once QR stickers print in M5. Settle all three here, which is why inspection leads.

**Acceptance:**
- [ ] `docs/data-sources.md` exists in this repo and, per candidate source, records: stable URL, format, field names/types, species vocabulary, date granularity, history depth, publication cadence, revision/backfill behavior, known gaps, and attribution/terms.
- [ ] The report states explicitly whether one or more than one authoritative series must be stored, with the evidence; names the source(s) P2/P3 will use; and states the recent-window size P3's importer should re-fetch, derived from observed backfill behavior.
- [ ] `plans/DECISIONS.md` contains entries choosing `(date, species, source)` **or** `(date, species)` and fixing the canonical species vocabulary (including the catch-all for unrecognized labels), each naming the source data that decided it and carrying its "Why this matters long-term" line.
- [ ] `apps/salmon` exists with the standard app layout, is in `INSTALLED_APPS`, and `/salmon/` is included in `mjt_pub_api/urls.py`.
- [ ] `SightingReport` matches VISION §4.1 field-for-field; `FishCount` matches VISION §4.2 plus the two Q-005 correction fields and no others; `FishCount` carries the chosen `UniqueConstraint`; both reference `constants.py` species rather than free-text.
- [ ] `python manage.py makemigrations --check --dry-run` reports no missing migrations; `python manage.py migrate` applies cleanly on a fresh database.
- [ ] Both models are registered in admin and their change lists load (admin test, per `apps/analytics/tests/test_admin.py`).
- [ ] The report names the history depth actually obtained and, if the archive was truncated, the cutoff and the reason (target: all readily available years; floor of 10 complete years; stop at the most recent ~15 if each additional year costs a separate manual extraction).
- [ ] `pytest apps/salmon` passes with model tests covering: duplicate-`FishCount` constraint violation, nullable `quantity`/`species` on `SightingReport`, rejection of a negative `count`, rejection of an out-of-vocabulary `species` at the database level, and rejection of `manually_corrected=True` with an empty `correction_note`.
- [ ] No throwaway inspection scripts are committed to `mjt-pub-api`.

### P2 — Endpoints (write + read) and the historical bootstrap
**What:** The public API surface, plus the history that makes the reads worth calling. Grouped because every read endpoint's contract is only testable against real loaded data.

*Write.* `POST /salmon/reports/` — what a visitor's phone hits after scanning the QR code: anonymous, single-tap, fast. Mirror the `EventCreateView` posture (`AllowAny`, `authentication_classes = []` so anonymous cross-origin posts aren't rejected by session CSRF, `@extend_schema` docs) with a serializer accepting only `saw_salmon`, optional `quantity`, optional `species`. Two protections, both per human direction:
- A required write key via a `X-Salmon-Key` header, configured by env var (`env.example` entry, analytics precedent). A speed bump against idle posting — it is embedded in a public page and is not expected to stop anyone determined.
- A custom `AnonRateThrottle` subclass set **materially tighter than DRF's default** (a real visitor taps once per trip), with the rate as a named constant so it can be tuned without a code change.

`reported_at` is derived **server-side** and never trusted from the body — M3's current-status rule keys off report recency, so a client-supplied timestamp is a free way to poison the answer.

*Read.* All windows bounded by named constants (precedent: `DEFAULT_WINDOW_DAYS`/`MAX_WINDOW_DAYS` in `apps/analytics/views.py`); all responses carry explicit freshness meta, because §17's degradation depends on the frontend distinguishing "no data" from "stale data". Empty result sets return 200 with zeroed payloads and honest meta — never 404, never something the frontend special-cases.
- `GET /salmon/reports/recent/` — YES/NO totals over a bounded window, the most recent report timestamp, and enough time-bucketing for M3 to weight recent reports above old ones. Individual reports are **not** exposed.
- `GET /salmon/counts/` — official counts for a bounded date range, optional species filter, plus meta carrying the latest stored count date and its `retrieved_at`, so the frontend can print "Latest official count: September 3" rather than implying it is current.
- `GET /salmon/counts/seasonality/` — the historical baseline from stored rows: per-species totals per seasonal bucket across all stored years, plus the year coverage each bucket is computed from. A **raw historical aggregate, not a forecast or a prior** — M3 owns turning it into a prediction, M5's charts read the same endpoint. It lives here so M3 and M5 don't each invent their own.

*Bootstrap.* Load the historical series once. Per VISION §5 this is allowed to be unglamorous: extract/transform the public source by hand into a committed data file under `apps/salmon/fixtures/` (precedent: `apps/homecare/fixtures/`), loaded by a `load_historical_fish_counts` command that upserts against the chosen constraint. Commit the data as **CSV** read by the command, not as a `loaddata` JSON fixture — at the expected 10–15k rows JSON is needlessly bulky and the command is custom anyway. The committed file is the audit trail — it records exactly what was loaded, and makes the load reproducible on a fresh database without re-scraping a source that may since have changed. Supports `--dry-run`; writes real provenance (`source`, `source_url`, `retrieved_at`) on every row. Manual anomaly corrections get noted in `docs/data-sources.md` with reasons.

*Buy vs. build:* a hand-built one-shot loader rather than a general ingestion framework — VISION §20 warns explicitly against turning ingestion into a data platform.

**Acceptance:**
- [ ] `POST /salmon/reports/` accepts `{"saw_salmon": true}` with a valid key and returns 201 with the created report.
- [ ] A missing or wrong `X-Salmon-Key` returns 403; the required key is documented in `env.example`.
- [ ] The custom throttle is attached, its rate is a named constant tighter than DRF's default, and a test asserts 429 once exceeded.
- [ ] `reported_at` is server-derived: a client-supplied `reported_at`/`created_at` in the body is ignored, proven by a test.
- [ ] Invalid payloads return 400 with field errors — missing `saw_salmon`, non-boolean `saw_salmon`, out-of-vocabulary `species`, out-of-vocabulary `quantity`.
- [ ] The write endpoint works with no credentials and no CSRF token cross-origin, and is absent from any authenticated-only schema group.
- [ ] A historical data file is committed under `apps/salmon/fixtures/`; `docs/data-sources.md` records its provenance, extraction method, and any manual corrections with reasons.
- [ ] `load_historical_fish_counts` loads the file on a fresh database with row count and species/date coverage matching the file; re-running inserts zero rows and reports zero changes (idempotency proven by test); `--dry-run` writes nothing (row count asserted before/after) and reports its would-apply tally; every loaded row has non-null `source` and `retrieved_at`; a malformed input row fails loudly naming the offending row and leaves no partial load.
- [ ] All three read endpoints return 200 for valid requests; window/range params are bounded by named constants; an over-range request clamps or 400s deterministically (tested) and never 500s.
- [ ] `GET /salmon/reports/recent/` returns YES/NO totals plus latest report timestamp, exposes no individual rows, and returns zeroed totals with null timestamp on an empty database.
- [ ] `GET /salmon/counts/` returns latest stored count date and `retrieved_at` in meta, and an empty series with null meta on an empty database.
- [ ] `GET /salmon/counts/seasonality/` returns per-species per-bucket totals plus per-bucket year coverage, computed only from stored `fish_count` rows (no hardcoded seasonality table), degrading to empty on an empty database.
- [ ] A test asserts each read endpoint's query count does not grow with row count (no N+1 across species or buckets).
- [ ] All endpoints appear in the drf-spectacular schema with summary, description, and tag; `python manage.py spectacular --fail-on-warn` succeeds.
- [ ] `pytest apps/salmon` passes.

### P3 — Scheduled idempotent importer
**What:** `python manage.py import_fish_counts` — the recurring job, implementing VISION §6: fetch the source's currently available recent window (size set in P1 from observed backfill behavior), parse, validate, compare against stored rows, insert what's missing, record the outcome. It must **not** assume yesterday's count exists, and must tolerate the source being unavailable, slow, or shape-changed without breaking the public site — a failed import leaves the last good data in place and the reads keep serving with honest staleness meta.

Adds the `ImportRun` model (`started_at`, `finished_at`, `status`, `records_inserted`, `message`) and extends `GET /salmon/counts/` meta with the last successful import time. `ImportRun` is a deliberate third table: inferring freshness from `max(FishCount.retrieved_at)` cannot tell "the source published nothing new" from "the importer has been broken a week," and §17 needs that distinction. Human-confirmed.

*Buy vs. build:* a plain management command on Heroku Scheduler, not Celery/Airflow — matches the existing `send_homecare_weekly_digest` precedent and adds no infrastructure. Documented here, deployed in M5.

**Acceptance:**
- [ ] `import_fish_counts` fetches a recent window (not a single expected date), inserts only observations absent locally, and reports the tally.
- [ ] Idempotency: two runs against the same stubbed source payload insert zero rows the second time (tested).
- [ ] Backfill tolerance: a payload containing days older than the newest stored row still inserts those missing older days (tested).
- [ ] Manual-correction latch honored: a row with `manually_corrected=True` is not overwritten even when the source payload disagrees with it, and the run's `ImportRun` message reports the skipped-because-latched count (tested).
- [ ] Published totals are used as a checksum: a stubbed payload whose published total disagrees with the sum of its per-species rows fails the run loudly and writes no `FishCount` rows (tested). No aggregate row is ever stored.
- [ ] Source unavailable (network error, non-200, empty body) and source malformed (unexpected shape) both fail gracefully — no rows written, an `ImportRun` recorded as failed with the reason, no unhandled exception.
- [ ] All read endpoints still return 200 with correct staleness meta after a failed import (tested).
- [ ] `ImportRun` rows are written on both success and failure paths; `GET /salmon/counts/` meta exposes the last successful import time.
- [ ] `--dry-run` writes no `FishCount` rows and reports what it would insert.
- [ ] A deployment note documents the Heroku Scheduler command and cadence, following `docs/DEPLOYMENT_DIGEST.md`; the schedule itself is verified in M5.
- [ ] `pytest apps/salmon` passes, and the full `pytest` suite shows no regressions in `apps/analytics`, `apps/homecare`, or `apps/bible_guides`.

## Notes / Dependencies
- **Phase order is a dependency chain:** P1 settles the schema (inspection → constraint → models) → P2 exposes it and loads history → P3 keeps it current and consumes P2's freshness contract. The inspection cannot move later than P1: getting the constraint wrong after P2's bootstrap means migrating the whole history.
- **Scope-of-change routing:** every code artifact (app, models, endpoints, commands, tests, backend deployment note) is **shared scope** → `mjt-pub-api`, no `plans/` there. `docs/data-sources.md` and everything under `plans/` are **project scope** → this repo. Nothing is written to `mjt-pub-api/STANDARDS.md` or `mjt-pub-api/DECISIONS.md` without prior human approval via `PM.ThreadMaintenance`.
- **Concurrent branch `feat/bible-guides` — migrations are structurally safe; three config files will conflict.** Django numbers migrations per app, so `apps/salmon/migrations/0001+` cannot collide with `apps/bible_guides/migrations/0001-0009`; verified that branch touches no other app's migrations, and neither app has a cross-app migration dependency or shared ForeignKey, so merge order does not affect the migration graph. The genuine (minor) conflicts are three files both branches append to: `mjt_pub_api/settings.py` (`INSTALLED_APPS`), `mjt_pub_api/urls.py` (`urlpatterns`), and `env.example`. Resolution is "keep both lines." Whichever branch reaches `main` second rebases and resolves them.
- **M2 adds no new backend dependencies.** Django, DRF, drf-spectacular and `requests` are already present. `feat/bible-guides` rewrote all three of `requirements/base.txt` / `dev.txt` / `prod.txt`, so leaving them untouched avoids the only lockfile-scale conflict. If a phase turns out to genuinely need a new package, flag it rather than silently regenerating a requirements file.
- **Eventual prod release:** the chain is `feat/*` -> `main` -> `prod` -> Heroku with a **manual** `python manage.py migrate` step (`mjt-pub-api/README.md`). Once both apps are on `main`, one migrate run applies both apps' pending migrations together — independent and safe, but not separable.
- **CORS needs no M2 work.** `mjt-pub-api` already ships `corsheaders`, allows all origins in DEBUG, and reads `CORS_ALLOWED_ORIGINS` from env in production. The production static-site origin is added at deploy time (M4/M5). The `X-Salmon-Key` header must be added to `CORS_ALLOW_HEADERS` alongside the existing `x-analytics-key`.
- **M3 boundary held deliberately.** M2 ships raw and lightly aggregated reads only — no current-status score, no weighting rule, no forecast. Including `seasonality/`, which returns historical totals and year coverage, never a prediction.
- **Anti-abuse remains BACKLOG P1.** P2's write key and tight throttle are speed bumps by design, not a solution. Turnstile stays on the backlog and should be revisited before QR stickers ship.
- **Verification runs in the devcontainer** against `mjt-pub-api/requirements/dev.txt`. If a live container run genuinely cannot be completed for a phase, record the exact gap in that phase's verification notes rather than substituting a host-venv path.
- **Source inspection: proceed on partial reachability, block only if nothing verifies (Q-007 ruling).** Outbound HTTPS from the container was confirmed working on 2026-09-07 (`wdfw.wa.gov` → 200; `nwd.usace.army.mil` → 403, a WAF/user-agent rejection rather than a network block — try a browser user-agent first). If egress works but a candidate source is unreachable or shape-changed, that is an inspection *finding*: record the exact URL, status code, and observation date in `docs/data-sources.md` and proceed on the sources that did respond, since P1 needs only one authoritative series to settle the constraint. If **no** source can be verified live, stop and raise a blocker — do not write a constraint or species vocabulary from recollection. The `pytest` / `makemigrations --check` / `migrate` verification has no network dependency and runs regardless.
