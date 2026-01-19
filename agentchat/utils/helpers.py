from datetime import datetime, timedelta, timezone


def get_now_beijing_time(delta: int = 0) -> str:
    """Return the current Beijing time as YYYY-MM-DD HH:MM."""
    beijing_tz = timezone(timedelta(hours=8 + delta))
    now = datetime.now(beijing_tz)
    return now.strftime("%Y-%m-%d %H:%M")
