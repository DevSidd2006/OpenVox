# Codebase Concerns

**Analysis Date:** 2026-04-01

## Tech Debt

**Dual config loading with different variable names:**
- `app/config.py` reads `GROQ_*` env vars
- `scripts/lynx_daemon/config.py` reads `WILLOW_*` env vars
- Files: `app/config.py`, `scripts/lynx_daemon/config.py`
- Impact: Confusing naming, easy to misconfigure
- Fix approach: Unify env var naming under one prefix

**No auth on API:**
- API has no authentication (CORS wide open)
- Files: `app/main.py`
- Impact: Any local process or browser can access/modify profile, settings, and call transcription
- Fix approach: Add API key auth or limit to localhost

**Static files served with CORs wide open:**
- `allow_origins=["*"]` in FastAPI CORS middleware
- File: `app/main.py`
- Impact: API accessible from any origin
- Fix approach: Restrict to localhost in production

**GroqService instantiated per-request:**
- `GroqService()` created in each route handler
- File: `app/main.py`
- Impact: Connection overhead, no connection pooling
- Fix approach: Use module-level singleton or dependency injection

**Hardcoded systemd service names:**
- Service names hardcoded as `willow-groq-clone-api.service` and `willow-groq-clone-hotkey.service`
- Files: `desktop/app.py`, `scripts/install_user_service.sh`
- Impact: Inconsistent with project name "Lynx", confusing
- Fix approach: Rename to `lynx-api.service` and `lynx-hotkey.service`

## Known Bugs

**Overlay geometry computed before window is ready:**
- `root.winfo_screenwidth()` called immediately in `_run()` before `update_idletasks()`
- File: `scripts/lynx_daemon/overlay.py`
- Trigger: Overlay starts with potentially incorrect screen dimensions
- Workaround: `root.update_idletasks()` before geometry call

**Daemon config is frozen but runtime toggles mutate it:**
- `cfg.audio_feedback` toggled via `object.__setattr__(cfg, "audio_feedback", ...)` despite `@dataclass(frozen=True)`
- File: `scripts/lynx_daemon/tray.py`
- Impact: Breaks the frozen contract, could cause unexpected behavior
- Fix approach: Use a mutable inner container or recreate config object

**VAD auto-stop scheduling race:**
- `_auto_stop_timer = threading.Timer(0, self.stop_recording)` scheduled from within `_record_worker`
- File: `scripts/lynx_daemon/recorder.py`
- Impact: Timer fires after `process_audio` may have already started, unclear ordering
- Workaround: None observed

## Security Considerations

**GROQ_API_KEY in plaintext .env file:**
- API key stored in `.env` which is likely in git
- Files: `.env`, `.gitignore`
- Current mitigation: `.env` is gitignored
- Recommendations: Use a secrets manager or environment-specific injection

**No input sanitization on text rewrite:**
- User-provided text passed directly to LLM prompts
- Files: `app/prompts.py`, `app/groq_client.py`
- Current mitigation: None (relies on LLM to not echo harmful content)
- Recommendations: Content length limits, prompt injection defenses

## Performance Bottlenecks

**WAV file written to disk then read back:**
- `tempfile.mkstemp()` creates temp WAV, written by `_record_worker`, read in `process_audio`, then deleted
- Files: `scripts/lynx_daemon/recorder.py`
- Cause: Wave module requires seekable file; simplest approach given constraints
- Improvement path: Use io.BytesIO in memory buffer

**Blocking HTTP request in recorder:**
- `urllib.request.urlopen(request, timeout=60)` blocks during transcription
- File: `scripts/lynx_daemon/recorder.py`
- Impact: Recording thread exits but `process_audio` is synchronous on the caller's thread
- Fix approach: Run `process_audio` in a thread pool

## Fragile Areas

**System tray without AppIndicator library:**
- pystray used without ayatana-appindicator on GNOME Wayland
- File: `scripts/lynx_daemon/tray.py`
- Why fragile: Tray icon silently fails to appear on many Wayland setups
- Safe modification: Keep fallback tray-less mode
- Test coverage: Manual only

**Wayland hotkey detection relies on XWayland:**
- Global hotkeys on Wayland require XWayland or special setup
- File: `scripts/lynx_daemon/tray.py` (`_warn_wayland_hotkey`)
- Why fragile: Hotkeys silently fail on pure Wayland without XWayland
- Safe modification: Check `WAYLAND_DISPLAY` and `XDG_SESSION_TYPE`
- Test coverage: Environment-dependent manual testing

## Scaling Limits

**SQLite as single-file database:**
- No connection pooling, single writer at a time
- Limit: Not designed for concurrent multi-process access
- Scaling path: Migrate to PostgreSQL if multi-user or high-concurrency needed

**Groq API rate limits:**
- No request throttling or retry logic
- Limit: Dependent on Groq quota
- Scaling path: Add rate limiting and exponential backoff

## Dependencies at Risk

**pystray compatibility with Python 3.12+ on Wayland:**
- pystray may have issues with newer Python/tkinter combinations
- File: `requirements-hotkey.txt`
- Impact: System tray fails to load
- Migration plan: Investigate `appindicator` library as alternative

**webrtcvad binary compatibility:**
- webrtcvad is a C extension that may have compatibility issues
- File: `requirements-hotkey.txt`
- Impact: VAD silently disabled if import fails
- Migration plan: Fallback to simpler energy-based VAD

## Missing Critical Features

**No test suite:**
- Zero test files detected
- Blocks: Safe refactoring, CI/CD integration
- Priority: High

**No database migrations:**
- Schema changes require manual ALTER TABLE in `init_db()`
- File: `app/db.py`
- Blocks: Clean deployment upgrades
- Priority: Medium

**No logging framework:**
- Print statements used throughout
- Blocks: Log aggregation, log levels, structured logging
- Priority: Medium

## Test Coverage Gaps

**API routes:**
- All routes lack unit/integration tests
- Files: `app/main.py`
- Risk: Regression in transcription, rewrite, profile endpoints
- Priority: High

**Database functions:**
- No tests for `db.py` functions
- Files: `app/db.py`
- Risk: Data corruption, incorrect queries
- Priority: High

**Hotkey daemon:**
- No tests for recorder, overlay, tray, clipboard
- Files: `scripts/lynx_daemon/recorder.py`, `scripts/lynx_daemon/overlay.py`, etc.
- Risk: Silent failures on different systems
- Priority: Medium

---

*Concerns audit: 2026-04-01*
