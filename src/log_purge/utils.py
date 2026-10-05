"""Small helpers shared by the core logic and the CLI."""

from __future__ import annotations

SECONDS_PER_DAY = 86_400


def format_size(num_bytes: int) -> str:
    """Return a human-readable size, e.g. ``1536`` -> ``'1.5 KB'``."""
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{int(size)} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"  # pragma: no cover


def age_in_days(mtime: float, now: float) -> float:
    """Age of a file in days, given its modification time."""
    return (now - mtime) / SECONDS_PER_DAY
