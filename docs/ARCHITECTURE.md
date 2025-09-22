# Unified Billing Web App — Architecture Overview

This document captures the high-level application architecture derived from the Product Requirement Prompt (PRP), payments business flow, and swimlane diagram. It is intended to guide development and onboarding of new contributors.

## Goals & Principles
- **Beginner-friendly**: intuitive setup, descriptive help text, extensive documentation.
- **Monolith-first**: Django serves API, admin, and background tasks in a single project; React handles the interactive UI.
- **Manual-first payments**: application enforces manual allocation, unapplied credits, and period locks.
- **Auditability**: every sensitive mutation is logged with before/after snapshots.
- **Portability**: containerized stack runs on macOS (dev), Windows + WSL2 (ops laptop), and future Linux VM.

## Logical Components
```
backend/
  billing_project/            # Django project configuration
  common/                     # Shared utilities, base models, mixins
  accounts/                   # Custom User model, role-based access control
  clients/                    # Client & Contact master data
  engagements/                # Retainer and Special engagement management
  statements/                 # Billing statements (SOAs), items, issuance logic
  payments/                   # Payments, allocations, unapplied credits, status rules
  sequences/                  # Number series management (SOA, payments, etc.)
  reports/                    # Aggregated read models & analytics endpoints
  audit/                      # Audit logging infrastructure
  integrations/pdf/           # Playwright-driven PDF rendering service
frontend/
  src/                        # Vite + React + Tailwind web client
  public/                     # Static assets (logos, manifest)
docs/
  ARCHITECTURE.md             # This doc
  DATA_MODEL.md               # Entity relationships & field glossary
  OPERATIONS.md               # Runbook for admins/ops (backups, sequences, locks)
```

### Backend
- **Framework**: Django 5 + Django REST Framework.
- **Database**: PostgreSQL (via Docker Compose); future cloud migration uses the same DSN.
- **Apps**: segmented by business capability (clients, engagements, statements, payments, sequences, reports, audit, accounts).
- **Auth**: Django custom user with role choices (`Admin`, `Biller`, `Reviewer`, `Viewer`) mapped to DRF permissions.
- **Admin Site**: customized admin for quick CRUD/import staging.
- **Background Jobs**: Django management commands (e.g., `run_retainer_cycle`) invoked via CLI or scheduled with cron/Task Scheduler.
- **PDF Engine**: Playwright headless Chromium; HTML templates stored under `statements/templates/`.
- **Storage**: PDFs saved locally (mounted volume), path recorded in statement records.

### Frontend
- **Framework**: Vite + React + TypeScript + Tailwind CSS.
- **State**: React Query for data fetching/cache, Zustand for lightweight UI state.
- **Routing**: React Router with protected routes per RBAC role.
- **Components**: Form wizards, tables with quick filters, tooltips, onboarding modals.
- **PDF Links**: Serve generated PDFs from backend static files; frontend displays preview links.

### Docker & Tooling
- **docker-compose.yml** orchestrates services:
  - `backend` (Django + Gunicorn + Playwright drivers)
  - `frontend` (Vite dev server or Nginx for prod build)
  - `db` (PostgreSQL 15)
  - `caddy` (reverse proxy; automatic HTTPS ready)
  - `worker` (optional, same image as backend for cron-style jobs)
- **Makefile** shortcuts: `make init`, `make up`, `make migrate`, `make seed`, `make test`, `make pdf-smoke`.
- **.env files**: `.env.example` for shared config; `.env.development` for local overrides.

## Data Flow Summary
1. **Master Data**: Clients & engagements created via UI or import staging -> reviewer approval -> active status.
2. **Retainer Cycle Runner**: CLI command or UI trigger generates draft SOAs (idempotent by client+engagement+period).
3. **Special SOAs**: Created on demand, awaiting reviewer issue.
4. **Issuance**: Reviewer assigns next number from sequence, locks items, renders PDF, status -> `issued`.
5. **Payments**: Biller records payment with manual invoice number, method, OR/ref -> manually applies allocations to one/many SOAs -> remainder stored as UnappliedCredit -> Reviewer verifies -> status -> `verified`.
6. **Reporting**: REST endpoints aggregate balances, aging buckets, collections register, audit log exports.
7. **Audit Trail**: Signals capture create/update/void/apply events with diff snapshots persisted in `AuditLog`.

## Security & Compliance
- Role-based permissions enforced at API, service, and UI level.
- Period/sequence locks prevent mutation post-close; Admin-only overrides.
- All monetary amounts stored as `Decimal(12,2)`; totals exclude tax/withholding by design.
- Manual invoice number recorded but never generated.
- Input validation ensures PHP currency, allowed payment methods, manual allocations only.

## Extensibility Considerations
- **Cloud Migration**: switch `DATABASE_URL`, configure object storage for PDFs, update Caddy TLS.
- **Future Enhancements**: automatic email dispatch, scheduler for retainer runner, Sentry integration, additional branches.

## References
- Product Requirement Prompt — `context/product_requirement_prompt_prp_unified_billing_web_app.md`
- Payments Flow & Data Model v2 — `context/business_flow_payments_manual_first_data_model_v_2.md`
- Swimlane Flowchart (React) — `context/swimlane_flowchart_unified_billing_web_app-2.jsx`
