# OpenVox Rename Design

**Date:** 2026-06-18
**Status:** Approved for implementation

## Overview

Rename the project from "Lynx" (codename) / "Willow" (original) to **OpenVox** across all source code, file names, environment variables, and documentation. Code-only rename — no logo/brand assets.

## Mapping Rules

| Pattern | Replace with | Example |
|---------|-------------|---------|
| `Lynx` (display) | `OpenVox` | Window titles, labels, user-facing text |
| `lynx` (internal) | `openvox` | File paths, log prefixes, temp files |
| `Willow` (project ref) | `OpenVox` | Env var origin, docs |
| `WILLOW_*` | `OPENVOX_*` | All environment variables |
| `willow-groq-clone` | `openvox` | Systemd service names, git URLs |

## Scope

### A. Source Code Strings

| File | Changes |
|------|---------|
| `app/__init__.py` | Package docstring |
| `app/main.py` | FastAPI title |
| `app/prompts.py` | System prompt identity |
| `app/config.py` | Database path |
| `desktop/app.py` | Window title, env vars, systemd service names |
| `scripts/hotkey_push_to_talk.py` | Docstring + import path |
| `scripts/lynx_daemon/__init__.py` | Package docstring |
| `scripts/lynx_daemon/config.py` | All `WILLOW_*` → `OPENVOX_*` |
| `scripts/lynx_daemon/tray.py` | Window titles, log prefixes, notify messages |
| `scripts/lynx_daemon/recorder.py` | Temp file prefix, multipart boundary |
| `scripts/lynx_daemon/notifier.py` | Notify-send app name |
| `web/index.html` | Page title, logo text, subtitle |

### B. Environment Variables (`.env` + `.env.example`)

- `WILLOW_CLONE_URL` → `OPENVOX_API_URL`
- `WILLOW_HOTKEY` → `OPENVOX_HOTKEY`
- `WILLOW_STYLE` → `OPENVOX_STYLE`
- `WILLOW_CONTEXT` → `OPENVOX_CONTEXT`
- `WILLOW_LANGUAGE` → `OPENVOX_LANGUAGE`
- `WILLOW_AUTO_PASTE` → `OPENVOX_AUTO_PASTE`
- `WILLOW_INSERT_MODE` → `OPENVOX_INSERT_MODE`
- `WILLOW_OVERLAY` → `OPENVOX_OVERLAY`
- `WILLOW_AUDIO_FEEDBACK` → `OPENVOX_AUDIO_FEEDBACK`
- `WILLOW_OVERLAY_POSITION` → `OPENVOX_OVERLAY_POSITION`
- `WILLOW_VAD_ENABLED` → `OPENVOX_VAD_ENABLED`
- `WILLOW_VAD_SILENCE_TIMEOUT` → `OPENVOX_VAD_SILENCE_TIMEOUT`
- `WILLOW_VAD_AGGRESSIVENESS` → `OPENVOX_VAD_AGGRESSIVENESS`

### C. File/Directory Renames

- `scripts/lynx_daemon/` → `scripts/openvox_daemon/`
- `scripts/lynx_toggle.sh` → `scripts/openvox_toggle.sh`

### D. Systemd Services

- `willow-groq-clone-api.service` → `openvox-api.service`
- `willow-groq-clone-hotkey.service` → `openvox-hotkey.service`

### E. Documentation

- `README.md` — full rewrite with OpenVox branding
- `CONTRIBUTING.md` — updated references
- `ROADMAP.md` — updated title
- `.planning/` files — updated references

### F. Shell Scripts

All 11 scripts in `scripts/` — update references to file paths, service names, log messages, env vars.

## What We Don't Change

- `GROQ_*` env vars (provider-specific, not project-specific)
- `data/lynx.db` (runtime artifact; recreated on next run)
- Git internals (repo rename handled separately)

## Implementation Approach

Bulk automated sweep using `sed`/`rg` with verification pass.

1. String replacements across all file types
2. File/directory renames
3. Import path updates
4. Verification: `rg -i 'lynx|willow|willow-groq-clone'` → zero matches

## Verification

- `rg -i 'lynx|willow' --include='*.py' --include='*.{html,js,css}' --include='*.sh' --include='*.md' --include='*.example'` returns nothing
- All imports resolve correctly
- `python -c "from app.main import app"` succeeds
- `python -c "from openvox_daemon.tray import run_daemon"` succeeds (after rename)
