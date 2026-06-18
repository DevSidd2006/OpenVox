#!/usr/bin/env bash
set -euo pipefail

# Records a short clip, sends to local server, and copies polished text to clipboard.
# Requires: arecord, curl, jq, xclip (X11) or wl-copy (Wayland).

API_URL="${OPENVOX_API_URL:-http://127.0.0.1:8080}"
TMP_WAV="/tmp/openvox_$(date +%s).wav"

# 8 second push-to-talk style capture. Adjust duration as needed.
arecord -f cd -t wav -d 8 "$TMP_WAV" >/dev/null 2>&1

JSON=$(curl -sS -X POST "$API_URL/api/transcribe" \
  -F "audio=@${TMP_WAV};type=audio/wav" \
  -F "style=professional" \
  -F "context=email" \
  -F "language=en" \
  -F "auto_rewrite=true")

TEXT=$(echo "$JSON" | jq -r '.rewritten_text // .transcript // empty')

if [ -z "$TEXT" ]; then
  echo "No text returned" >&2
  rm -f "$TMP_WAV"
  exit 1
fi

if command -v wl-copy >/dev/null 2>&1; then
  printf '%s' "$TEXT" | wl-copy
elif command -v xclip >/dev/null 2>&1; then
  printf '%s' "$TEXT" | xclip -selection clipboard
else
  echo "Install wl-copy or xclip for clipboard integration." >&2
fi

# Optional: auto-paste in active window (requires xdotool and X11).
if command -v xdotool >/dev/null 2>&1; then
  xdotool key --clearmodifiers ctrl+v || true
fi

rm -f "$TMP_WAV"
echo "OpenVox dictation copied to clipboard"
