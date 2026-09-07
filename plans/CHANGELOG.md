# CHANGELOG
<!-- See plans/FORMATS.md for expected structure. -->

## Unreleased

### B1-M1-P1 — Multi-root workspace + devcontainer scaffolding
- Stood up the multi-root workspace (`workspaces/AreSalmonAtBallardLocks`): `.code-workspace` (three roots: frontend, api, workspace), devcontainer (Py3.12 + Node LTS, binds all three roots, owns backend venv/deps from `mjt-pub-api/requirements/dev.txt`), `dev.sh` (Django API :8000 + static frontend :8080, clean Ctrl+C shutdown), README, VERIFY.md.
- Added temporary placeholder `index.html` to the frontend repo (replaced in M4).
- Adapted from `stencil-bible-guides` pattern — Stripe CLI, webhook forwarder, and LLM worker stripped; devcontainer-first model with no host-venv fallback.

## Released
