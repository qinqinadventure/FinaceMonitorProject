from datetime import datetime, date, timedelta


def get_current_time():
    """
    获取当前时间

    Returns:
        datetime: 包含当前日期和时间的datetime对象
    """
    return datetime.now()


def get_today_date():
    """
    获取今天日期

    Returns:
        date: 只包含日期的date对象
    """
    return date.today()


def get_date_before_days(before_days, base_date=None):
    """
    获取今天及之前before_days天的日期

    Args:
        before_days (int): 之前的天数
        base_date (date/datetime, optional): 基准日期，默认为今天

    Returns:
        list: 包含今天及之前before_days天的日期列表
    """
    if base_date is None:
        base_date = date.today()

    # 如果是datetime对象，转换为date对象
    if isinstance(base_date, datetime):
        base_date = base_date.date()

    dates = []
    for i in range(before_days + 1):
        target_date = base_date - timedelta(days=i)
        dates.append(target_date)

    return dates


def format_date_to_yyyymmdd(input_date):
    """
    将datetime格式日期转为YYYYMMDD格式

    Args:
        input_date (date/datetime): 输入的日期对象

    Returns:
        str: YYYYMMDD格式的字符串
    """
    if isinstance(input_date, datetime):
        return input_date.strftime('%Y%m%d')
    elif isinstance(input_date, date):
        return input_date.strftime('%Y%m%d')
    else:
        raise ValueError("输入必须是date或datetime对象")


# 增强函数：更多实用的日期操作
def get_date_range(start_date, end_date):
    """
    获取两个日期之间的所有日期

    Args:
        start_date (date/datetime): 开始日期
        end_date (date/datetime): 结束日期

    Returns:
        list: 日期范围内的所有日期列表
    """
    if isinstance(start_date, datetime):
        start_date = start_date.date()
    if isinstance(end_date, datetime):
        end_date = end_date.date()

    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)

    return dates


def is_weekend(input_date):
    """
    判断日期是否为周末

    Args:
        input_date (date/datetime): 输入的日期

    Returns:
        bool: 如果是周末返回True，否则返回False
    """
    if isinstance(input_date, datetime):
        return input_date.weekday() >= 5
    else:
        return input_date.weekday() >= 5


# 示例使用
if __name__ == "__main__":
    # 1. 获取当前时间
    current_time = get_current_time()
    print(f"当前时间: {current_time}")

    # 2. 获取今天日期
    today = get_today_date()
    print(f"今天日期: {today}")

    # 3. 获取今天及之前5天的日期
    last_5_days = get_date_before_days(5)
    print("今天及之前5天的日期:")
    for day in last_5_days:
        print(f"  {day}")

    # 4. 格式化为YYYYMMDD
    formatted_today = format_date_to_yyyymmdd(today)
    formatted_time = format_date_to_yyyymmdd(current_time)
    print(f"今天日期(YYYYMMDD): {formatted_today}")
    print(f"当前时间日期部分(YYYYMMDD): {formatted_time}")

    # 5. 使用基准日期获取之前日期
    specific_date = date(2024, 1, 15)
    dates_from_specific = get_date_before_days(3, specific_date)
    print(f"{specific_date}及之前3天的日期:")
    for day in dates_from_specific:
        formatted_day = format_date_to_yyyymmdd(day)
        print(f"  {day} -> {formatted_day}")

    # 6. 额外功能示例
    date_range = get_date_range(date(2024, 1, 1), date(2024, 1, 5))
    print("2024年1月1日到5日的日期范围:")
    for day in date_range:
        weekend_status = "周末" if is_weekend(day) else "工作日"
        print(f"  {day} ({weekend_status})")