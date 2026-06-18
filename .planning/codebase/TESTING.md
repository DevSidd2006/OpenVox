# Coding Conventions

**Analysis Date:** 2026-04-01

## Naming Patterns

### Files
- Python modules: `snake_case.py`
- Daemon sub-package: `snake_case.py`
- Shell scripts: `snake_case.sh`
- Frontend: `index.html`, `app.js`, `styles.css`

### Functions
- `snake_case` for all functions and methods
- Examples: `fetch_profile()`, `list_entries()`, `copy_to_clipboard()`, `token_from_key()`

### Classes
- `PascalCase` for all classes
- Examples: `PushToTalk`, `VoiceOverlay`, `SystemTrayIcon`, `GroqService`, `DesktopApp`

### Variables
- `snake_case` for local variables and instance variables
- Examples: `source_text`, `rewritten_text`, `current_wav`, `hotkey_proc`

### Types (Pydantic)
- `PascalCase` model names: `ProfileModel`, `RewriteRequest`, `RewriteResponse`

### Constants/Envs
- `UPPER_SNAKE_CASE` for environment-backed constants: `GROQ_API_KEY`, `OPENVOX_HOTKEY`
- Internal module-level constants: `_ALIASES` dict, `_ICON_COLORS` dict

## Code Style

**Formatting:** No automated formatter detected (no ruff, black, or autopep8 config found)

**Linting:** No linting configuration detected

**Type Annotations:**
- Python 3.12 with `from __future__ import annotations` (postponed evaluation)
- Heavy use of type hints: `def func() -> None:`, `list[dict[str, Any]]`
- `@dataclass(frozen=True)` for configuration objects

**Imports:**
- `from __future__ import annotations` in all Python files
- Relative imports within package: `from .db import ...`, `from .config import settings`
- Absolute imports for cross-package: `from pathlib import Path`

## Import Organization

1. Stdlib: `os`, `sys`, `pathlib`, `subprocess`, `threading`, `json`, `sqlite3`
2. Third-party: `fastapi`, `groq`, `pydantic`, `dotenv`, `pynput`, `webrtcvad`, `pystray`
3. Local package imports: `from .module import ...`

## Error Handling

**API Layer:**
- HTTPException with status_code and detail: `raise HTTPException(status_code=500, detail=f"Transcription failed: {exc}")`
- Generic try/except with traceback printing for debugging

**Daemon Layer:**
- Graceful degradation (e.g., VAD unavailable → disable silently)
- `notify()` for user-facing error notifications
- `play("error")` for audio feedback on failure
- System exit with clear messages for missing dependencies

**Database:**
- Context managers for connection lifecycle
- Exception propagation for missing records (e.g., `raise RuntimeError("Profile record missing")`)

## Logging

**Framework:** Print statements to stdout/stderr
- `print(f"[OpenVox] message", flush=True)` for daemon messages
- `traceback.print_exc()` for exception details
- Log files: `backend.log` and `hotkey.log` in project root (written by external process)

## Comments

**When to Comment:**
- Module-level docstrings explaining purpose
- Class docstrings for public API
- Inline comments for non-obvious logic (e.g., VAD frame processing, multipart form building)

**TSDoc/JSDoc:** Not used (vanilla JS, no TypeScript)

## Function Design

**Size:** Moderate - functions typically 20-80 lines; complex functions like `process_audio()` are longer

**Parameters:**
- Explicit type annotations
- Default values where appropriate
- Configuration always accessed via `cfg` or `settings` singletons

**Return Values:**
- Explicit type annotations
- Pydantic models for API responses
- `dict[str, Any]` for database rows

## Module Design

**Exports:** No explicit `__all__` defined

**Barrel Files:** `app/__init__.py` is empty; `scripts/openvox_daemon/__init__.py` is empty

**Package Structure:**
- `app/` - FastAPI package with `main.py` as the app entry
- `scripts/openvox_daemon/` - Sub-package with `__init__.py` marker

---

*Convention analysis: 2026-04-01*
