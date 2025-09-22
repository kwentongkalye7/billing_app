# Operations Runbook

## Daily Tasks
- **Login & Health Check**
  1. Access `http://localhost` (or laptop hostname) to ensure the app loads.
  2. Check Django admin `/admin` → `Audit logs` for overnight activity.
- **Retainer Cycle**
  - Run monthly via UI (`Statements → Run Retainer Cycle`) or CLI:
    ```bash
    docker compose run --rm backend python manage.py run_retainer_cycle 2025-09 --user admin
    ```
  - Reviewer issues drafts after review to lock content and assign numbers.
- **Payments Verification**
  - Biller records payments with manual invoice number and allocations.
  - Reviewer hits “Mark Verified” once supporting documents are confirmed.

## Backups
- **Database**: `docker compose exec db pg_dump -U billing_app billing_app > backups/$(date +%F).sql`
- **Media/PDFs**: copy `backend/media/` directory (contains generated SOAs & logos).
- Store backups on an encrypted external drive or secure cloud bucket.

## Disaster Recovery
1. Restore database backup into Postgres (`psql < backup.sql`).
2. Restore `media/` directory.
3. Set environment variables via `.env` and run `docker compose up --build`.

## Sequence Management
- Admins adjust numbering in Django admin → `Sequences`.
- To preview next number: use admin inline or API `/sequences/{id}/next_number/`.

## Period Locks & Voids
- Once period is closed, Admin can enforce lock by updating statements to `issued/settled` only.
- Void process: `Statements` → `Void` with reason (auto logs + retains number). Reissue via clone/draft.

## Monitoring & Logs
- Backend stdout logs via `docker compose logs backend`.
- Structured audit data in admin → `Audit logs`.
- For PDF generation issues, check Playwright output (`backend/media/pdf/statements`).

## Windows Laptop Deployment Steps
1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) with WSL2.
2. Clone repo and copy `.env.example` to `.env` (adjust secrets).
3. Run `docker compose up --build` from PowerShell.
4. Access app via `http://localhost`.

## Future Cloud Lift
- Provision small Ubuntu VM (4GB RAM) with Docker & Docker Compose installed.
- Copy repo + `.env` and run `docker compose up --build -d`.
- Point DNS to VM, enable TLS via Caddy (set `CADDY_TLS_EMAIL` + domain in `Caddyfile`).

## Support Checklist
- Can't log in? Reset password via `docker compose run --rm backend python manage.py changepassword <user>`.
- PDFs blank? Re-run `docker compose run --rm backend playwright install chromium`.
- Sequence mismatch? Reset via Django admin and reissue (void retains original number).
