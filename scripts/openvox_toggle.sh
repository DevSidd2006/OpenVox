#!/usr/bin/env bash
# Toggles OpenVox recording by sending a SIGUSR1 to the hotkey daemon.
# Useful for Wayland users who want to map a system shortcut.

DAEMON_PROC="scripts/hotkey_push_to_talk.py"

# Try to find the PID
PID=$(pgrep -f "$DAEMON_PROC")

if [ -z "$PID" ]; then
    echo "OpenVox hotkey daemon is not running."
    exit 1
fi

# Send SIGUSR1 to toggle recording
kill -USR1 "$PID"
echo "Sent toggle signal to OpenVox daemon (PID: $PID)"
