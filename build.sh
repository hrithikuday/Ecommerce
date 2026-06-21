#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Compile static assets
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Seed data on every deploy (required for ephemeral SQLite database)
python seed_data.py
