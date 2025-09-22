# Unified Billing Web App

A monolith-first Django + React implementation that replaces the legacy Excel tools for retainers & special engagement billing. It streamlines statements of account (SOA) generation, manual-first payments, unapplied credits, PDF output, and audit-ready reporting.

## Highlights
- **Unified master data** for clients, contacts, engagements, and SOAs.
- **Retainer cycle runner** generates draft statements per period (idempotent).
- **Manual-first payments** enforce manual invoice capture, manual allocation, and unapplied credits.
- **PDF engine** uses Playwright/Chromium for consistent SOA templates.
- **RBAC** roles (Admin, Biller, Reviewer, Viewer) with audit logs for every sensitive action.
- **Dockerized** stack that runs the same way on macOS (dev), Windows + WSL2 (ops laptop), and Linux VMs (future cloud).

## Stack
- **Backend**: Django 5, Django REST Framework, PostgreSQL, Playwright (PDF)
- **Frontend**: React 18, Vite, Tailwind CSS, React Query, Zustand
- **Proxy**: Caddy (reverse proxy, future TLS)

## Repository Layout
```
backend/     # Django project, apps, tests, Dockerfile
frontend/    # Vite React client with Tailwind
docs/        # Architecture, data model, operations runbooks
ops/         # Caddy config, infra helpers
context/     # Reference materials from legacy tools (read-only)
```

## Quick Start (Docker)
1. Copy environment template and adjust if needed:
   ```bash
   cp .env.example .env
   ```
2. Build and start the stack:
   ```bash
   docker compose up --build
   ```
3. Visit the following:
   - Frontend: <http://localhost>
   - API (Swagger): <http://localhost/api/docs/swagger/>
   - Django admin: <http://localhost/api/admin/> (create a superuser first)

### Create a superuser
```bash
docker compose run --rm backend python manage.py createsuperuser
```

### Stop / teardown
```bash
docker compose stop          # stop services
docker compose down          # stop + remove containers (data persists via volumes)
```

## macOS Local Development (without Docker)
1. **Backend**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r backend/requirements.txt
   cd backend
   cp ../.env.example ../.env
   python manage.py migrate
   python manage.py runserver 0.0.0.0:8000
   ```
2. **Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
3. Access the app at <http://localhost:5173> (frontend proxying API calls to `http://localhost:8000/api`).

## Windows (Docker Desktop + WSL2)
1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and ensure WSL2 integration is enabled.
2. Clone the repo inside your WSL2 distro (e.g., Ubuntu).
3. Copy `.env.example` to `.env` and review secrets.
4. Run `docker compose up --build`.
5. Open <http://localhost> from the Windows browser. Docker Desktop handles port forwarding.

## Core Workflows
- **Retainer cycle**: `Statements → Run Retainer Cycle` (UI) or `python manage.py run_retainer_cycle 2025-09 --user <username>`.
- **Issue SOA**: Reviewer opens Statements table → `Issue & PDF` (assigns number, locks content, generates Playwright PDF).
- **Record payment**: Payments screen captures method, manual invoice no., optional initial allocation. Any leftover creates an `UnappliedCredit`.
- **Manual allocation**: Use the “Optional Allocate now” field or edit later; the system never auto-applies funds.
- **Verify payment**: Reviewer clicks “Mark Verified” after documents are reviewed.
- **Void**: Available on statements/payments with required reason; numbers remain reserved; audit entry created.

## Testing & Linting
```bash
# Django tests (retainer cycle + payment scenarios)
docker compose run --rm backend python manage.py test

# React lint (optional)
npm --prefix frontend run lint
```

## PDF Smoke Test
Generate a sample PDF after issuing a statement:
```bash
make pdf-smoke
```
Output path will be printed (stored under `backend/media/pdf/statements/`).

## Data Imports
- Use Django admin for CSV/XLSX staging (future enhancement hook).
- Tags, aliases, and branding assets are available per client for PDF overrides.

## Additional Documentation
- `docs/ARCHITECTURE.md` — high-level system design.
- `docs/DATA_MODEL.md` — entity glossary & relationships.
- `docs/OPERATIONS.md` — runbook for admins, backups, and troubleshooting.

## Future Enhancements (Suggested)
1. Email dispatch with secure attachments (post-PDF issuance).
2. Scheduled job container for automated retainer runs.
3. Sentry or similar error monitoring.
4. Import wizards for legacy Excel data with row-level validation.
