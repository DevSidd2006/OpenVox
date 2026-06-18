# Technology Stack

**Analysis Date:** 2026-04-01

## Languages

**Primary:**
- Python 3.12 - Backend API, hotkey daemon, desktop controller
- JavaScript (ES6) - Frontend web application
- HTML5 / CSS3 - Web UI

**Secondary:**
- Bash - Startup scripts and service installation

## Runtime

**Environment:**
- Python 3.12 virtual environment (`.venv/`)
- System Python 3 available for bootstrap only

**Package Manager:**
- pip (via `.venv/bin/pip`)
- Lockfile: Not present (direct `pip install -r requirements.txt`)

## Frameworks

**Core:**
- FastAPI 0.35.x - REST API framework
- Starlette 0.41.x - ASGI framework (FastAPI dependency)
- uvicorn 0.35.x - ASGI server

**Database:**
- sqlite3 (stdlib) - Primary database via Python's built-in sqlite3
- No ORM - Raw SQL with sqlite3.Row factory and context managers

**AI/ML:**
- groq 0.31.x - Groq API SDK for Whisper transcription and LLM rewriting

**Hotkey Daemon:**
- pynput - Global keyboard listener for hotkey detection
- webrtcvad - Voice Activity Detection for silence-based auto-stop
- pystray - System tray icon
- PIL (Pillow) - Icon image generation for system tray
- tkinter - Voice overlay window (floating audio visualizer)

**Desktop UI:**
- tkinter (stdlib) - Desktop controller app for local development

**Frontend:**
- Vanilla JavaScript (ES6) - No framework
- Inter font from Google Fonts
- Fetch API for HTTP requests

## Key Dependencies

**Critical:**
- `groq` - All AI transcription and rewriting
- `fastapi` - API server
- `uvicorn` - ASGI server runner

**Hotkey Daemon:**
- `pynput` - Global hotkey listener (from requirements-hotkey.txt)
- `webrtcvad` - Voice activity detection (from requirements-hotkey.txt)
- `pystray` - System tray icon (from requirements-hotkey.txt)
- `Pillow` - Tray icon image generation (from requirements-hotkey.txt)

**Configuration:**
- `python-dotenv` - Environment variable loading from `.env`

## Configuration

**Environment:**
- `.env` file at project root
- Loaded via `dotenv.load_dotenv()` in both `app/config.py` and `scripts/openvox_daemon/config.py`
- No `.env` validation library - silent defaults if missing

**Build:**
- No build step for Python (interpreted)
- Frontend is static files served directly

**Key env vars:**
- `GROQ_API_KEY` - Groq API authentication
- `GROQ_STT_MODEL` - Whisper model (default: whisper-large-v3-turbo)
- `GROQ_TEXT_MODEL` - LLM model (default: llama-3.3-70b-versatile)
- `HOST` / `PORT` - API server binding
- `OPENVOX_CLONE_URL` - Daemon's API endpoint
- `OPENVOX_HOTKEY` - Push-to-talk hotkey (default: ctrl+space)
- `OPENVOX_STYLE` / `OPENVOX_CONTEXT` / `OPENVOX_LANGUAGE` - Default rewriting parameters
- `OPENVOX_AUTO_PASTE` / `OPENVOX_INSERT_MODE` - Clipboard behavior
- `OPENVOX_OVERLAY` - Enable/disable voice overlay
- `OPENVOX_AUDIO_FEEDBACK` - Sound notifications
- `OPENVOX_VAD_ENABLED` / `OPENVOX_VAD_SILENCE_TIMEOUT` / `OPENVOX_VAD_AGGRESSIVENESS` - VAD settings

## Platform Requirements

**Development:**
- Python 3.12+
- pip
- bash
- Internet connection (for Groq API)

**Production (API server):**
- Linux (systemd assumed)
- Python 3.12
- Ports available: 8080 (or custom)

**Hotkey Daemon:**
- Linux with X11 or Wayland display server
- ALSA utilities (`arecord` from alsa-utils)
- Global hotkey support requires X11 or Wayland with input group membership

**System dependencies (per bootstrap.sh):**
- For X11: `xclip`, `xdotool`
- For Wayland: `wl-clipboard`, `wtype`
- For system tray on GNOME Wayland: `gir1.2-ayatanaappindicator3-0.1`
- Audio feedback: `paplay` (PulseAudio) or `pw-play` (PipeWire) or `aplay` (ALSA)

---

*Stack analysis: 2026-04-01*
