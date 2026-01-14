from __future__ import annotations

from datetime import datetime, date, timezone, timedelta
from fastmcp import FastMCP

mcp = FastMCP("TimeServer")


@mcp.tool
def days_diff(t1: str, t2: str):
    """
    Calculate the day difference between two dates in "YYYY-MM-DD" format.

    Args:
        t1: Start date in "YYYY-MM-DD".
        t2: End date in "YYYY-MM-DD".

    Returns:
        A dict containing status and the day difference (t2 - t1) in days.
    """
    _t1 = datetime.strptime(t1, "%Y-%m-%d")
    _t2 = datetime.strptime(t2, "%Y-%m-%d")

    return {"status": "ok", "output": f"{(_t2 - _t1).days} days"}


@mcp.tool
def date_to_weekday(d: str, locale: str = "en", short: bool = False):
    """
    Convert a date string into a weekday name.

    Notes:
        - This function uses English weekday names only (locale parameter is reserved
          for future extension).
        - Input format: "YYYY-MM-DD".

    Args:
        d: Date string in "YYYY-MM-DD".
        locale: Reserved; currently only "en" is supported.
        short: If True, return abbreviated weekday (e.g., "Mon"); otherwise full name.

    Returns:
        A dict containing status and weekday name.
    """
    dt = datetime.strptime(d, "%Y-%m-%d").date()

    weekdays_full = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekdays_short = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    idx = dt.weekday()  # Monday=0 ... Sunday=6
    name = (weekdays_short if short else weekdays_full)[idx]

    return {"status": "ok", "output": name}


@mcp.tool
def iso_seconds_diff(t1: str, t2: str):
    """
    Calculate the seconds difference between two ISO-8601 datetime strings.

    Supported examples:
        - "2026-01-14T12:30:00"
        - "2026-01-14T12:30:00Z"
        - "2026-01-14T12:30:00+08:00"

    Interpretation:
        - If timezone info is present, it is respected.
        - If timezone info is absent, the datetime is treated as naive local time.

    Args:
        t1: ISO datetime string.
        t2: ISO datetime string.

    Returns:
        A dict containing status and the seconds difference (t2 - t1) in seconds.
    """
    def _parse_iso(s: str) -> datetime:
        # Accept trailing "Z" as UTC.
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        return datetime.fromisoformat(s)

    dt1 = _parse_iso(t1)
    dt2 = _parse_iso(t2)

    delta = dt2 - dt1
    return {"status": "ok", "output": int(delta.total_seconds())}


@mcp.tool
def convert_time_units(value: float, from_unit: str, to_unit: str):
    """
    Convert between common time units.

    Supported units:
        - "ms" (milliseconds)
        - "s"  (seconds)
        - "min" (minutes)
        - "h"  (hours)
        - "d"  (days)
        - "w"  (weeks)

    Args:
        value: Numeric value to convert.
        from_unit: Source unit.
        to_unit: Target unit.

    Returns:
        A dict containing status and the converted value.
    """
    unit_to_seconds = {
        "ms": 0.001,
        "s": 1.0,
        "min": 60.0,
        "h": 3600.0,
        "d": 86400.0,
        "w": 604800.0,
    }

    fu = from_unit.strip().lower()
    tu = to_unit.strip().lower()

    if fu not in unit_to_seconds:
        return {"status": "error", "output": f"Unsupported from_unit: {from_unit}"}
    if tu not in unit_to_seconds:
        return {"status": "error", "output": f"Unsupported to_unit: {to_unit}"}

    seconds = value * unit_to_seconds[fu]
    converted = seconds / unit_to_seconds[tu]

    return {"status": "ok", "output": converted}


@mcp.tool
def add_seconds_iso(t: str, seconds: int):
    """
    Add seconds to an ISO-8601 datetime string and return an ISO string.

    Notes:
        - If input ends with "Z", it is treated as UTC.
        - Output uses ISO format; if timezone-aware, includes offset.

    Args:
        t: ISO datetime string.
        seconds: Seconds to add (can be negative).

    Returns:
        A dict containing status and the resulting ISO datetime string.
    """
    if t.endswith("Z"):
        t = t[:-1] + "+00:00"
    dt = datetime.fromisoformat(t)
    dt2 = dt + timedelta(seconds=seconds)
    return {"status": "ok", "output": dt2.isoformat()}


if __name__ == "__main__":
    # 1) days_diff
    print("days_diff examples:")
    print(days_diff.fn("1989-06-04", "2026-01-14"))
    print(days_diff.fn("2026-01-01", "2026-01-14"))
    print(days_diff.fn("2026-01-14", "2026-01-01"))  # negative result
    print()

    # 2) date_to_weekday
    print("date_to_weekday examples:")
    print(date_to_weekday.fn("2026-01-14"))                 # full name
    print(date_to_weekday.fn("2026-01-14", short=True))     # abbreviated
    print(date_to_weekday.fn("1989-06-04"))
    print()

    # 3) iso_seconds_diff
    print("iso_seconds_diff examples:")
    print(iso_seconds_diff.fn("2026-01-14T00:00:00", "2026-01-14T00:00:10"))
    print(iso_seconds_diff.fn("2026-01-14T00:00:00Z", "2026-01-14T00:01:00Z"))
    print(iso_seconds_diff.fn("2026-01-14T00:00:00+08:00", "2026-01-14T00:00:30+08:00"))
    print(iso_seconds_diff.fn("2026-01-14T00:00:00+00:00", "2026-01-14T08:00:00+08:00"))  # same instant
    print()

    # 4) convert_time_units
    print("convert_time_units examples:")
    print(convert_time_units.fn(1500, "ms", "s"))
    print(convert_time_units.fn(2, "h", "min"))
    print(convert_time_units.fn(3, "d", "h"))
    print(convert_time_units.fn(1, "w", "d"))
    print(convert_time_units.fn(120, "s", "ms"))
    print()

    # 5) add_seconds_iso
    print("add_seconds_iso examples:")
    print(add_seconds_iso.fn("2026-01-14T00:00:00", 90))
    print(add_seconds_iso.fn("2026-01-14T00:00:00Z", 90))
    print(add_seconds_iso.fn("2026-01-14T23:59:30+00:00", 90))  # crosses day boundary
    print(add_seconds_iso.fn("2026-01-14T00:00:30+08:00", -60))  # subtract seconds

