
from datetime import datetime
import pytz


def datetime_to_timestamp(year: int, month: int, day: int,
                          hour: int= 0, minute: int= 0, second: int= 0,
                          timezone_offset: int= 8) -> int:
    """
    将给定的日期时间和时区偏移转换为Unix时间戳（秒级）

    参数:
        year (int): 年份，如2025
        month (int): 月份，1-12
        day (int): 日，1-31
        hour (int): 时，0-23
        minute (int): 分，0-59
        second (int): 秒，0-59
        timezone_offset (int): 时区偏移，如8表示东八区（UTC+8），-5表示西五区（UTC-5）

    返回:
        int: Unix时间戳（秒级）

    示例:
        >>> datetime_to_timestamp(2025, 6, 1, 0, 0, 0, 8)
        1748707200
    """
    # 创建时区对象
    tz = pytz.FixedOffset(timezone_offset * 60)

    # 创建指定时区的datetime对象
    dt = datetime(year, month, day, hour, minute, second, tzinfo=tz)

    # 转换为UTC时间并计算时间戳
    timestamp = int(dt.timestamp())

    return timestamp


def get_now_4_prompt() -> str:
    """
     用于提示词的当前日期
    :return:
    """
    return f"当前日期：{datetime.now()} \n"

# 示例用法
if __name__ == "__main__":
    # 示例：2025-06-01 00:00:00 UTC+8
    timestamp1 = datetime_to_timestamp(2025, 6, 1, 0, 0, 0, 8)
    print(get_now_4_prompt())