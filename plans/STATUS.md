# STATUS

**Update configuration:** `status_updates=pm_only`

## Now
- Build: B1 — Are Salmon at Ballard Locks?
- Milestone: M2 — Backend data layer (`mjt-pub-api`)
- Phase: P1 (not yet started) — Source inspection, models, migrations, admin

## Blockers
- None

## Recent
- B1-M2 milestone approved. Plan was cut from 6 phases to 3 (P1 source inspection+models, P2 endpoints+bootstrap, P3 scheduled importer) after human pushback on administrative overhead of a code-free phase. Human confirmed: write key on the report endpoint (casual-posting speed bump, not spam defense), throttle tighter than DRF default, `ImportRun` table, and Turnstile deferred to BACKLOG. Investigated concurrent `feat/bible-guides` branch: migrations are per-app and cannot collide; only three append-only config files (`settings.py`, `urls.py`, `env.example`) will need trivial conflict resolution at merge time; M2 must add no new backend dependencies to avoid the one real conflict risk (`requirements/*.txt`).

## Next
- Staff.DraftQuestions — open questions for B1-M2-P1 before implementation starts.
