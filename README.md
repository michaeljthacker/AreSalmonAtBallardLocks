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

Development happens in a multi-root VS Code workspace backed by a devcontainer (adapted from the `stencil-bible-guides` workspace pattern — the pattern only, not its Stripe/LLM concerns). The devcontainer is the standard environment: it owns the backend Python virtualenv and dependency install, so there is no separate host-venv workflow.

- **Frontend** — this repo, a plain static site (HTML/CSS/vanilla JS; no framework, no build step).
- **Backend** — the existing `mjt-pub-api` service, a shared Django 5.2 + DRF app on Python 3.12 (report + fish-count storage, ingestion, aggregation endpoints). Bind-mounted into the workspace; feature work branches off `main`.
- **Workspace** — the [`workspace-AreSalmonAtBallardLocks`](https://github.com/michaeljthacker/workspace-AreSalmonAtBallardLocks) repo, which holds the `.code-workspace` file, the `.devcontainer/`, and a `dev.sh` runner.

## Getting started

Development runs inside the devcontainer defined in the workspace repo (`workspace-AreSalmonAtBallardLocks`), which bind-mounts this frontend repo, the `mjt-pub-api` backend, and the workspace folder as three roots.

1. Clone the workspace repo, this repo, and `mjt-pub-api` as sibling checkouts under your `DevSpace` tree.
2. Open `AreSalmonAtBallardLocks.code-workspace` in VS Code and **Reopen in Container**. The devcontainer creates the backend virtualenv and installs dependencies from `mjt-pub-api/requirements/dev.txt` on first build.
3. Run `dev.sh` to start both services: the Django API on `:8000` and a static server for this frontend on `:8080` (both published to the LAN for on-phone testing). Ctrl+C stops both cleanly.

See the workspace repo's `README.md` and `VERIFY.md` for the full open-and-run guide and the environment verification log.

## Status

Workspace and devcontainer scaffolding (M1) is in place. Product features — data models, endpoints, the fish-count importer, aggregation, forecast, and the real frontend — are M2–M5. See `plans/` for the SAM build plan and current status.
