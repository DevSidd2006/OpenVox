# Codebase Structure

**Analysis Date:** 2026-04-01

## Directory Layout

```
/home/devisdd/OpenVox/
├── app/                    # Python backend (FastAPI)
├── desktop/                # Tkinter desktop controller app
├── scripts/                # Shell scripts and hotkey daemon
│   └── openvox_daemon/        # Python daemon modules
├── web/                    # Frontend (HTML/CSS/JS)
├── data/                   # SQLite database
├── docs/                   # Documentation
├── .venv/                  # Python virtual environment
├── .env                    # Environment configuration
├── .env.example            # Environment template
├── requirements.txt        # Core Python dependencies
├── requirements-hotkey.txt # Hotkey daemon dependencies
└── README.md               # Project documentation
```

## Directory Purposes

### `app/`
- **Purpose:** Python backend serving the REST API
- **Contains:** FastAPI app, database layer, Groq client, Pydantic models
- **Key files:**
  - `main.py` - FastAPI application entry point
  - `db.py` - SQLite connection management and queries
  - `groq_client.py` - Groq API wrapper
  - `models.py` - Pydantic request/response models
  - `prompts.py` - System prompt builder for LLM rewriting
  - `config.py` - Settings dataclass from environment

### `desktop/`
- **Purpose:** Tkinter GUI for local development (starts API + hotkey daemon, edits `.env`)
- **Contains:** Single `app.py` with DesktopApp class

### `scripts/`
- **Purpose:** Shell runners and the hotkey daemon package
- **Key files:**
  - `bootstrap.sh` - Initial setup (venv + pip install)
  - `start_prod.sh` - Production API server runner
  - `run_hotkey_daemon.sh` - Hotkey daemon runner
  - `start_all.sh` - Starts both API and hotkey daemon
  - `hotkey_push_to_talk.py` - Daemon entry point (imports openvox_daemon)
  - `install_user_service.sh` - systemd user service installer

### `scripts/openvox_daemon/`
- **Purpose:** Python package for the push-to-talk daemon (imported by hotkey_push_to_talk.py)
- **Key files:**
  - `recorder.py` - PushToTalk class: recording, VAD, API call, clipboard/typing
  - `overlay.py` - VoiceOverlay class: Tkinter floating audio visualizer
  - `tray.py` - SystemTrayIcon class and `run_daemon()` function
  - `clipboard.py` - `copy_to_clipboard()` and `paste_into_active_window()`
  - `vad.py` - VoiceActivityDetector wrapper around webrtcvad
  - `config.py` - DaemonConfig dataclass (OPENVOX_* env vars)
  - `audio_feedback.py` - Sound playback via paplay/pw-play/aplay
  - `notifier.py` - System notifications via notify-send
  - `rms.py` - Audio level calculator
  - `__init__.py` - Empty (package marker)

### `web/`
- **Purpose:** Browser-based single-page application
- **Contains:** `index.html`, `app.js`, `styles.css`
- **Note:** Served by FastAPI from `web/` directory via `StaticFiles`

### `data/`
- **Purpose:** Persistent storage
- **Contains:** `openvox.db` (SQLite database), `.gitkeep`

### `docs/`
- **Purpose:** Additional documentation

## Key File Locations

### Entry Points
- `app/main.py` - FastAPI app (run via `uvicorn app.main:app`)
- `scripts/hotkey_push_to_talk.py` - Hotkey daemon entry point
- `desktop/app.py` - Tkinter desktop controller

### Configuration
- `.env` - Runtime environment variables (GROQ_API_KEY, OPENVOX_* settings)
- `app/config.py` - Backend settings (GROQ_* vars)
- `scripts/openvox_daemon/config.py` - Daemon settings (OPENVOX_* vars)

### Database
- `data/openvox.db` - SQLite database file

## Naming Conventions

### Files
- Python modules: `lowercase_with_underscores.py` (e.g., `db.py`, `vad.py`)
- Daemon package modules: `lowercase_with_underscores.py`
- Shell scripts: `lowercase_with_underscores.sh`
- Frontend: `index.html`, `app.js`, `styles.css`

### Classes
- PascalCase: `PushToTalk`, `VoiceOverlay`, `SystemTrayIcon`, `GroqService`, `DesktopApp`

### Variables and Functions
- snake_case: `fetch_profile`, `list_entries`, `copy_to_clipboard`, `token_from_key`

### Constants/Config
- UPPER_SNAKE_CASE for env-backed constants: `GROQ_API_KEY`, `OPENVOX_HOTKEY`

## Where to Add New Code

### New API Endpoint
- **Primary code:** Add route function to `app/main.py`
- **Request/Response models:** Add Pydantic model to `app/models.py`
- **Database access (if needed):** Add function to `app/db.py`

### New Groq Feature
- **Implementation:** Add method to `app/groq_client.py`
- **Prompt logic:** Add function to `app/prompts.py`

### New Hotkey Daemon Feature
- **Implementation:** Add to `scripts/openvox_daemon/` as new module
- **Config:** Add env var loading in `scripts/openvox_daemon/config.py`

### New Frontend Feature
- **UI:** Add to `web/index.html`
- **Logic:** Add to `web/app.js`
- **Styling:** Add to `web/styles.css`

## Special Directories

### `.venv/`
- **Purpose:** Python virtual environment with installed packages
- **Generated:** Yes (by `scripts/bootstrap.sh`)
- **Committed:** No (.gitignore excludes it)

### `data/`
- **Purpose:** SQLite database storage
- **Generated:** Yes (created on first `init_db()` call)
- **Committed:** No (`.gitkeep` only, actual `.db` file gitignored)

### `scripts/openvox_daemon/__pycache__/`
- **Purpose:** Python bytecode cache
- **Generated:** Yes
- **Committed:** No

---

*Structure analysis: 2026-04-01*
