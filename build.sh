#!/bin/bash
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Run database migrations
flask db upgrade

# Collect static files (if needed)
# python manage.py collectstatic --noinput
