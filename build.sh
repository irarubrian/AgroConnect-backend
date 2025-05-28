#!/bin/bash
echo "Installing dependencies..."
pipenv install -r requirements.txt

# Optional: Migrations
echo "Running migrations..."
alembic upgrade head
