"""获取当前时间的工具函数。"""

from datetime import datetime, timedelta, timezone


def get_current_time_iso() -> str:
    """返回当前时间的 ISO 8601 字符串（UTC，含时区偏移）。"""
    return datetime.now(timezone.utc).isoformat()


def get_current_time_bj_iso() -> str:
    """返回北京时间的 ISO 8601 字符串（UTC+8，含时区偏移）。"""
    bj_tz = timezone(timedelta(hours=8))
    return datetime.now(bj_tz).isoformat()

if __name__ == "__main__":
    print(get_current_time_bj_iso())
