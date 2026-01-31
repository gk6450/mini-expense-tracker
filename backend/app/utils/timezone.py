from datetime import datetime, timezone

try:
    # Python 3.9+
    from zoneinfo import ZoneInfo
    IST_ZONE = ZoneInfo("Asia/Kolkata")
except Exception:
    raise RuntimeError(
        "Time zone data not found. "
        "Install it using: pip install tzdata"
    )

def to_ist(dt: datetime) -> datetime:
    """
    Convert a datetime to IST (Asia/Kolkata).

    Rules:
    - If datetime is naive, we assume it is UTC.
    - Always returns a timezone-aware IST datetime.
    """
    if dt is None:
        return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(IST_ZONE)

def now_ist() -> datetime:
    """Return current time as timezone-aware IST datetime."""
    return datetime.now(IST_ZONE)
