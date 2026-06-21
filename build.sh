#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Compile static assets
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Seed data
python seed_data.py
