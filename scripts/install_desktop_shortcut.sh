#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DESKTOP_FILE="$HOME/.local/share/applications/openvox.desktop"

cat > "$DESKTOP_FILE" <<EOD
[Desktop Entry]
Type=Application
Name=OpenVox
Exec=$ROOT_DIR/scripts/run_desktop_app.sh
Terminal=false
Categories=Utility;
EOD

chmod +x "$DESKTOP_FILE"
echo "Desktop shortcut created at: $DESKTOP_FILE"
