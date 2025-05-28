#!/bin/bash
set -ex  # Enable debugging

# 1. Ensure correct Python version
python3.8 --version

# 2. Install Pipenv explicitly
python3.8 -m pip install --upgrade pip
python3.8 -m pip install pipenv

# 3. System-wide install
python3.8 -m pipenv install --system --deploy

# 4. Verify installed packages
pip freeze

# 5. Run migrations
python3.8 -m flask db upgrade