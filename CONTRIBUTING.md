# Contributing to OpenVox

Welcome! OpenVox is a community-driven project. Contributions are welcome.

## How to Contribute

### Reporting Bugs

1. Check existing issues first
2. Open a new issue with:
   - Clear title
   - Steps to reproduce
   - Environment (OS, Python version)
   - Relevant logs (`backend.log`, `hotkey.log`)

### Suggesting Features

1. Search the roadmap to avoid duplicates
2. Open a discussion first for major changes
3. Explain the use case and proposed solution

### Pull Requests

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Follow the code style below
4. Test your changes
5. Commit with clear messages
6. Push and open a PR

## Code Style

- **Python**: Follow PEP 8, use Black formatter
- **JavaScript**: ES6+, no semicolons
- **Shell**: Bash with `set -euo pipefail`

Run formatting before submitting:
```bash
# Python
black app/ scripts/openvox_daemon/

# Shell
shellcheck scripts/*.sh
```

## Good First Issues

Looking for a way to contribute? Try these:

- [ ] Improve error messages in the daemon
- [ ] Add more VAD aggressiveness levels
- [ ] Write tests for db.py
- [ ] Improve documentation
- [ ] Add keyboard shortcut customization UI

## Development Setup

```bash
git clone https://github.com/devsidd/openvox.git
cd willow-groq-clone

# Create venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-hotkey.txt

# Run locally
bash scripts/start.sh
```

## Commit Messages

- Use present tense: "Add feature" not "Added feature"
- Keep first line under 72 characters
- Reference issues: "Fix #123"

## License

By contributing, you agree your work will be licensed under MIT.