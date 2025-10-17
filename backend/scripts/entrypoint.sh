#!/bin/bash
set -e

echo "Starting Academic Integrity Platform Backend..."

# Docker compose already handles dependencies with healthchecks
# No need to wait manually

# Start application
echo "✓ Starting application..."
exec "$@"
