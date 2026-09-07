# MILESTONE — B1-M1

## Goal
Stand up the multi-root workspace and devcontainer so this frontend repo and the shared `mjt-pub-api` backend can be developed together from one reproducible, container-based environment — adapting (not cloning) the `stencil-bible-guides` pattern.

## Scope note
Environment scaffolding **only** — no product code, backend apps, data models, or real frontend (those are M2–M5). The single deliverable is a working, documented dev environment. The one frontend artifact created is a throwaway placeholder page so the static-preview task has something to serve; it is replaced wholesale in M4.

## Known facts (decided, do not re-litigate)
- **Workspace folder:** `C:/Users/Micha/DevSpace/workspaces/AreSalmonAtBallardLocks` (human-confirmed).
- **Workspace git remote:** `https://github.com/michaeljthacker/workspace-AreSalmonAtBallardLocks.git` (human-confirmed).
- **Frontend repo (this repo, primary / owns `plans/`):** `C:/Users/Micha/DevSpace/Projects/AreSalmonAtBallardLocks`.
- **Backend repo (shared, reused):** `C:/Users/Micha/DevSpace/projects/mjt-pub-api` (Django 5.2 + DRF, Python 3.12, pip-tools). Now registered in `config.json` `shared_repos`.
- **Frontend stack:** plain static site — HTML/CSS/vanilla JS, no framework, no build step (BUILD.md; VISION §3.5, §20).
- **Environment model:** the **devcontainer is the standard dev environment** — it owns the backend venv and dependency install, matching how `mjt-pub-api` is already developed in other projects. There is no co-equal host-venv workflow.
- **Shared-repo branching discipline:** backend work branches off `main`; `mjt-pub-api` is shared with other in-flight branches across projects, so this project does not assume ownership of its working state. (M1 does not modify backend code, but the discipline is recorded now — see Notes.)

## Phases

### P1 — Multi-root workspace + devcontainer scaffolding
**What:** Adapt the `stencil-bible-guides` workspace/devcontainer pattern into a working environment for this project. Create the workspace folder/repo, the `.code-workspace`, the devcontainer (which owns venv/dependency setup), and a `dev.sh` that runs the two services this project needs; add a placeholder frontend page; then verify the whole thing end-to-end and document how to run it. Every artifact is derived from the reference but stripped of bible-guides-specific concerns (Stripe CLI, Stripe webhook task, LLM generation worker). Executed as ordered steps below.

**Steps:**
- **S1 — Workspace folder & repo.** Create `C:/Users/Micha/DevSpace/workspaces/AreSalmonAtBallardLocks`, `git init`, set `origin` to the confirmed remote, add `.gitignore` / `.gitattributes` / `README.md` stub naming the three roots and their host paths. (Container for workspace config only — not product code.)
- **S2 — `.code-workspace`.** Author `AreSalmonAtBallardLocks.code-workspace` defining exactly three folders — `frontend` → this repo, `api` → `mjt-pub-api`, `workspace` → `.` — plus editor settings (interpreter, format-on-save: Black for Python, Prettier for HTML/CSS/JS/JSON), recommended extensions, forwarded ports (8000 API, 8080 frontend, published to LAN for on-phone testing), and generic tasks (Django runserver, shell, pytest, deps refresh, static frontend preview). Drop bible-guides-specific tasks.
- **S3 — Devcontainer (the venv/dependency owner).** Create `.devcontainer/devcontainer.json` + `postCreate.sh` + `postStart.sh`. Python 3.12 base image, GitHub CLI + Node LTS features, bind mounts for the workspace folder + this frontend repo + `mjt-pub-api` at stable paths. `postCreate.sh` (one-time): git identity + `safe.directory` for mounted repos, create/repair the backend venv, install backend deps from `mjt-pub-api/requirements/dev.txt`, install pre-commit hooks, guard `npm install` behind a `package.json` check. `postStart.sh`: idempotent venv-usability re-check + hook reinstall. Drop the Stripe-CLI install step.
- **S4 — `dev.sh` + placeholder frontend.** `dev.sh` starts the Django API (`0.0.0.0:8000`) and a static file server for the frontend (`0.0.0.0:8080`) with prefixed output and clean shared-process-group shutdown. Omit the Stripe webhook forwarder and LLM worker; the salmon fish-count importer is an M2 scheduled job, not wired here. Add a minimal placeholder `index.html` to this frontend repo, clearly marked temporary (replaced in M4).
- **S5 — Verify & document.** Open the workspace in the devcontainer, run `dev.sh`, confirm both servers respond and `python manage.py check` passes against `mjt-pub-api` inside the container. Record an open-and-run guide + verification log in the workspace `README.md` (or a short `VERIFY.md`).

**Acceptance:**
- [ ] Workspace folder exists, is a git repo, and `origin` = `https://github.com/michaeljthacker/workspace-AreSalmonAtBallardLocks.git`.
- [ ] `AreSalmonAtBallardLocks.code-workspace` is valid JSON, defines exactly the three roots with correct relative paths, forwards ports 8000/8080, and contains no Stripe/LLM tasks.
- [ ] `devcontainer.json` is valid JSON and mounts all three roots; `postCreate.sh` / `postStart.sh` are present, executable, install backend deps from `mjt-pub-api/requirements/dev.txt`, and contain no Stripe-CLI/guide-worker setup.
- [ ] Inside the (re)built devcontainer, the backend venv is usable and `python manage.py check` runs against `mjt-pub-api` without import/env errors.
- [ ] `dev.sh` starts API (:8000) and static frontend (:8080), Ctrl+C stops both cleanly; `http://127.0.0.1:8000/` responds and `http://127.0.0.1:8080/` serves the placeholder `index.html`.
- [ ] A placeholder `index.html` exists in this frontend repo, marked temporary (replaced in M4).
- [ ] Workspace `README.md` documents the open-and-run steps and includes a verification log confirming each root opens, the devcontainer builds, and both servers respond.

## Notes / Dependencies
- **Devcontainer-first, no host-venv workflow.** The devcontainer owns venv creation and dependency install; verification happens inside it. This matches how `mjt-pub-api` is developed in other projects and keeps venv management simple. If a live rebuild can't be completed on the host during M1, note the exact gap in the S5 verification log rather than substituting a parallel host-venv path.
- **Shared-repo discipline (record during execution).** `mjt-pub-api` is now a registered `shared_repo`. Backend feature work branches off `main`, and because the backend is shared with other in-flight branches across projects, this project must not assume ownership of its working state. Capture this as a standing entry (DECISIONS.md and/or STANDARDS.md) when M1 executes. M1 itself does not edit backend code — it only bind-mounts the repo.
- **Backend dependency hygiene is OUT of B1.** Fixing `mjt-pub-api` dependabot / dependency warnings is **not** part of this build; recommended as a separate, wholly-unrelated `fix/` branch off `main` (shared-platform work, independently valuable and revertable, and B1 should build against the backend as-is). No M1 step performs dependency remediation. Pending human confirmation to record as a DECISIONS.md entry.
- **Adapt, don't clone (VISION §0, BUILD.md):** every artifact derives from `stencil-bible-guides` minus bible-guides-specific concerns. The name refers to the *workspace/devcontainer pattern*, not a mandated frontend framework.
- **Step order is sequential:** S1 → S2 → S3 → S4 → S5; each step's artifacts feed the next.
- **No product scope here:** data models (`sighting_report`, `fish_count`), endpoints, importer, aggregation, forecast, and the real frontend are all M2–M5 (see BUILD.md).
