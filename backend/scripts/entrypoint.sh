#!/bin/bash
set -e

echo "Starting Academic Integrity Platform Backend..."

# Wait for database to be ready
echo "Waiting for PostgreSQL..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.5
done
echo "✓ PostgreSQL is ready"

# Wait for Redis
echo "Waiting for Redis..."
while ! nc -z redis 6379; do
  sleep 0.5
done
echo "✓ Redis is ready"

# Run database migrations
echo "Running database migrations..."
python scripts/init_db.py

# Start application
echo "✓ Starting application..."
exec "$@"
