#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

# Install requirements
.venv/bin/python3 -m pip install --upgrade pip
.venv/bin/python3 -m pip install -r requirements.txt

echo "Core bootstrap complete"
echo ""
echo "If you want global hotkey daemon:"
echo "  pip install -r requirements-hotkey.txt"
echo ""
echo "System dependencies (choose based on your display server):"
echo ""
echo "  X11 (Xorg):"
echo "    sudo apt install xclip xdotool"
echo ""
echo "  Wayland (Ubuntu 22.04+ default — 'normal Ubuntu'):"
echo "    sudo apt install wl-clipboard wtype ydotool"
echo "    sudo apt install gir1.2-ayatanaappindicator3-0.1   # system tray on GNOME"
echo ""
echo "  Global hotkeys on Wayland (choose one):"
echo "    Option A (recommended): Map ./scripts/openvox_toggle.sh as a GNOME custom shortcut."
echo "    Option B: sudo usermod -aG input \$USER   (then log out and back in)"
echo ""
