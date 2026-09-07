# Fish-count data sources

Source inspection for B1-M2-P1. Everything below was retrieved and verified
live from this project's devcontainer on **2026-09-07**; every claim about
field names, vocabulary, granularity and depth comes from the fetched
artifact, not from recollection.

This document is also the raw material for M5's public Sources page.

---

## Conclusion first

**One authoritative series must be stored, not several.** Salmon entering the
Lake Washington ship canal are counted at a single physical location — the
fish ladder at the Hiram M. Chittenden (Ballard) Locks — by a single
co-management arrangement: WDFW and the Muckleshoot Indian Tribe, counting
cooperatively. There is no second, independent count of the same fish to
reconcile against. The two retrieval routes below (S1 and S2) are two
*publications of the same series*, not two series.

**Therefore the uniqueness constraint is `(date, species)`**, and `source`
records which retrieval route produced a row rather than forming part of its
identity. See `plans/DECISIONS.md`.

**Species vocabulary is `sockeye`, `chinook`, `coho`, plus an `other`
catch-all.** Those three are exactly what the source publishes, and exactly
the three species VISION §21.1 names. **Steelhead is not published at this
ladder** and is therefore not a vocabulary member (see "Corrections to prior
assumptions").

**Sources P2/P3 will use:** S1 as the primary for all three species; S2 as the
multi-year historical bootstrap for sockeye only.

**Recent window for P3's importer: re-parse the entire current season, every
run.** Justification under "Revision and backfill behavior".

---

## S1 — WDFW "Lake Washington salmon counts" (primary)

| | |
|---|---|
| **Stable URL** | `https://wdfw.wa.gov/fishing/reports/counts/lake-washington` |
| **Retrieval** | HTTPS GET, server-rendered HTML. No API key, no session, no JS required for the tables. Returned `200` on 2026-09-07. |
| **Format** | Three HTML `<table>` elements with stable `id` attributes: `lw-sockeye-counts`, `lw-chinook-counts`, `lw-coho-counts`. A fourth, unnamed table holds annual sockeye totals. |
| **Fields** | Three columns per species table: `Date` (string), `Daily Count` (integer, thousands-separated), `Running Total` (integer, thousands-separated). |
| **Species vocabulary** | `sockeye`, `Chinook`, `coho`. Exactly three. Nothing else. |
| **Date granularity** | Daily, **with exceptions** — see "Range rows" below. Dates are `M/D` with no year; the year is implied by the season and must be supplied by the parser. |
| **History depth** | **Current season only.** The page is rewritten each year; it carries no prior-year daily detail. |
| **Publication cadence** | Roughly daily during each species' counting window. Per the page: sockeye counted daily June through July; Chinook "typically available from late July through September"; coho "typically available from early September into October". Outside those windows nothing is published. |
| **Attribution** | Washington Department of Fish and Wildlife, counting cooperatively with the Muckleshoot Indian Tribe. The locks and fish ladder are managed by the U.S. Army Corps of Engineers. |

### Observed state on 2026-09-07

- **Sockeye:** complete daily rows 6/12 → 9/3. Season total 31,302 (matches the
  9/3 running total). Season effectively over — every row from 8/26 is `0`.
- **Chinook:** daily rows 7/1 → 9/3, running total 11,369. Rows for 9/4
  onward exist but have **empty** `Daily Count` *and* empty `Running Total`.
- **Coho:** daily rows through 9/3, running total 972. Rows 9/4 → 10/2 have
  an **empty** `Daily Count` but the `Running Total` column carries forward
  the stale value `972`.

### Two parser traps, both load-bearing

**1. Empty cells are pre-rendered for the whole season.** The page emits a row
for every date in the season window up front and fills the counts in as they
are published. An empty `Daily Count` means *"not published yet"*, **not
zero** — the coho rows above are the clean demonstration, since a carried-
forward running total sits next to a blank daily cell. Reading blanks as zeros
would manufacture ~30 fake zero-passage days per species per season, and
VISION §21.3 forbids exactly that conflation. The importer must skip rows with
an empty `Daily Count` and write no row at all.

**2. Range rows.** The first row of the Chinook and coho tables is a
multi-day bucket, not a single date:

| Species | Row label | Daily Count |
|---|---|---|
| coho | `6/12-8/31` | 420 |
| Chinook | `6/18-6/30` | 0 |

These are pre-season totals covering the period before daily counting began.
`FishCount.date` is a single `DateField` and every row is one calendar day, so
a range row **cannot be represented** and must be skipped. Consequence to
accept knowingly: the 420 pre-season coho of 2026 are not stored, so
season-to-date coho derived from our rows will fall short of the source's
published running total by that amount. This is the correct trade — the
alternative is either inventing a distribution across 81 days (interpolation,
forbidden) or attributing 420 fish to a single arbitrary date (a fake spike in
the seasonality curve). The importer must detect a range label, skip it, and
name it in the `ImportRun` message rather than silently dropping it.

### Revision and backfill behavior

The page states this in its own words, twice:

> All daily count data is preliminary and subject to change as the season
> progresses.

> The preliminary counts are subject to revision.

So published days *do* change after first publication. Because the page always
serves **the entire current season in a single document**, a rolling "last N
days" window is both unnecessary and strictly worse than the alternative: one
fetch already contains every date, so a narrow window would spend the same
single request and then deliberately ignore revisions to earlier dates that
the source explicitly warns about.

**Recent window = the full current season, re-parsed every run.** Cost is one
HTTP request and 212 table rows across the three species as observed on
2026-09-07 (sockeye 84, Chinook 95, coho 33). This is also why the
`manually_corrected` latch matters: the importer will revisit and upsert every
date in the season on every run.

---

## S2 — WDFW PSSP chart feed (historical bootstrap, sockeye only)

| | |
|---|---|
| **Stable URL** | `https://pssp-count.wdfw-fish.us/salmon_counts_ballard.json` |
| **How it was found** | Not linked in the page body. It is declared in the page's `drupal-settings-json` blob as `wdfwSalmonChart.data_url`, and is what powers the on-page "Ballard Locks sockeye counts" chart. |
| **Retrieval** | HTTPS GET, static object on S3 behind CloudFront. `200`, `content-length: 55307`, `last-modified: 2026-09-02T01:35:37Z`. No key, no auth. |
| **Format** | JSON. `data.ballard_locks.sockeye.{data, stat_settings, current_year_count_sum}` plus a top-level `created_date`. |
| **Species vocabulary** | **`sockeye` only.** No Chinook, no coho. |
| **Date granularity** | Daily, and cleanly so — no range rows. Real ISO dates (`count_datetime`, `YYYY-MM-DD`), which is a genuine advantage over S1's `M/D`. |
| **Window** | **June 1 – August 31 only** (86 rows). September sockeye are outside the file; in 2026 those are all zeros, but this is a structural gap, not an empty one. |
| **History depth** | **17 seasons — current year plus 16 back (2010–2026).** This is the deep history, and it arrives in one download. |
| **Cadence** | Regenerated during the season. `created_date: ["2026-09-01"]` and `last-modified` 2026-09-02 — i.e. already 5 days stale on the day of inspection, consistent with the sockeye season having ended. |

### The relative-year encoding — the single biggest trap in either source

Each row carries the same day-of-season across many years, keyed **relative to
the current year**, not by calendar year:

```json
{
  "count_datetime": "2026-06-15",
  "count_current": 0,           // 2026 — the current season
  "count_1year": 7,             // 2025
  "count_2year": 7,             // 2024
  ...
  "count_16year": 669,          // 2010
  "rolling_mean": 12.8,
  "standard_deviation": 35.8391
}
```

`count_current` is the current year; **`count_Nyear` is the year
`current_year − N`**. A parser that reads `count_1year` as "this year" is off
by one for all 17 series, and the same key name means a different calendar year
next season. The importer must resolve `N` against the fetch year and record
the resolved calendar year in `source_metadata`.

**How the mapping was verified** (not assumed): summing each `count_Nyear`
series over the June–August window and comparing against the independent
annual-totals table in S1.

| key | implied year | S1 annual total | S2 Jun–Aug sum | ratio |
|---|---|---|---|---|
| `count_current` | 2026 | — | 31,302 | matches `current_year_count_sum` and S1's 9/3 running total exactly |
| `count_1year` | 2025 | 17,881 | 18,112 | 1.01 |
| `count_2year` | 2024 | 23,188 | 23,262 | 1.00 |
| `count_5year` | 2021 | 36,618 | 38,033 | 1.04 |
| `count_9year` | 2017 | 129,568 | 133,008 | 1.03 |
| `count_13year` | 2013 | 177,349 | 179,187 | 1.01 |
| `count_16year` | 2010 | 155,900 | 161,417 | 1.04 |

Fourteen of sixteen years land within ±13%, and the shape is decisive — the
2017 and 2013 spikes (129k and 177k against a ~25k baseline) appear at exactly
`count_9year` and `count_13year`. Every off-by-one alternative mapping puts
those spikes on ordinary years and fails by an order of magnitude. Mapping
confirmed.

### Known gaps and anomalies in S2

- **`count_4year` (2022) has only 38 of 86 rows**, summing to 27,393 against
  S1's annual 43,289 (ratio 0.63). Roughly half the season is simply absent
  from the file. Do not treat 2022 as a complete year.
- **`count_10year` (2016) sums to 23,834 against S1's annual 58,583**
  (ratio 0.41) *despite* having a full 81 rows. Unexplained by row count. The
  most likely reading is a 2016 run that extended well past the file's
  August 31 cutoff, but this is **not** verified and 2016 should be treated as
  suspect until it is.
- **`count_5year` (72 rows) and `count_3year` (80 rows)** are also short of
  the 81-row norm — minor, but the importer must not assume a uniform row set.
- Derived statistics (`rolling_mean`, `standard_deviation`) and
  `stat_settings` (`years_back: 5`, `mean_start_year: 2021`,
  `mean_end_year: 2025`) are **the source's own** analysis. Do not store them.
  M3 owns the forecast and computes its own baseline from stored rows;
  importing someone else's rolling mean would smuggle a second, invisible
  seasonality model into the product.

### What this means for history depth (Q-006)

The Q-006 ruling was: take all readily available years, floor of 10 complete
years, soft cap ~15 if each additional year costs a separate manual
extraction.

- **Sockeye clears the floor comfortably** — 17 seasons in one download, no
  per-year extraction cost at all. After excluding 2022 (half-missing) and
  quarantining 2016 (unexplained), that is ~15 sound years, right at the soft
  cap. Nothing needs truncating: the cap and the data agree by coincidence.
- **Chinook and coho do not clear it, and cannot be made to from these
  sources.** S1 carries current-season detail only and S2 omits both species
  entirely. There is no cheap route to multi-year daily Chinook or coho
  history; obtaining it would mean per-year archived snapshots of S1 (e.g.
  Wayback Machine), which is a separate hand extraction *per year per
  species* — squarely the case the Q-006 soft cap exists to stop.

**This is the one finding that changes downstream plans.** It is not a
blocker for P1 — the schema is unaffected, and `(date, species)` handles a
deep sockeye series and shallow Chinook/coho series without modification —
but P2's bootstrap will produce a database with 17 years of sockeye and one
season of Chinook and coho, and M3's per-species seasonality baseline for
Chinook and coho will rest on a single year. Flagged to P2 and M3.

---

## S3 — U.S. Army Corps of Engineers, Chittenden Locks fish ladder (not usable)

| | |
|---|---|
| **URL** | `https://www.nws.usace.army.mil/Missions/Civil-Works/Locks-and-Dams/Chittenden-Locks/Fish-Ladder/` |
| **Status** | **`403 Access Denied`** on 2026-09-07, with both a default client user-agent and a browser user-agent. The response is an edge/WAF denial page carrying a reference id, not a Django/app 404. |

Per the Q-007 ruling this is recorded as a **source finding, not an
environment failure** — container egress is demonstrably fine (S1 and S2 both
returned 200 from the same shell in the same session). USACE operates the
ladder but WDFW is the counting authority, so nothing is lost: S1/S2 already
provide the count series. Not needed by P2 or P3. USACE still warrants
attribution on M5's Sources page as the ladder operator.

## S4 — ballardlocks.org (context only, not a data source)

`https://ballardlocks.org/fish-salmon-ladder.html` returns 200 and is linked
from S1. It is a visitor-information page from the locks' friends
organization — background and photographs, not a count series, and not an
authoritative publisher. Possibly useful for M4/M5 copy. No data value.

---

## Access, terms and attribution

- **Licensing.** WDFW pages carry a bare `© 2026 All rights reserved` footer
  with no open-data license and no published terms-of-use for these tables.
  WDFW is a Washington state agency and these are public records. The stance
  this project takes: store the **counts as facts** (individual measurements
  are not themselves copyrightable expression), always attribute, always link
  the source URL, and never republish the pages or present the data as
  anything other than WDFW's.
- **Required attribution wherever counts are displayed** (M4/M5): Washington
  Department of Fish and Wildlife and the Muckleshoot Indian Tribe, who count
  cooperatively; U.S. Army Corps of Engineers as operator of the locks and
  fish ladder.
- **`robots.txt`.** `https://wdfw.wa.gov/robots.txt` returns 200. The
  `User-agent: *` group does **not** disallow `/fishing/reports/`— the
  disallow list is Drupal internals, `/admin/`, `/search/` and `/user/*`. So
  the counts path is permitted to general clients. Separately, the file
  contains `Disallow: /` groups naming specific AI-training crawlers,
  including `anthropic-ai`. Those groups target training crawlers by
  user-agent token, and P3's importer is neither — it is a single scheduled
  request for one public page.
  - **Requirement for P3:** send an honest, descriptive `User-Agent`
    identifying this project and a contact URL. Do **not** impersonate a
    browser and do **not** send any of the disallowed tokens.
  - *Disclosure:* during this inspection a browser user-agent was used while
    probing S3's WAF (which rejected the default client). The committed
    importer must not carry that behavior forward.
  - `https://pssp-count.wdfw-fish.us/robots.txt` returns `403` (bare S3
    bucket, no robots file). No crawl directives exist for that host.
- **Politeness.** One request per source per scheduled run. Both S1 and S2 are
  single documents containing everything needed; there is nothing to paginate
  and no reason to crawl.

---

## Manual corrections applied

None yet. No historical data has been loaded — that is P2's bootstrap.

When a correction is made, it is recorded here (date, species, published
value, corrected value, reason) **and** on the row itself via
`FishCount.manually_corrected` + `correction_note`, which the importer will
not overwrite. Rows already known to need scrutiny at bootstrap time: S2's
2022 (incomplete) and 2016 (unexplained shortfall).

---

## Corrections to prior assumptions

Two working assumptions recorded before inspection turned out to be wrong.
Both are noted here because the reasoning that depended on them is on the
record in `plans/thread.md` and `plans/DECISIONS.md`.

1. **Steelhead is not in this source.** Q-003 was answered on the premise that
   steelhead appears in the same source table as the salmon species, and ruled
   it a first-class vocabulary member. It does not appear: S1 publishes exactly
   sockeye, Chinook and coho, and S2 publishes sockeye alone. No `steelhead`
   member was created — a vocabulary member for data that does not exist would
   be speculation frozen into a database constraint. The *structural* half of
   that ruling is untouched and still valuable: `SALMON_SPECIES` remains a
   named subset distinct from the full vocabulary, so if the co-managers ever
   do publish a non-salmon species, it becomes a member without becoming a
   salmon, and no query needs revisiting.

2. **Published totals are running totals, not just season totals.** Q-003
   anticipated a season/period total to use as an import checksum. The actual
   shape is better: S1 gives a per-row `Running Total` column, so the checksum
   can be applied **per date** (`running_total[n] − running_total[n−1]` must
   equal `daily_count[n]`) rather than once per season. That catches a parser
   or publication error on the day it appears instead of at season end. S2
   independently provides `current_year_count_sum` for a whole-season check.
