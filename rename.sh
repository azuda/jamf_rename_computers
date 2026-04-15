#!/bin/sh
PROJECT="$PWD"
VENV="$PROJECT/.venv/bin/python3"
LOG_DIR="$PROJECT/logs"
LATEST_LOG=$(ls -1t "$LOG_DIR"/*.log 2>/dev/null | head -n 1)

if [ -z "$LATEST_LOG" ]; then
	timestamp=$(date '+%Y-%m-%d_%H-%M-%S')
	LOG_FILE="$LOG_DIR/$timestamp.log"
	mkdir -p "$LOG_DIR"
else
	LOG_FILE="$LATEST_LOG"
fi

export LOG_FILE

echo "\n------------------------------------------\n" >> "$LOG_FILE"
echo "rename.sh start @ $(date)" >> "$LOG_FILE"

$VENV rename.py >> "$LOG_FILE" 2>&1

echo "rename.sh end @ $(date)" >> "$LOG_FILE"
