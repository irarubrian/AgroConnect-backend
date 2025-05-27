#!/bin/bash
set -o errexit

# Install Poetry if needed
if ! command -v poetry &> /dev/null; then
    pip install poetry
fi

# Install dependencies
poetry install --no-interaction --no-ansi

# Run migrations
poetry run flask db upgrade