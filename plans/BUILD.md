---
size: full
---
# BUILD — B1

## Purpose
Build "Are Salmon at Ballard Locks?" — a small, mobile-first local website that answers whether salmon are currently visible at the Ballard Locks fish ladder and gives a coarse total-salmon forecast for the next 7 days. It combines lightweight crowd YES/NO reports with locally stored official and historical fish-count data, aiming to run cheaply and cover its own costs via one local sponsor and optional tips.

## Scope

### In scope
- Use `stencil-bible-guides` as a **reference model** for the multi-root workspace / devcontainer setup and **adapt it as needed** (not a verbatim clone) across this frontend repo, the `mjt-pub-api` backend, and a new workspace folder.
- Frontend stack: a plain **static site — HTML/CSS/vanilla JS, no framework and no build step** — consistent with the "tiny, boring, one-frontend" philosophy (VISION §3.5, §20). The `stencil-bible-guides` name refers to the *workspace/devcontainer pattern*, not a mandated frontend framework.
- Two backend data models (`sighting_report`, `fish_count`), a report-submission endpoint, aggregated-report and count endpoints.
- One-time historical fish-count bootstrap into the local database from public sources.
- Choose the `fish_count` uniqueness constraint — `(date, species, source)` vs `(date, species)` — only *after* inspecting the actual source data, as an early M2 step (the importer's idempotency contract depends on it).
- A scheduled, idempotent importer for newly published official counts.
- Cheap hosting/deployment for both the static frontend and the scheduled importer, consistent with the "runs cheaply, covers its own costs" philosophy.
- Deterministic current-status aggregation and a simple, explainable 7-day total-salmon forecast.
- Mobile-first frontend: answer-first hero, YES/NO reporting, forecast, official-count context, data-freshness cues.
- Seasonality/historical visualizations, grounded evergreen content, SEO hygiene, and a Data Sources / Methodology / Acknowledgments section with a data-validity disclaimer.

### Out of scope
- User accounts, profiles, social features, comments, gamification, native apps.
- Computer vision, image uploads, push notifications.
- Day-by-day or hourly forecasts; exact probability-of-sighting claims.
- Heavy ML infrastructure; live retrieval of historical data on page load.
- Multiple sponsors, ad networks, nonprofit structure, coverage beyond Ballard Locks.

## Success criteria
- A visitor can open the site on a phone and get a useful current answer in seconds, see how recent it is, and tap YES/NO to report.
- The site shows a coarse 7-day total-salmon forecast and latest official-count context with clear freshness labeling.
- Visitor reports and historical/official counts are stored locally; the importer runs on a schedule and is idempotent.
- The public site keeps working when visitor reports are absent, official counts are stale, or the importer fails.
- Data sources are visibly attributed and a data-validity disclaimer is present.

## Milestones
- M1 — Stand up the multi-root workspace/devcontainer structure (frontend repo, `mjt-pub-api`, new workspace folder), using `stencil-bible-guides` as a reference model to adapt (not clone verbatim), so development can begin.
- M2 — Backend data layer: `sighting_report` + `fish_count` models (inspect source data first, then choose the `fish_count` uniqueness constraint), report-submission and read endpoints, one-time historical bootstrap, and the scheduled idempotent importer.
- M3 — Aggregation & forecast: deterministic current-status rule and the coarse 7-day total-salmon forecast, tolerant of partial/missing data.
- M4 — Frontend MVP: answer-first mobile utility (hero status, YES/NO reporting, forecast, official-count context, freshness cues), deployed to cheap static hosting.
- M5 — Seasonality visualizations, grounded evergreen content, SEO hygiene, Sources/Methodology/Acknowledgments with data-validity disclaimer, and confirming cheap deployment of both the static frontend and the scheduled importer.

## Risks / assumptions
- Uses the `stencil-bible-guides` devcontainer pattern as a reference to adapt (not a verbatim clone) and assumes `mjt-pub-api` is reusable; a new `workspace-AreSalmonAtBallardLocks` repo may be needed (human confirmation pending — see VISION §0).
- Public historical/official fish-count sources may be messy, incomplete, or change; bootstrap and importer must tolerate gaps and source unavailability.
- Forecast must stay simple and explainable — risk of over-engineering the model.
- Crowd reports may be sparse, stale, or abusive; aggregation must degrade gracefully without fake precision.
