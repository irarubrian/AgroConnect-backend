#!/bin/bash
set -ex  # Enable debugging and exit on error

# 1. Verify Python version matches runtime.txt
python --version

# 2. Install dependencies
pip install --upgrade pip
pip install pipenv
pipenv install --system --deploy

# 3. Database migrations
flask db upgrade

# 4. Verify installed packages
pip freeze