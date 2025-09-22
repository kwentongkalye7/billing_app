PROJECT_NAME=unified-billing

init:
	python3 -m venv .venv && . .venv/bin/activate && pip install -r backend/requirements.txt && npm --prefix frontend install

up:
	docker compose up --build

up-detach:
	docker compose up --build -d

stop:
	docker compose stop

down:
	docker compose down

migrate:
	docker compose run --rm backend python manage.py migrate

createsuperuser:
	docker compose run --rm backend python manage.py createsuperuser

test:
	docker compose run --rm backend python manage.py test

lint-frontend:
	npm --prefix frontend run lint

build-frontend:
	npm --prefix frontend run build

pdf-smoke:
	docker compose run --rm backend python manage.py shell -c "from statements.models import BillingStatement; from statements.pdf import render_statement_pdf; qs = BillingStatement.objects.first(); print(render_statement_pdf(qs) if qs else 'No statements yet')"

.PHONY: init up up-detach stop down migrate createsuperuser test lint-frontend build-frontend pdf-smoke
