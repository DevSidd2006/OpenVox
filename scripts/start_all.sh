#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "Stopping existing processes..."
pkill -f "uvicorn app.main:app" || true
pkill -f "scripts/hotkey_push_to_talk.py" || true
fuser -k 18080/tcp 2>/dev/null || true

if [ ! -d ".venv" ]; then
  echo "Virtual environment not found. Running bootstrap..."
  bash scripts/bootstrap.sh
fi

source .venv/bin/activate

echo "Starting backend server..."
export HOST=${HOST:-127.0.0.1}
export PORT=${PORT:-18080}
# Start backend in background
bash scripts/start.sh > backend.log 2>&1 &
BACKEND_PID=$!

echo "Waiting for backend to be ready..."
MAX_RETRIES=30
COUNT=0
until curl -s "http://$HOST:$PORT/api/health" | grep -q "ok"; do
  if [ $COUNT -ge $MAX_RETRIES ]; then
    echo "Backend failed to start"
    exit 1
  fi
  sleep 1
  COUNT=$((COUNT + 1))
done
echo "Backend is ready."

echo "Starting hotkey daemon..."
# Start hotkey daemon in background
bash scripts/run_hotkey_daemon.sh > hotkey.log 2>&1 &
DAEMON_PID=$!

echo "--------------------------------------------------"
echo "OpenVox is now running!"
echo "Backend PID: $BACKEND_PID (logs: backend.log)"
echo "Hotkey PID:  $DAEMON_PID (logs: hotkey.log)"
echo "--------------------------------------------------"
echo "Use 'pkill -f uvicorn' and 'pkill -f hotkey_push_to_talk' to stop."
