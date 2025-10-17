#!/bin/bash
# Database backup script

set -e

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/academic_integrity_${DATE}.sql"

echo "Starting backup at $(date)"

# Create backup directory if it doesn't exist
mkdir -p ${BACKUP_DIR}

# Perform backup
pg_dump -h postgres -U ${POSTGRES_USER} ${POSTGRES_DB} > ${BACKUP_FILE}

# Compress backup
gzip ${BACKUP_FILE}

echo "✓ Backup completed: ${BACKUP_FILE}.gz"

# Delete backups older than 30 days
find ${BACKUP_DIR} -name "*.sql.gz" -mtime +30 -delete

echo "✓ Old backups cleaned up"
echo "Backup finished at $(date)"
