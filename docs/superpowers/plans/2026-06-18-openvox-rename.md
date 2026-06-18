# OpenVox Rename Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename all references from Lynx/Willow to OpenVox across source code, files, env vars, and docs.

**Architecture:** Single-pass automated rename using bulk string replacement and file renames, followed by verification. No logic changes — purely cosmetic/naming.

**Tech Stack:** sed, rg (ripgrep), mv, Python import verification

---

### Task 1: Rename source code strings (Python + HTML/JS/CSS)

**Files:** All .py, .html, .js, .css files in app/, desktop/, scripts/, web/

- [ ] **Step 1: Bulk-replace strings in source files**

```bash
# Replace display names
sed -i 's/\bLynx\b/OpenVox/g' app/__init__.py app/main.py app/prompts.py
sed -i 's/\bLynx\b/OpenVox/g' desktop/app.py
sed -i 's/\bLynx\b/OpenVox/g' scripts/hotkey_push_to_talk.py
sed -i 's/\bLynx\b/OpenVox/g' scripts/lynx_daemon/__init__.py
sed -i 's/\bLynx\b/OpenVox/g' scripts/lynx_daemon/tray.py
sed -i 's/\bLynx\b/OpenVox/g' scripts/lynx_daemon/recorder.py
sed -i 's/\bLynx\b/OpenVox/g' scripts/lynx_daemon/notifier.py

# Replace internal snake_case references
sed -i 's/\blynx\b/openvox/g' app/main.py app/config.py app/__init__.py
sed -i 's/\blynx\b/openvox/g' scripts/hotkey_push_to_talk.py
sed -i 's/\blynx\b/openvox/g' scripts/lynx_daemon/__init__.py
sed -i 's/\blynx\b/openvox/g' scripts/lynx_daemon/tray.py
sed -i 's/\blynx\b/openvox/g' scripts/lynx_daemon/recorder.py
sed -i 's/\blynx\b/openvox/g' scripts/lynx_daemon/notifier.py

# Replace environment variable prefixes
sed -i 's/WILLOW_CLONE_URL/OPENVOX_API_URL/g' desktop/app.py scripts/lynx_daemon/config.py
sed -i 's/WILLOW_HOTKEY/OPENVOX_HOTKEY/g' desktop/app.py scripts/lynx_daemon/config.py
sed -i 's/WILLOW_STYLE/OPENVOX_STYLE/g' desktop/app.py scripts/lynx_daemon/config.py
sed -i 's/WILLOW_CONTEXT/OPENVOX_CONTEXT/g' desktop/app.py scripts/lynx_daemon/config.py
sed -i 's/WILLOW_LANGUAGE/OPENVOX_LANGUAGE/g' desktop/app.py scripts/lynx_daemon/config.py
sed -i 's/WILLOW_AUTO_PASTE/OPENVOX_AUTO_PASTE/g' desktop/app.py scripts/lynx_daemon/config.py
sed -i 's/WILLOW_INSERT_MODE/OPENVOX_INSERT_MODE/g' desktop/app.py scripts/lynx_daemon/config.py
sed -i 's/WILLOW_OVERLAY/OPENVOX_OVERLAY/g' desktop/app.py scripts/lynx_daemon/config.py
sed -i 's/WILLOW_AUDIO_FEEDBACK/OPENVOX_AUDIO_FEEDBACK/g' desktop/app.py scripts/lynx_daemon/config.py
sed -i 's/WILLOW_OVERLAY_POSITION/OPENVOX_OVERLAY_POSITION/g' desktop/app.py scripts/lynx_daemon/config.py
sed -i 's/WILLOW_VAD_ENABLED/OPENVOX_VAD_ENABLED/g' desktop/app.py scripts/lynx_daemon/config.py
sed -i 's/WILLOW_VAD_SILENCE_TIMEOUT/OPENVOX_VAD_SILENCE_TIMEOUT/g' desktop/app.py scripts/lynx_daemon/config.py
sed -i 's/WILLOW_VAD_AGGRESSIVENESS/OPENVOX_VAD_AGGRESSIVENESS/g' desktop/app.py scripts/lynx_daemon/config.py

# Replace systemd service names in desktop app
sed -i 's/willow-groq-clone-api/openvox-api/g' desktop/app.py
sed -i 's/willow-groq-clone-hotkey/openvox-hotkey/g' desktop/app.py

# Replace frontend (HTML/JS/CSS)
sed -i 's/\bLynx\b/OpenVox/g' web/index.html
```

- [ ] **Step 2: Rename import paths in hotkey entry point**

```bash
sed -i 's/from lynx_daemon/from openvox_daemon/g' scripts/hotkey_push_to_talk.py
```

- [ ] **Step 3: Verify no Python syntax errors**

```bash
python -c "import ast; ast.parse(open('app/main.py').read())"
python -c "import ast; ast.parse(open('desktop/app.py').read())"
python -c "import ast; ast.parse(open('scripts/hotkey_push_to_talk.py').read())"
```

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "rename: update source code strings from Lynx/Willow to OpenVox"
```

---

### Task 2: Rename environment variables

**Files:** `.env`, `.env.example`

- [ ] **Step 1: Replace all WILLOW_* vars in .env**

```bash
sed -i 's/WILLOW_CLONE_URL/OPENVOX_API_URL/g' .env .env.example
sed -i 's/WILLOW_HOTKEY/OPENVOX_HOTKEY/g' .env .env.example
sed -i 's/WILLOW_STYLE/OPENVOX_STYLE/g' .env .env.example
sed -i 's/WILLOW_CONTEXT/OPENVOX_CONTEXT/g' .env .env.example
sed -i 's/WILLOW_LANGUAGE/OPENVOX_LANGUAGE/g' .env .env.example
sed -i 's/WILLOW_AUTO_PASTE/OPENVOX_AUTO_PASTE/g' .env .env.example
sed -i 's/WILLOW_INSERT_MODE/OPENVOX_INSERT_MODE/g' .env .env.example
sed -i 's/WILLOW_OVERLAY/OPENVOX_OVERLAY/g' .env .env.example
sed -i 's/WILLOW_AUDIO_FEEDBACK/OPENVOX_AUDIO_FEEDBACK/g' .env .env.example
sed -i 's/WILLOW_OVERLAY_POSITION/OPENVOX_OVERLAY_POSITION/g' .env .env.example
sed -i 's/WILLOW_VAD_ENABLED/OPENVOX_VAD_ENABLED/g' .env .env.example
sed -i 's/WILLOW_VAD_SILENCE_TIMEOUT/OPENVOX_VAD_SILENCE_TIMEOUT/g' .env .env.example
sed -i 's/WILLOW_VAD_AGGRESSIVENESS/OPENVOX_VAD_AGGRESSIVENESS/g' .env .env.example
```

- [ ] **Step 2: Verify .env matches .env.example structure**

```bash
diff <(grep -v '^$' .env | grep -v '^#' | sort) <(grep -v '^$' .env.example | grep -v '^#' | sort)
```

- [ ] **Step 3: Commit**

```bash
git add .env .env.example && git commit -m "rename: update env vars from WILLOW_* to OPENVOX_*"
```

---

### Task 3: Rename files and directories

**Files/Dirs:**
- `scripts/lynx_daemon/` → `scripts/openvox_daemon/`
- `scripts/lynx_toggle.sh` → `scripts/openvox_toggle.sh`

- [ ] **Step 1: Rename directory**

```bash
mv scripts/lynx_daemon scripts/openvox_daemon
```

- [ ] **Step 2: Rename toggle script**

```bash
mv scripts/lynx_toggle.sh scripts/openvox_toggle.sh
```

- [ ] **Step 3: Update all references to renamed paths in scripts**

```bash
sed -i 's|lynx_daemon|openvox_daemon|g' scripts/hotkey_push_to_talk.py
sed -i 's|lynx_daemon|openvox_daemon|g' scripts/start_all.sh
sed -i 's|lynx_toggle.sh|openvox_toggle.sh|g' scripts/bootstrap.sh
sed -i 's|lynx_toggle.sh|openvox_toggle.sh|g' scripts/install_desktop_shortcut.sh
sed -i 's|lynx\.desktop|openvox\.desktop|g' scripts/install_desktop_shortcut.sh
```

- [ ] **Step 4: Verify imports resolve**

```bash
python -c "import ast; ast.parse(open('scripts/hotkey_push_to_talk.py').read())"
```

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "rename: rename files/directories from lynx to openvox"
```

---

### Task 4: Update shell scripts

**Files:** All 10 remaining .sh files in scripts/

- [ ] **Step 1: Bulk-replace strings in shell scripts**

```bash
sed -i 's/\bLynx\b/OpenVox/g' scripts/*.sh scripts/run_hotkey_daemon.sh
sed -i 's/\blynx\b/openvox/g' scripts/*.sh
sed -i 's/willow-groq-clone-api/openvox-api/g' scripts/install_user_service.sh
sed -i 's/willow-groq-clone-hotkey/openvox-hotkey/g' scripts/install_user_service.sh
sed -i 's/WILLOW_CLONE_URL/OPENVOX_API_URL/g' scripts/ubuntu_hotkey_dictate.sh
sed -i 's|lynx_daemon|openvox_daemon|g' scripts/run_hotkey_daemon.sh
```

- [ ] **Step 2: Commit**

```bash
git add scripts/ && git commit -m "rename: update shell scripts from lynx/willow to openvox"
```

---

### Task 5: Update documentation

**Files:** README.md, CONTRIBUTING.md, ROADMAP.md, .planning/codebase/*.md, docs/research.md

- [ ] **Step 1: Bulk-replace in docs**

```bash
# Display names
sed -i 's/\bLynx\b/OpenVox/g' README.md CONTRIBUTING.md ROADMAP.md docs/research.md
# Internal names
sed -i 's/\blynx\b/openvox/g' README.md ROADMAP.md docs/research.md
# Env vars
sed -i 's/WILLOW_CLONE_URL/OPENVOX_API_URL/g' README.md
sed -i 's/WILLOW_HOTKEY/OPENVOX_HOTKEY/g' README.md
sed -i 's/WILLOW_STYLE/OPENVOX_STYLE/g' README.md
sed -i 's/WILLOW_CONTEXT/OPENVOX_CONTEXT/g' README.md
sed -i 's/WILLOW_LANGUAGE/OPENVOX_LANGUAGE/g' README.md
sed -i 's/WILLOW_AUTO_PASTE/OPENVOX_AUTO_PASTE/g' README.md
sed -i 's/WILLOW_INSERT_MODE/OPENVOX_INSERT_MODE/g' README.md
sed -i 's/WILLOW_OVERLAY/OPENVOX_OVERLAY/g' README.md
sed -i 's/WILLOW_VAD_ENABLED/OPENVOX_VAD_ENABLED/g' README.md
sed -i 's/WILLOW_VAD_SILENCE_TIMEOUT/OPENVOX_VAD_SILENCE_TIMEOUT/g' README.md
# Git URL
sed -i 's|devsidd/willow-groq-clone|devsidd/openvox|g' README.md CONTRIBUTING.md
# Systemd service names
sed -i 's/willow-groq-clone-api/openvox-api/g' README.md install_user_service.sh
sed -i 's/willow-groq-clone-hotkey/openvox-hotkey/g' README.md install_user_service.sh
# File paths
sed -i 's|lynx_daemon|openvox_daemon|g' README.md CONTRIBUTING.md
sed -i 's|lynx_toggle.sh|openvox_toggle.sh|g' README.md
# Data/db path
sed -i 's|lynx\.db|openvox\.db|g' README.md
```

- [ ] **Step 2: Update .planning/ files**

```bash
sed -i 's/\bLynx\b/OpenVox/g' .planning/codebase/*.md
sed -i 's/\blynx\b/openvox/g' .planning/codebase/*.md
sed -i 's/WILLOW_/OPENVOX_/g' .planning/codebase/*.md
sed -i 's/willow-groq-clone/openvox/g' .planning/codebase/*.md
sed -i 's|lynx_daemon|openvox_daemon|g' .planning/codebase/*.md
sed -i 's|lynx\.db|openvox\.db|g' .planning/codebase/*.md
```

- [ ] **Step 3: Commit**

```bash
git add README.md CONTRIBUTING.md ROADMAP.md docs/ .planning/ && git commit -m "rename: update documentation from lynx/willow to openvox"
```

---

### Task 6: Final verification

- [ ] **Step 1: Check for any remaining old name references**

```bash
rg -i 'lynx|willow' --type py --type html --type js --type css --type sh --type md --glob '!.git/' --glob '!.venv/' --glob '!.planning/' --glob '!__pycache__/' --glob '!*.pyc'
```

Expected: only matches in `.planning/` (which were already updated) or zero matches.

- [ ] **Step 2: Quick sanity — verify key imports work**

```bash
python -c "from app.main import app; print('Backend OK')"
python -c "import sys; sys.path.insert(0, 'scripts'); from openvox_daemon.config import DaemonConfig; print('Daemon config OK')"
```

- [ ] **Step 3: If verification clean, final commit**

```bash
git add -A && git commit -m "rename: final cleanup of remaining references"
```
