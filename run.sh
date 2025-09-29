#!/bin/sh

PROJECT="$PWD"
VENV="$PROJECT/.venv/bin/python3"

LOG_DIR="$PROJECT/logs"
LOG_FILE="$LOG_DIR/$(date '+%Y-%m-%d_%H-%M-%S').log"
mkdir -p "$LOG_DIR"
ls -1t "$LOG_DIR" | tail -n +5 | xargs -I {} rm -f "$LOG_DIR/{}"

echo "Script start @ $(date)" >> "$LOG_FILE"

$VENV query_jamf.py >> "$LOG_FILE" 2>&1
$VENV parse.py >> "$LOG_FILE" 2>&1
# $VENV rename.py >> "$LOG_FILE" 2>&1

echo "Script end @ $(date)" >> "$LOG_FILE"
