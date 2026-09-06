# VISION.md

PROJECT SIZE: I'd like this to be as small as you possible think is reasonable. But I know it has multiple repos / directories, and several substantial components.

## Are Salmon at Ballard Locks?

A tiny, useful, local website that answers one simple question:

> **Are there salmon at Ballard Locks right now?**

The site combines lightweight public visitor reports with historical and recent official fish-count data to give a simple current-status answer and a coarse forecast for the **total salmon expected over the next 7 days**.

This is intentionally a small, bounded project. The goal is not to build a comprehensive fisheries platform, a scientific monitoring system, or a large community product. The goal is to make a clever, useful local utility that can be built quickly, run cheaply, and potentially pay for itself through a tiny local sponsorship and optional “Buy Me a Coffee” support.

---

# 0. First Step: Recreate the Existing Workspace / Devcontainer Pattern

Before implementing the product, first inspect and reproduce the development setup used by:

`C:/Users/Micha/DevSpace/workspaces/stencil-bible-guides/`

The new project should follow that workspace/devcontainer pattern.

The multi-root workspace should include:

1. **Frontend repo**
   - This repo.
   - Repo/project name is TBD.
   - This repo initially contains only `plans/` and the SAM planning files, plus this `VISION.md`.

2. **Backend repo**
   - `C:/Users/Micha/DevSpace/projects/mjt-pub-api`

3. **Workspace folder**
   - A new folder under:
     - `C:/Users/Micha/DevSpace/workspaces/`
   - It should play the same role as `stencil-bible-guides`.
   - Name is TBD.

The first implementation task is therefore:

> **Inspect `C:/Users/Micha/DevSpace/workspaces/stencil-bible-guides/`, understand its devcontainer and multi-root workspace structure, and reproduce that structure for this project before beginning product implementation.** Let me know if I should create a github repo for the `workspaces/AreSalmonAtBallardLocks` folder - it will need to be `workspace-AreSalmonAtBallardLocks`, since the unprefixed repo is already taken by the frontend.

Do not invent a new workspace architecture if the existing pattern can be reused.

---

# 1. Product Idea

The site should answer:

> **Are there salmon at Ballard Locks?**

Visitors at or near the Ballard Locks fish ladder can submit an extremely lightweight report:

- **Yes, there are salmon**
- **No salmon right now**

These reports are aggregated with recent official fish-count data and historical fish-count seasonality.

The site then displays a simple, human-readable current status such as:

- **YES — salmon are being seen today**
- **PROBABLY — salmon are likely, but recent visitor reports are limited**
- **MAYBE — mixed or stale reports**
- **PROBABLY NOT — few salmon are expected and visitors are not seeing them**
- **NOT ENOUGH RECENT DATA**

The site should also provide:

> **Salmon expected over the next 7 days**

This is a forecast of the **total number of salmon expected to pass through the Locks over the entire next seven-day period**.

It is explicitly **not** a day-by-day forecast.

That distinction is important. The available data does not justify pretending we know that Tuesday will have 417 fish and Wednesday will have 632. A rolling seven-day total is useful for planning while remaining appropriately coarse.

---

# 2. Core User Need

The official fish-count data answers:

> How many salmon have been counted passing through the Locks?

This site answers a more practical visitor question:

> If I go to the Ballard Locks, am I likely to see salmon?

That distinction is the entire product.

Someone planning a family outing, showing Seattle to a visitor, or deciding whether to walk over to the fish ladder should be able to open the page and get a useful answer in seconds.

No account should be required.

No app should be required.

No onboarding should be required.

---

# 3. Product Principles

## 3.1 The answer comes first

The first screen should immediately answer the question.

Do not make the user scroll through background information before seeing the current salmon status.

## 3.2 Reporting should be almost frictionless

The primary contribution flow is binary:

- **YES, I SAW SALMON**
- **NO SALMON RIGHT NOW**

Optional follow-up fields may exist, but they must not block the basic report.

Possible optional follow-ups:

- One / a few / lots
- Species, if known
- Short note, only if there is a clear reason to support it later

The binary observation is the important data.

## 3.3 Do not imply scientific precision that does not exist

The site should use broad language such as:

- High
- Moderate
- Low
- Peak season
- Mixed reports
- Recently seen
- Official count data is stale

Avoid fake precision.

For example, do not display:

> 87.3% chance of seeing salmon

unless a future model has enough validated data to justify such a number.

## 3.4 Graceful degradation is a core requirement

The system should remain useful if:

- no one has submitted a visitor report today,
- official fish counts have not updated for several days,
- the daily fish-count importer fails,
- historical data is missing for a species or period,
- a public source changes or temporarily disappears.

The site should never depend on live historical-data retrieval.

Historical observations belong in our database.

## 3.5 Keep infrastructure boring

This is a tiny local utility.

Prefer:

- existing `mjt-pub-api` infrastructure,
- simple database tables,
- deterministic aggregation,
- scheduled ingestion,
- browser- or API-side arithmetic,
- no LLM dependency,
- no unnecessary ML infrastructure.

---

# 4. Data Model

The product needs two primary conceptual tables.

## 4.1 Visitor Reports

Suggested model:

```text
sighting_report
---------------
id
reported_at
saw_salmon          boolean
quantity            nullable enum
species             nullable
created_at
```

Potential anti-abuse or diagnostic metadata can be added later if needed, but should not complicate the initial product.

Possible examples:

- anonymous session identifier
- coarse client fingerprint
- user agent
- source / QR campaign

Do not collect more identifying information than is needed.

The site does not need user accounts for reporting.

---

## 4.2 Official / Historical Fish Counts

Suggested model:

```text
fish_count
----------
id
date
species
count
source
source_url           nullable
source_metadata      nullable JSON
retrieved_at
created_at
updated_at
```

There should be a uniqueness constraint appropriate to the data source, likely based on:

```text
(date, species, source)
```

or, if only one authoritative series is maintained:

```text
(date, species)
```

The exact constraint should be chosen after inspecting the available source data.

The important principle is:

> **Fish-count history is durable local data, not a transient external lookup.**

---

# 5. Historical Data Strategy

Historical counts should be populated once into the local database from the best available public source or combination of public sources.

This may involve:

- downloading or extracting historical data,
- transforming a public table or chart,
- creating an import file,
- combining multiple authoritative/public sources,
- manually cleaning a small number of anomalies.

That is acceptable.

The initial historical bootstrap does **not** need to be a beautiful live integration.

Once the historical data exists locally, the frontend and forecast model should query our own backend.

Do not retrieve historical data live on normal page loads.

Do not make basic site behavior depend on a third-party historical API remaining available.

---

# 6. Ongoing Fish-Count Ingestion

After the initial historical bootstrap, run a scheduled job to retrieve newly published official counts.

The importer should be deliberately simple and idempotent:

```text
fetch public source
→ parse available observations
→ validate
→ identify records not yet stored
→ insert new observations
→ record success/failure
→ done
```

The job should not assume that “yesterday’s count” will always be available.

The public source may publish data late or backfill several days at once.

Therefore the importer should fetch a recent window and insert any missing observations rather than relying on one exact expected date.

For example:

> Fetch the latest N days or the currently available current-season table, compare to local rows, and insert anything missing.

The system should tolerate the source being unavailable.

A failed import should not break the public site.

---

# 7. Current Salmon Status

The current answer should combine the available signals without requiring every signal to exist.

Possible inputs:

1. Recent visitor reports
2. Recent official counts
3. Historical seasonal expectations

The aggregation does not need to begin as a sophisticated model.

A deterministic scoring rule is appropriate for V1.

Possible qualitative hierarchy:

## Strong current visitor data

Recent visitor reports should heavily influence the immediate answer.

Examples:

- multiple recent YES reports → strong evidence
- multiple recent NO reports → evidence against current visibility
- mixed reports → mixed status
- one isolated report → limited evidence

Recent observations should matter more than old observations.

## Recent official counts

Recent official passage counts provide useful context, especially when visitor reports are sparse.

The page should make clear when the latest official data is stale.

Example:

> Latest official count: September 3

rather than silently treating it as current on September 6.

## Historical seasonality

Historical counts provide the fallback prior.

Even when no recent data exists, the site should be able to say something useful such as:

> This is historically a strong period for coho.

Historical seasonality should be derived from the locally stored `fish_count` data rather than maintained as a separate manually authored dataset.

---

# 8. Seven-Day Salmon Forecast

The site should provide one coarse forecast:

> **Expected total salmon over the next 7 days**

This is a **single seven-day total**.

It is not seven separate daily forecasts.

The purpose is to answer:

> Is the coming week generally a good salmon week?

The forecast can begin with a very simple model using:

- historical counts for the same seasonal period,
- recent current-year counts,
- current-year run strength relative to historical years,
- species-level seasonality.

A simple statistical model is sufficient.

Possible approaches include:

- historical seasonal baseline with smoothing,
- regression using engineered seasonal features,
- recent-run scaling,
- a small pretrained/fitted model whose coefficients are shipped with the frontend,
- a model calculated in the backend and returned through the API.

There is no need to introduce a heavy ML framework.

The model should be explainable enough that we can describe the forecast in ordinary language.

For example:

> **Next 7 days: HIGH**
>
> Based on historical run timing and this season’s recent official counts, a strong number of salmon are expected to pass through the Locks over the coming week.

Or, if displaying a numeric range or point estimate later proves useful:

> **About 4,000 salmon expected over the next 7 days**

Any numeric forecast should be presented with appropriate humility.

The product should not imply that salmon passage guarantees visitor visibility.

---

# 9. Future Model Opportunity: Visibility vs. Passage

The public visitor reports create a potentially interesting dataset that does not currently appear to exist in a purpose-built form:

> Given official fish passage counts and seasonality, how likely is a normal visitor to actually see salmon at the fish ladder?

This does **not** need to exist in V1.

Initially:

- official counts estimate fish passage,
- visitor reports describe real-world visibility,
- the current-status algorithm combines them heuristically.

If enough public reports accumulate, a future model could estimate the relationship between:

- official count levels,
- species mix,
- recent counts,
- time of season,
- recent visitor reports,

and the probability that a visitor reports seeing salmon.

This would be a genuinely useful derived dataset, but it is a later possibility rather than an MVP requirement.

---

# 10. Page Structure

The initial page should be extremely simple.

## Hero / current answer

Example:

```text
ARE THERE SALMON AT BALLARD LOCKS?

YES — SALMON ARE BEING SEEN TODAY

12 YES · 2 NO reports today
Last reported sighting: 18 minutes ago
```

## Report buttons

Very prominent:

```text
YES, I SAW SALMON
NO SALMON RIGHT NOW
```

After submission, thank the visitor and immediately update or reflect the report if appropriate.

## Seven-day forecast

Example:

```text
NEXT 7 DAYS

HIGH

A strong number of salmon are expected to pass through
the Locks over the next seven days.
```

Optionally display:

- expected seven-day total,
- historical comparison,
- species composition,

but only if these are understandable and useful.

## Official-data context

Example:

```text
LATEST OFFICIAL COUNTS

Chinook     ...
Coho        ...
Sockeye     ...

Latest available official data: September 3
```

The site should clearly distinguish:

- visitor reports,
- official fish counts,
- forecast estimates.

## Informational content

Below the utility, include concise evergreen information:

- When are salmon usually at Ballard Locks?
- Which salmon species pass through?
- Where is the fish ladder?
- What are the Ballard Locks?
- Links to official Ballard Locks information
- Links to official fish-count sources
- Possibly links to relevant salmon / fisheries information

This content can also support search traffic for phrases such as:

- Ballard Locks salmon
- salmon at Ballard Locks
- Ballard Locks fish ladder
- when to see salmon at Ballard Locks
- Ballard Locks salmon season

---

# 11. QR-Code Participation Strategy

The site depends on making it absurdly easy for people who are physically at the fish ladder to submit a report.

Create QR codes pointing directly to the site.

Potential sticker language:

> **Did you see salmon?**
>
> Tell the next visitor.
>
> [QR CODE]

Or:

> **ARE THERE SALMON TODAY?**
>
> Report what you see.
>
> [QR CODE]

The QR code should lead directly to the main page, where the YES / NO buttons are immediately visible.

No separate reporting landing page is necessary unless testing later shows a benefit.

QR-code deployment is operationally separate from the one-day software build.

---

# 12. Monetization

This is not intended to become a large business.

The desired economic outcome can be extremely small.

The site should ideally:

1. pay its own carrying costs,
2. possibly earn a small amount of profit,
3. remain fun and useful.

## 12.1 Local sponsor

The most natural business model is one local sponsor.

For example, a nearby restaurant or other Locks-adjacent business could pay for a small sponsorship.

Example:

> **Today’s salmon report is supported by [Local Business]**
>
> Hungry after the fish ladder? They’re two minutes away.

This is ordinary advertising/sponsorship revenue paid to the site owner.

It is **not** a charitable contribution and should not be described as tax-deductible.

The sponsorship should remain visually subordinate to the utility.

Do not put an interstitial ad between the user and the salmon answer.

## 12.2 Buy Me a Coffee

The site may also include an unobtrusive:

> ☕ Buy me a coffee

This is optional support from people who enjoy or appreciate the site.

Again, do not frame this as a nonprofit donation.

---

# 13. Cost Philosophy

The site should be nearly free to operate.

Expected recurring costs should be limited primarily to:

- one domain,
- negligible incremental backend hosting,
- negligible frontend hosting,
- occasional sticker replacement.

Avoid adding recurring SaaS dependencies unless they solve a real problem.

This project's financial bar is intentionally low.

If a tiny sponsorship or a handful of coffee purchases cover the annual domain and sticker cost, the project is economically successful.

---

# 14. Domain / Brand

Working domain:

`AreSalmonAtBallardLocks.org`

The domain itself expresses the product question and is well suited to QR-code discovery.

Do not buy multiple domains merely for speculative SEO value.

The site can target conventional search terms through:

- page title,
- H1,
- headings,
- evergreen explanatory content,
- structured metadata.

Potential page title:

> **Are There Salmon at Ballard Locks Today? | Live Salmon Reports**

Potential H1:

> **Are there salmon at Ballard Locks?**

---

# 15. Backend Responsibilities

Use the existing backend:

`C:/Users/Micha/DevSpace/projects/mjt-pub-api`

Likely backend responsibilities:

- store visitor reports,
- expose report submission endpoint,
- expose aggregated recent-report data,
- store historical fish counts,
- ingest newly published official counts,
- expose historical/recent count data needed by the frontend,
- optionally calculate current-status aggregation,
- optionally calculate seven-day forecast.

The exact split between frontend calculation and backend calculation can remain simple.

Preference:

- durable data and shared logic belong in the backend,
- trivial presentation math can live in the frontend,
- avoid duplicating canonical business logic unnecessarily.

---

# 16. Frontend Responsibilities

The frontend should:

- load current status,
- load recent report counts,
- load official-count context,
- load or calculate the seven-day forecast,
- submit YES / NO reports,
- clearly communicate data freshness,
- provide evergreen salmon / Locks information,
- render well on phones,
- make the QR-code-to-report flow nearly instantaneous.

This is primarily a mobile web experience.

Someone may scan the QR code while standing at the fish ladder.

---

# 17. Failure Modes and Graceful Degradation

The UX should explicitly handle missing inputs.

## No recent visitor reports

Show the best estimate from official counts and seasonality.

Example:

> Salmon are likely this week, but nobody has reported from the Locks recently.

## Official count data is stale

Keep using reports and historical seasonality.

Show:

> Latest official count data: September 3

## Official importer is broken

The public site should continue functioning using:

- historical data already stored,
- visitor reports.

## No useful current data of any kind

Fall back to seasonal context.

Example:

> This is historically a strong period for coho, but we do not have recent visitor or official observations.

## Historical gaps

Use the data that exists.

Do not fail the forecast merely because one species or year is incomplete.

The model should be designed to tolerate partial coverage.

---

# 18. Anti-Scope

The following are explicitly **not** required for the first version:

- user accounts,
- profiles,
- social features,
- comments,
- gamification,
- badges,
- native mobile app,
- detailed species identification workflow,
- computer vision,
- image uploads,
- push notifications,
- daily seven-day forecast chart,
- hour-by-hour forecasts,
- exact probability-of-sighting claims,
- complicated machine-learning infrastructure,
- live retrieval of historical data,
- multiple sponsors,
- ad network integration,
- nonprofit structure,
- broad Puget Sound coverage,
- other fish ladders,
- fishing-condition forecasts.

If the site becomes useful enough to justify expansion, those decisions can be made later.

---

# 19. MVP Definition

A successful first version should allow a visitor to:

1. Open the site.
2. Immediately see whether salmon are likely being seen.
3. See how recent that information is.
4. Press **YES** or **NO** to report what they see.
5. See a coarse estimate of **total salmon expected over the next 7 days**.
6. See the latest official-count context.
7. Understand when salmon are normally present at Ballard Locks.
8. Follow links to authoritative external resources.

Operationally, the system should also:

9. Store visitor reports.
10. Store historical official counts locally.
11. Periodically ingest newly published official counts.
12. Continue working when external data is temporarily unavailable.

---

# 20. Build Philosophy

This should remain a small project.

The ideal implementation is:

- one frontend,
- a few API endpoints,
- two main database models,
- one scheduled importer,
- one simple aggregation rule,
- one simple seven-day forecasting function,
- one afternoon of historical-data bootstrap work,
- QR-code stickers later.

Do not turn the forecasting piece into a research project.

Do not turn the ingestion piece into a generalized data platform.

Do not turn the reporting piece into a social network.

The site succeeds if someone in Seattle wonders whether it is worth going to the Locks, checks the site, gets a useful answer, and perhaps contributes one tap of fresh information for the next person.

And if the fish-and-chips place next door eventually pays to sponsor it, even better.

---

# 21. Data Visualizations, Seasonality, and SEO Context

The site should not be only a current YES/NO indicator. The locally stored historical fish-count dataset creates an opportunity to provide useful, evergreen context through simple visualizations and explanatory content.

These features serve three purposes:

1. help visitors understand when salmon are normally present,
2. make the forecast and current status more interpretable,
3. create substantial indexable content around common Ballard Locks salmon searches.

The goal is not to build an analytics dashboard. Visualizations should be simple, legible on mobile, and answer obvious visitor questions.

## 21.1 Historical Seasonality Visualization

Provide a visualization showing the typical salmon season across the calendar year.

A preferred form is a line or area chart showing historical average passage by week or day-of-year, ideally separated by species:

* Chinook
* Coho
* Sockeye

This should make the seasonal pattern visually obvious:

> When during the year are each species usually passing through Ballard Locks?

The visualization should be calculated from locally stored historical `fish_count` data.

Consider smoothing historical observations so that ordinary year-to-year noise does not make the chart unnecessarily jagged.

Possible labels or annotations:

* Typical sockeye season
* Typical Chinook peak
* Typical coho peak
* You are here / current date

Do not hard-code seasonal descriptions if they can be derived from the historical dataset.

## 21.2 This Year vs. Typical Year

If the data supports it, show a simple comparison between:

* cumulative salmon counted so far this year, and
* the historical average cumulative count by the same date.

This can answer:

> Is this year a strong or weak salmon run so far?

This comparison can be shown for all salmon or individually by species.

Keep the interpretation qualitative when appropriate:

* Above average
* Near average
* Below average

This same comparison may be useful as an input into the seven-day forecast.

## 21.3 Recent Official Counts

Provide a compact visualization of recent official counts, such as the last 7–30 published days.

This should help visitors see whether passage has recently been:

* increasing,
* decreasing,
* consistently high,
* sporadic,
* effectively absent.

Clearly distinguish dates with no published data from dates with a reported count of zero.

Do not silently interpolate missing official observations.

## 21.4 Visitor-Report Visualization

Once there are enough reports to make it meaningful, provide a lightweight view of recent crowd observations.

Possible representations include:

* YES vs. NO reports over the past several days,
* percentage of recent reports that were YES,
* report volume by day,
* a simple recent-sightings timeline.

Do not over-interpret a tiny sample.

If there are only three reports, show three reports rather than pretending they constitute a statistically meaningful trend.

## 21.5 Historical “Best Time to See Salmon” Context

Use the historical data to generate clear evergreen answers to questions visitors commonly have, such as:

* What is the best month to see salmon at Ballard Locks?
* When do sockeye pass through Ballard Locks?
* When do Chinook pass through Ballard Locks?
* When do coho pass through Ballard Locks?
* Are there salmon at Ballard Locks in September?
* What time of year is the Ballard Locks fish ladder busiest?

These answers should be grounded in the actual historical dataset wherever possible rather than generic salmon-season prose.

For example, the site may eventually say:

> Historically, this part of September is one of the strongest periods of the year for coho passage through the Ballard Locks.

Exact wording and statistics should be derived from the stored data.

## 21.6 SEO-Friendly Evergreen Content

The utility itself should remain the primary experience, but the page should contain enough high-quality contextual information to answer related search queries.

Relevant search-oriented topics include:

* Are there salmon at Ballard Locks today?
* Ballard Locks salmon
* Ballard Locks salmon season
* Ballard Locks fish ladder
* When to see salmon at Ballard Locks
* Best time to see salmon at Ballard Locks
* Ballard Locks salmon counts
* Sockeye at Ballard Locks
* Chinook at Ballard Locks
* Coho at Ballard Locks
* Salmon run Seattle
* Where to see salmon in Seattle

Do not create thin keyword-stuffed pages simply to target each phrase.

Prefer a strong primary page with useful sections, data, charts, and clear headings. Separate species or historical-data pages may be added later if they provide genuinely useful standalone information.

## 21.7 Indexable Data Pages

If implementation remains simple, consider stable URLs for useful data views such as:

```text
/history/
/seasonality/
/counts/
/species/coho/
/species/chinook/
/species/sockeye/
```

These are optional.

Do not add them merely for SEO architecture. Add them when there is enough useful data or explanation to justify a standalone page.

If they exist, they should be server-rendered or otherwise readily indexable and should contain meaningful text context in addition to charts.

## 21.8 Explain the Data

Charts should not stand alone.

Each visualization should include a short plain-language interpretation.

For example:

> **When are salmon usually at the Locks?**
>
> Salmon passage varies substantially by species. This chart uses historical Ballard Locks fish counts to show when each species has typically passed through during prior years.

Where relevant, include:

* historical years included,
* source attribution,
* last data update,
* whether values are averages, medians, cumulative counts, or modeled estimates.

This should remain understandable to a normal visitor, not only a data analyst.

## 21.9 Structured Search Metadata

Implement ordinary technical SEO hygiene:

* descriptive `<title>`
* useful meta description
* canonical URL
* Open Graph metadata
* sitemap
* robots.txt
* semantic headings
* descriptive chart captions / accessible text
* structured data where genuinely appropriate

Do not add schema markup merely because a schema type exists.

The page content itself should carry the SEO value.

## 21.10 Visualizations Are Secondary to the Answer

Despite all of the above, the site must still open with:

> **Are there salmon at Ballard Locks?**

followed immediately by the best current answer and the reporting controls.

Historical charts, seasonality, species information, and search-oriented explanatory material belong below that primary utility.

The desired hierarchy is:

```text
CURRENT ANSWER
↓
REPORT WHAT YOU SEE
↓
NEXT 7 DAYS: TOTAL SALMON FORECAST
↓
RECENT / OFFICIAL DATA
↓
SEASONALITY & HISTORICAL VISUALIZATIONS
↓
EVERGREEN BALLARD LOCKS SALMON INFORMATION
↓
SOURCES / METHODOLOGY
```

The site should be surprisingly informative once someone explores it, while remaining absurdly simple for the person who only wants to know whether there are fish today.

---

# 22. Data Sources, Attribution, and Acknowledgments

The site should clearly acknowledge the external public data sources that make the project possible.

This includes:

* official fish-count data,
* historical fish-count datasets,
* fisheries agencies,
* tribal fisheries data providers,
* research organizations,
* public informational pages,
* any third-party source used to bootstrap or validate historical records.

Attribution should not be hidden only in code comments or internal documentation.

Provide a visible **Data Sources / Methodology / Acknowledgments** section on the site that explains:

* where the fish-count data comes from,
* which organization originally collected or published it,
* whether the site imported, transformed, aggregated, or modeled that data,
* when the data was last retrieved,
* links to the original public sources where appropriate,
* any important caveats about preliminary counts, incomplete dates, estimated passage, reporting methodology, or missing data.

## Data Validity Disclaimer

**We make no guarantees regarding the accuracy, completeness, timeliness, validity, or reliability of any data displayed on this site.**

This applies to:

* external public fish-count data,
* historical data imported from third-party sources,
* visitor-submitted sightings,
* derived statistics,
* seasonal summaries,
* visualizations,
* current-status assessments,
* forecasts.

External datasets may contain errors, revisions, delays, missing observations, preliminary estimates, or methodological limitations.

Visitor reports are crowdsourced and may be mistaken, incomplete, duplicated, stale, or intentionally false.

Forecasts and derived statistics are estimates based on available data and should not be treated as official fisheries information or guarantees that salmon will or will not be visible.

The site should communicate uncertainty plainly rather than implying more confidence than the underlying data supports.

Do not imply that AreSalmonAtBallardLocks.org is an official government, tribal, fisheries, or Ballard Locks service.

The site should make the distinction clear:

> AreSalmonAtBallardLocks.org is an independent project that combines public fish-count data with visitor reports. Data may be incomplete, delayed, inaccurate, or revised, and the site makes no guarantees regarding its validity.

Where historical data is assembled from multiple sources, document that provenance rather than presenting it as a single homogeneous official dataset.

For example, if one period comes from WDFW and another from a Muckleshoot Fisheries dataset or a research publication, preserve that source information at the record or import-batch level where practical.

If a third-party site helps locate or expose public data, distinguish between:

* the **original data producer**, and
* the **website or interface through which the data was accessed**.

Prefer crediting the original producer whenever that can be determined.

The site should also acknowledge that visitor reports are crowdsourced and are not official fish counts.

Examples of appropriate language:

> **Official fish-count data:** Publicly available data from credited fisheries data providers. Data may be preliminary, incomplete, delayed, or subsequently revised.

> **Visitor reports:** Anonymous public observations submitted through this site. Reports are not independently verified.

> **Forecasts:** Independent estimates calculated by AreSalmonAtBallardLocks.org from historical and recent count data. They are not official fisheries forecasts and are not guarantees of future salmon passage or visibility.

Attribution and data-validity disclaimers should be treated as part of the product, not as an afterthought.
