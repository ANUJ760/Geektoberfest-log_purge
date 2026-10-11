"""Small helpers shared by the core logic and the CLI."""

from __future__ import annotations

import re

SECONDS_PER_DAY = 86_400

DURATION_FACTORS: dict[str, float] = {
    "": 1.0,
    "d": 1.0,
    "day": 1.0,
    "days": 1.0,
    "w": 7.0,
    "week": 7.0,
    "weeks": 7.0,
    "h": 1.0 / 24.0,
    "hr": 1.0 / 24.0,
    "hour": 1.0 / 24.0,
    "hours": 1.0 / 24.0,
    "m": 1.0 / 1440.0,
    "min": 1.0 / 1440.0,
    "minute": 1.0 / 1440.0,
    "minutes": 1.0 / 1440.0,
    "s": 1.0 / 86400.0,
    "sec": 1.0 / 86400.0,
    "second": 1.0 / 86400.0,
    "seconds": 1.0 / 86400.0,
}


def parse_duration(duration_str: str | float | int) -> float:
    """Parse a duration string into days as a float.

    Accepts units like d, w, h, m, s (e.g. ``'30d'``, ``'2w'``, ``'12h'``)
    or bare numbers which default to days.
    """
    if isinstance(duration_str, (int, float)):
        val = float(duration_str)
        if val < 0:
            raise ValueError("Duration cannot be negative")
        return val

    if not isinstance(duration_str, str):
        raise ValueError(f"Duration must be a string or number, got {type(duration_str).__name__}")

    s = duration_str.strip()
    if not s:
        raise ValueError("Empty duration string")

    match = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z]*)", s)
    if not match:
        raise ValueError(f"Invalid duration string: '{duration_str}'")

    number_part, unit_part = match.groups()
    try:
        num = float(number_part)
    except ValueError:
        raise ValueError(f"Invalid duration number: '{number_part}'") from None

    unit = unit_part.lower()
    if unit not in DURATION_FACTORS:
        raise ValueError(f"Unknown duration unit: '{unit_part}'")

    days = num * DURATION_FACTORS[unit]
    if days < 0:
        raise ValueError("Duration cannot be negative")
    return days



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
