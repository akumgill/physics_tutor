#!/bin/bash

# Install requirements
pip install -r requirements.txt

# Clean up existing database and migrations
rm -f db.sqlite3
rm -rf storyboard/migrations

# Set up new database
python manage.py makemigrations storyboard
python manage.py migrate

# Run startup script through Django shell
python manage.py shell << EOF
from storyboard import views
views.startup()
exit()
EOF

# Start development server
python manage.py runserver
