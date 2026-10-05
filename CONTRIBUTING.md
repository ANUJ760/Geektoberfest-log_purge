# Contributing to log-purge

Thanks for helping out! This project is small on purpose: a dependency-free
CLI that deletes old files safely. Bug fixes, tests, docs and focused
features are all welcome.

## Getting started

```bash
git clone https://github.com/YOUR_USERNAME/log-purge.git
cd log-purge
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check .
```

## Ground rules

- **Safety first.** This tool deletes files. Any change that widens what can
  be deleted (following symlinks, removing directories, etc.) needs a clear
  justification and tests.
- **No runtime dependencies.** The standard library only. Dev tools are fine.
- **Keep logic out of `cli.py`.** Put behavior in `purger.py` so it can be
  tested without capturing output.
- **Add tests** for every bug fix and feature (`tests/`, use `tmp_path`).
- Keep Python 3.9+ compatibility.

## Pull requests

1. Open an issue first for anything bigger than a small fix.
2. Create a branch: `git checkout -b fix/short-description`.
3. Make sure `pytest` and `ruff check .` pass.
4. Add a line under **Unreleased** in `CHANGELOG.md`.
5. Open the PR and fill in the template.

## Commit messages

Short imperative summary, e.g. `Skip unreadable directories`. Add detail in
the body if the "why" isn't obvious.

## Reporting security issues

Please do not open a public issue. See [SECURITY.md](SECURITY.md).
