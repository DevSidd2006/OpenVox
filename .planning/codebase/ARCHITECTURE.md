# Architecture

**Analysis Date:** 2026-04-01

## Pattern Overview

**Overall:** Client-Server with Daemon Overlay

OpenVox follows a three-tier architecture:
- **FastAPI backend** (`app/`) serves the web UI and REST API
- **Web frontend** (`web/`) is a single-page application for configuration and history
- **Hotkey daemon** (`scripts/openvox_daemon/`) runs as a background service intercepting global keyboard shortcuts for push-to-talk recording

## Layers

### Backend API Layer
- **Purpose:** Serves REST endpoints for transcription, text rewriting, profile management, and history
- **Location:** `app/`
- **Contains:** FastAPI application, database access, Groq AI integration
- **Depends on:** SQLite, Groq SDK
- **Used by:** Web UI (browser), Hotkey daemon (HTTP POST)

### Database Layer
- **Purpose:** Persistent storage for user profile, app settings, and transcription history
- **Location:** `data/openvox.db`
- **Contains:** SQLite database with tables: `profile`, `entries`, `app_settings`
- **Depends on:** `app/db.py` for connection management
- **Used by:** Backend API exclusively

### Frontend/UI Layer
- **Purpose:** Browser-based dashboard for configuration, recording, and history browsing
- **Location:** `web/`
- **Contains:** `index.html`, `app.js`, `styles.css`
- **Depends on:** Backend REST API
- **Used by:** End user browser

### Hotkey Daemon Layer
- **Purpose:** Global hotkey listener (pynput) + push-to-talk recorder + overlay + system tray
- **Location:** `scripts/openvox_daemon/`
- **Contains:** `recorder.py`, `overlay.py`, `tray.py`, `clipboard.py`, `vad.py`, `audio_feedback.py`, `config.py`
- **Depends on:** ALSA (`arecord`), pynput, webrtcvad, pystray, tkinter (for overlay)
- **Used by:** System services or desktop app launcher

### Desktop Controller Layer
- **Purpose:** Tkinter GUI for starting/stopping local services and editing `.env` configuration
- **Location:** `desktop/app.py`
- **Contains:** DesktopApp class with service management UI
- **Depends on:** tkinter, subprocess
- **Used by:** End user for local development

## Data Flow

### Recording Flow (Push-to-Talk)

1. User presses hotkey (e.g., `ctrl+space`) via pynput global listener
2. `recorder.py` spawns `arecord` subprocess capturing raw S16_LE audio at 16kHz mono
3. Audio written to temporary WAV file via `_record_worker()` thread
4. RMS levels sent to `VoiceOverlay` for visual feedback
5. VAD (webrtcvad) monitors for silence; auto-stops after `OPENVOX_VAD_SILENCE_TIMEOUT` seconds
6. User releases hotkey → `stop_recording()` called
7. WAV file sent via multipart POST to `POST /api/transcribe`
8. Backend calls Groq Whisper for transcription, Groq LLM for rewrite
9. Result returned as JSON with `transcript` and `rewritten_text`
10. `recorder.py` copies text to clipboard (`wl-copy`/`xclip`) and types into active window (`wtype`/`xdotool`)

### Rewrite-Only Flow (Web UI)

1. User types or pastes text into web UI
2. `POST /api/rewrite` with `{text, style, context, language}`
3. Backend calls Groq LLM with system prompt built from user profile
4. Rewritten text returned and displayed

### Profile Update Flow

1. User fills profile form in web UI
2. `PUT /api/profile` with profile payload
3. `db.py` upserts into `profile` table
4. Hotkey daemon fetches profile on next recording via `GET /api/profile`

## Key Abstractions

### GroqService
- **Purpose:** Thin wrapper around Groq SDK for transcription and text rewriting
- **Examples:** `app/groq_client.py`
- **Pattern:** Singleton-like (instantiated per-request)

### PushToTalk
- **Purpose:** Manages recording lifecycle, VAD, API call, and text insertion
- **Examples:** `scripts/openvox_daemon/recorder.py`
- **Pattern:** State machine (idle → recording → processing → idle)

### VoiceOverlay
- **Purpose:** Tkinter-based floating overlay showing audio levels and state
- **Examples:** `scripts/openvox_daemon/overlay.py`
- **Pattern:** Owns tkinter mainloop in background thread

### SystemTrayIcon
- **Purpose:** pystray icon with menu for status, audio toggle, quit
- **Examples:** `scripts/openvox_daemon/tray.py`
- **Pattern:** Runs blocking event loop on main daemon thread

### DaemonConfig
- **Purpose:** Frozen dataclass loading all `OPENVOX_*` environment variables
- **Examples:** `scripts/openvox_daemon/config.py`
- **Pattern:** Immutable configuration object

## Entry Points

### API Server
- **Location:** `app/main.py`
- **Triggers:** `scripts/start_prod.sh` → `uvicorn app.main:app`
- **Responsibilities:** Serve REST API, CORS, static web files, database initialization

### Hotkey Daemon
- **Location:** `scripts/hotkey_push_to_talk.py`
- **Triggers:** `scripts/run_hotkey_daemon.sh` or desktop app
- **Responsibilities:** Global hotkey listener, push-to-talk recording, system tray

### Desktop Controller
- **Location:** `desktop/app.py`
- **Triggers:** `python desktop/app.py` or `.desktop` shortcut
- **Responsibilities:** GUI for service management and `.env` editing

### Bootstrap
- **Location:** `scripts/bootstrap.sh`
- **Triggers:** Manual or first-run setup
- **Responsibilities:** Create venv, install requirements

## Error Handling

**Strategy:** Graceful degradation and notification-driven feedback

**Patterns:**
- API returns HTTP 500 with detail message on failure
- Hotkey daemon uses `notify()` (system notifications) and `play()` (audio feedback) for user-facing errors
- Clipboard/t打字 fallback chain: `wl-copy` → `xclip` → `xsel` → `wl-copy` again
- Text insertion fallback: `wtype` → `xdotool type`
- VAD unavailable: silently disabled, rely on hotkey release to stop recording
- Missing pynput: exits with clear installation instructions

## Cross-Cutting Concerns

**Logging:** Print statements to stdout/stderr; `backend.log` and `hotkey.log` files in project root

**Validation:** Pydantic models for API request/response validation in `app/models.py`

**Authentication:** None (local-only, no auth implemented)

**CORS:** Wide open (`allow_origins=["*"]`) for local development

**Environment:** All configuration via `.env` file loaded by `dotenv` in both `app/config.py` and `scripts/openvox_daemon/config.py`

---

*Architecture analysis: 2026-04-01*
