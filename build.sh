#!/bin/bash
set -ex

# Local development setup
python3.8 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install pipenv
pipenv install --dev

flask db upgrade
flask seed run  # If you have seed data