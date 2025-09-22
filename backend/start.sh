#!/bin/bash
set -euo pipefail

python manage.py migrate --noinput
python manage.py collectstatic --noinput

gunicorn billing_project.wsgi:application --bind 0.0.0.0:8000 --workers ${GUNICORN_WORKERS:-3}
