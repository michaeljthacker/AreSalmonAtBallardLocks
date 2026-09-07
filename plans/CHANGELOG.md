# CHANGELOG
<!-- See plans/FORMATS.md for expected structure. -->

## Unreleased

### Milestone B1-M1 complete — Workspace/devcontainer scaffolding
Stood up the multi-root workspace and devcontainer so this frontend repo and the shared `mjt-pub-api` backend can be developed together from one reproducible, container-based environment. Live devcontainer rebuild confirmed by the human (2026-09-07): `python manage.py check` passed, `dev.sh` served both :8000/:8080, Ctrl+C shutdown clean.

### B1-M1-P1 — Multi-root workspace + devcontainer scaffolding
- Stood up the multi-root workspace (`workspaces/AreSalmonAtBallardLocks`): `.code-workspace` (three roots: frontend, api, workspace), devcontainer (Py3.12 + Node LTS, binds all three roots, owns backend venv/deps from `mjt-pub-api/requirements/dev.txt`), `dev.sh` (Django API :8000 + static frontend :8080, clean Ctrl+C shutdown), README, VERIFY.md.
- Added temporary placeholder `index.html` to the frontend repo (replaced in M4).
- Adapted from `stencil-bible-guides` pattern — Stripe CLI, webhook forwarder, and LLM worker stripped; devcontainer-first model with no host-venv fallback.

## Released
