# Are Salmon at Ballard Locks?

A tiny, mobile-first local website that answers one question: **are there salmon at Ballard Locks right now?**

## What it does

The site combines lightweight crowd reports (a single YES / NO tap) with recent and historical official fish-count data to show a plain-language current status and a coarse forecast of the **total salmon expected over the next 7 days**. It is intentionally small — a useful local utility, not a fisheries platform — designed to run cheaply and ideally cover its own costs through one local sponsor and optional "Buy Me a Coffee" support.

The answer comes first: open the page, see the status, tap YES or NO. Everything else (forecast, official counts, seasonality charts, evergreen Ballard Locks info) lives below the primary utility.

## Key features

- **Instant current answer** — YES / PROBABLY / MAYBE / PROBABLY NOT / NOT ENOUGH DATA, from a deterministic aggregation of recent reports, recent counts, and seasonality.
- **Frictionless reporting** — no account, no app; a binary YES / NO tap with optional follow-ups.
- **Seven-day forecast** — one coarse total-salmon estimate for the coming week (not a day-by-day chart).
- **Durable local data** — visitor reports and official fish counts stored locally; a scheduled, idempotent importer keeps counts fresh.
- **Graceful degradation** — stays useful when reports are absent, counts are stale, or the importer fails.
- **Seasonality & evergreen content** — simple charts and grounded explanatory text for SEO and visitor context, plus a visible Data Sources / Methodology / Acknowledgments section.

## Tech stack

Multi-root workspace modeled on the existing `stencil-bible-guides` devcontainer pattern:

- **Frontend** — this repo, a plain static site (HTML/CSS/vanilla JS; no framework, no build step).
- **Backend** — the existing [`mjt-pub-api`](https://github.com/) service (report + fish-count storage, ingestion, aggregation endpoints).
- **Workspace** — a `workspace-AreSalmonAtBallardLocks` multi-root workspace folder.

## Getting started

_To be filled in once the workspace/devcontainer scaffolding (M1) is reproduced._

## Status

Early planning. See `plans/` for the SAM build plan and current status.
