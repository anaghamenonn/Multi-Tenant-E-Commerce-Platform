#!/usr/bin/env bash
set -o errexit

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Run Django database migrations (no input required)
python manage.py migrate --noinput

# Collect static files (no input required)
python manage.py collectstatic --noinput
