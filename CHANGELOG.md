# Changelog

All notable changes are documented here. Format based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this project follows
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-10-04

### Added
- `log-purge` CLI: delete files older than N days by modification time.
- `--dry-run`, interactive confirmation, `--yes` for automation.
- `--pattern` glob filter, `--no-recursive`, `--verbose`.
- Safety guards: skips symlinks, never deletes directories, refuses filesystem
  roots, refuses to delete non-interactively without `--yes`.
