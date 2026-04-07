# Coding Conventions

**Analysis Date:** 2026-04-01

## Naming Patterns

**Files:**
- Python modules: `snake_case.py`
- Daemon sub-package: `snake_case.py`
- Shell scripts: `snake_case.sh`
- Frontend: `index.html`, `app.js`, `styles.css`

**Functions:**
- `snake_case` for all functions and methods
- Examples: `fetch_profile()`, `list_entries()`, `copy_to_clipboard()`, `token_from_key()`

**Variables:**
- `snake_case` for local variables and instance variables
- Examples: `source_text`, `rewritten_text`, `current_wav`, `hotkey_proc`

**Types (Pydantic):**
- `PascalCase` model names: `ProfileModel`, `RewriteRequest`, `RewriteResponse`

**Constants/Env vars:**
- `UPPER_SNAKE_CASE` for environment-backed constants: `GROQ_API_KEY`, `WILLOW_HOTKEY`
- Private module-level constants: `_ALIASES`, `_ICON_COLORS`

## Code Style

**Formatting:**
- No automated formatter detected (no ruff, black, or autopep8 config)
- Manual formatting consistent across files

**Linting:**
- No linting configuration detected

**Type Annotations:**
- Python 3.12 with `from __future__ import annotations` (postponed evaluation)
- Heavy use of type hints: `def func() -> None:`, `list[dict[str, Any]]`
- `@dataclass(frozen=True)` for configuration objects

**Imports:**
- `from __future__ import annotations` in all Python files
- Relative imports within package: `from .db import ...`, `from .config import settings`
- Stdlib first, then third-party, then local

## Import Organization

**Order:**
1. Stdlib: `os`, `sys`, `pathlib`, `subprocess`, `threading`, `json`, `sqlite3`, `urllib`
2. Third-party: `fastapi`, `groq`, `pydantic`, `dotenv`, `pynput`, `webrtcvad`, `pystray`
3. Local package imports: `from .module import ...`

**Path Aliases:** None used

## Error Handling

**Patterns:**
- API routes: `HTTPException(status_code=500, detail=f"Transcription failed: {exc}")`
- Daemon: `notify()` + `play("error")` for user-facing errors
- Database: Context managers with exception propagation
- Subprocess: `check=False` with return code checks

## Logging

**Framework:** Print statements to stdout/stderr
- `print(f"[Lynx] message", flush=True)` in daemon
- `traceback.print_exc()` for exception details
- Log files: `backend.log` and `hotkey.log` in project root (external process capture)

## Comments

**When to Comment:**
- Module-level docstrings explaining purpose
- Class docstrings for public API
- Inline comments for non-obvious logic (VAD frame processing, multipart form building, clipboard fallback chain)

**TSDoc/JSDoc:** Not used (vanilla JS)

## Function Design

**Size:** Moderate - typically 20-80 lines; complex functions like `process_audio()` are longer

**Parameters:**
- Explicit type annotations
- Default values where appropriate
- Configuration accessed via `cfg` or `settings` module-level singletons

**Return Values:**
- Explicit type annotations
- Pydantic models for API responses
- `dict[str, Any]` for database rows

## Module Design

**Exports:** No explicit `__all__` defined

**Barrel Files:** `app/__init__.py` and `scripts/lynx_daemon/__init__.py` are empty

**Package Structure:**
- `app/` - FastAPI package with `main.py` as entry
- `scripts/lynx_daemon/` - Sub-package imported by `hotkey_push_to_talk.py`

---

*Convention analysis: 2026-04-01*
