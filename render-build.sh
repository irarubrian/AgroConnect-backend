#!/bin/bash
set -ex

# 1. Verify Python version
python --version

# 2. Install dependencies from requirements.txt
pip install --upgrade pip
pip install -r requirements.txt

# 3. Run migrations if database exists
if [ -d "migrations" ]; then
  flask db upgrade
fi

# 4. Verify critical paths
ls -la
python -c "from wsgi import app; print(app)"