#!/bin/bash
set -e

echo "=== Online Poll System Setup ==="

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Setup .env
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env from .env.example — please update your credentials."
fi

# Create directories
mkdir -p logs media staticfiles

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

echo "=== Setup complete! ==="
echo "Run: source venv/bin/activate && python manage.py runserver"