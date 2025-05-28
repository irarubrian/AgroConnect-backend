#!/bin/bash
set -o errexit

# Install Pipenv
pip install pipenv

# Install dependencies system-wide
pipenv install --system --deploy

# Run migrations
flask db upgrade