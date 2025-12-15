from fastmcp import FastMCP
from datetime import datetime
import time
from zoneinfo import ZoneInfo

mcp = FastMCP("TimeServer")

@mcp.tool
async def now():
    """Returns the current time (YYYY-MM-DD HH:MM:SS)"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@mcp.tool
async def today():
    """Returns today's date (YYYY-MM-DD)"""
    return datetime.now().date().isoformat()

@mcp.tool
async def unix_timestamp():
    """Returns the current Unix timestamp (seconds since epoch)"""
    return int(time.time())

@mcp.tool
async def from_timestamp(ts, fmt="%Y-%m-%d %H:%M:%S"):
    """Converts a Unix timestamp to a formatted datetime string.
    ts: number or numeric string
    """
    try:
        t = float(ts)
    except Exception:
        return "invalid timestamp"
    return datetime.fromtimestamp(t).strftime(fmt)

@mcp.tool
async def add_seconds(seconds, base_time=None, fmt="%Y-%m-%d %H:%M:%S"):
    """Adds seconds to a base time and returns formatted result.
    base_time: ISO string or numeric timestamp. If omitted, uses now().
    """
    try:
        sec = float(seconds)
    except Exception:
        return "invalid seconds"
    if base_time is None:
        base_ts = time.time()
    else:
        try:
            base_ts = float(base_time)
        except Exception:
            try:
                base_dt = datetime.fromisoformat(str(base_time))
                base_ts = base_dt.timestamp()
            except Exception:
                return "invalid base_time"
    return datetime.fromtimestamp(base_ts + sec).strftime(fmt)

@mcp.tool
async def time_until(target):
    """Returns time until target as 'in Xd Xh Xm Xs' or 'X ago'.
    target: ISO string or numeric timestamp
    """
    try:
        target_ts = float(target)
    except Exception:
        try:
            target_dt = datetime.fromisoformat(str(target))
            target_ts = target_dt.timestamp()
        except Exception:
            return "invalid target"
    delta = int(target_ts - time.time())
    if delta == 0:
        return "now"
    past = delta < 0
    if past:
        delta = -delta
    days, rem = divmod(delta, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds or not parts:
        parts.append(f"{seconds}s")
    human = " ".join(parts)
    return f"{human} ago" if past else f"in {human}"

@mcp.tool
async def timezone_convert(dt, target_zone):
    """Converts an ISO datetime to target IANA timezone (e.g. 'Europe/Berlin')."""
    if ZoneInfo is None:
        return "zoneinfo not available in this Python build"
    try:
        src_dt = None
        try:
            src_dt = datetime.fromisoformat(str(dt))
        except Exception:
            # try numeric timestamp
            src_dt = datetime.fromtimestamp(float(dt))
        if src_dt.tzinfo is None:
            src_dt = src_dt.astimezone()  # assume local
        converted = src_dt.astimezone(ZoneInfo(str(target_zone)))
        return converted.isoformat()
    except Exception as e:
        return f"conversion error: {e}"

@mcp.tool
async def weekday(date_str):
    """Returns the weekday name for the given date (ISO date or datetime)."""
    try:
        d = datetime.fromisoformat(str(date_str))
    except Exception:
        try:
            # accept plain YYYY-MM-DD by appending time
            d = datetime.fromisoformat(str(date_str) + "T00:00:00")
        except Exception:
            return "invalid date"
    return d.strftime("%A")


async def test():
    from pprint import pprint

    resp = await now.fn()
    pprint(resp)

    resp = await today.fn()
    pprint(resp)

    resp = await unix_timestamp.fn()
    pprint(resp)

    resp = await from_timestamp.fn(resp)
    pprint(resp)

    resp = await add_seconds.fn(600, "2025-12-15 14:30:00")
    pprint(resp)

    resp = await time_until.fn("2077-07-01 14:30:00")
    pprint(resp)

    resp = await timezone_convert.fn("2025-12-15T14:30:00", "UTC")
    pprint(resp)

    resp = await weekday.fn("2077-07-01")
    pprint(resp)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test())