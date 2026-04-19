#!/bin/bash
DATE=$(date +%Y-%m-%d)
echo "[$DATE] Starte Backup..."

rclone sync /home/jens/JobAgent gdrive:JensHQ_Backup/RasPi \
  --exclude ".git/**" \
  --exclude "__pycache__/**" \
  --exclude "*.pyc" \
  --log-file=/home/jens/JobAgent/logs/backup.log

echo "[$DATE] Backup fertig!"
