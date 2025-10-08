#!/bin/sh

PROJECT="$PWD"
VENV="$PROJECT/.venv/bin/python3"

LOG_DIR="$PROJECT/logs"
timestamp=$(date '+%Y-%m-%d_%H-%M-%S')
LOG_FILE="$LOG_DIR/$timestamp.log"
export LOG_FILE="$LOG_DIR/$timestamp.log"

mkdir -p "$LOG_DIR"
ls -1t "$LOG_DIR" | tail -n +5 | xargs -I {} rm -f "$LOG_DIR/{}"

echo "run.sh start @ $(date)" >> "$LOG_FILE"

$VENV query_jamf.py >> "$LOG_FILE" 2>&1
$VENV parse.py >> "$LOG_FILE" 2>&1
$VENV rename.py >> "$LOG_FILE" 2>&1

echo "run.sh end @ $(date)" >> "$LOG_FILE"
