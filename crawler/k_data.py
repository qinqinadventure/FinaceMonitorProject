import akshare as ak
import pandas as pd
from typing import Optional

def get_daily_kline(
        symbol: str,
        start_date: str,
        end_date: str,
        adjust: str = "qfq"
) -> pd.DataFrame:
    """
    获取股票日K线数据[1,7](@ref)

    参数:
        symbol: 股票代码, 6位数字，例如 "000001"
        start_date: 开始日期, 格式 "YYYYMMDD"
        end_date: 结束日期, 格式 "YYYYMMDD"
        adjust: 复权类型, ""(不复权), "qfq"(前复权), "hfq"(后复权)[1](@ref)

    返回:
        DataFrame: 包含日期、开盘价、收盘价、最高价、最低价、成交量等列的DataFrame[7](@ref)
    """
    try:
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust=adjust
        )
        # 确保日期列是日期类型并排序
        if '日期' in df.columns:
            df['日期'] = pd.to_datetime(df['日期'])
            df = df.sort_values('日期').reset_index(drop=True)
        return df
    except Exception as e:
        print(f"获取日K线数据失败: {e}")
        return pd.DataFrame()


def get_weekly_kline(
        symbol: str,
        start_date: str,
        end_date: str,
        adjust: str = "qfq"
) -> pd.DataFrame:
    """
    获取股票周K线数据[7](@ref)

    参数与返回格式同get_daily_kline，但周期为周线[7](@ref)
    """
    try:
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="weekly",
            start_date=start_date,
            end_date=end_date,
            adjust=adjust
        )
        if '日期' in df.columns:
            df['日期'] = pd.to_datetime(df['日期'])
            df = df.sort_values('日期').reset_index(drop=True)
        return df
    except Exception as e:
        print(f"获取周K线数据失败: {e}")
        return pd.DataFrame()


def get_monthly_kline(
        symbol: str,
        start_date: str,
        end_date: str,
        adjust: str = "qfq"
) -> pd.DataFrame:
    """
    获取股票月K线数据[7](@ref)

    参数与返回格式同get_daily_kline，但周期为月线[7](@ref)
    """
    try:
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="monthly",
            start_date=start_date,
            end_date=end_date,
            adjust=adjust
        )
        if '日期' in df.columns:
            df['日期'] = pd.to_datetime(df['日期'])
            df = df.sort_values('日期').reset_index(drop=True)
        return df
    except Exception as e:
        print(f"获取月K线数据失败: {e}")
        return pd.DataFrame()


def get_intraday_minute_data(
        symbol: str,
        trade_date: Optional[str] = None,
        period: str = "1",
        adjust: str = ""
) -> pd.DataFrame:
    """
    获取股票分钟级分时数据[7,9](@ref)

    参数:
        symbol: 股票代码, 6位数字，例如 "000001"
        trade_date: 交易日期, 格式 "YYYYMMDD"。默认为None，通常返回最近交易日的数据[7](@ref)
        period: 分钟周期, 可选 "1", "5", "15", "30", "60"[7,9](@ref)
        adjust: 复权类型，同其他函数[7](@ref)

    返回:
        DataFrame: 包含日期时间、开盘、收盘、最高、最低、成交量等列的DataFrame[7](@ref)
    """
    try:
        # 方案1：使用 stock_zh_a_hist_min_em 接口（推荐，参数更清晰）
        # 注意：此接口可能对历史数据范围有限制，通常能获取近期数据[7](@ref)
        df = ak.stock_zh_a_hist_min_em(
            symbol=symbol,
            period=period,
            start_date=trade_date,  # 传入具体日期则获取该日数据
            end_date=trade_date,
            adjust=adjust
        )

        # 方案2（备选）：如果上述接口不可用，可以尝试 stock_zh_a_minute
        # if df.empty:
        #     df = ak.stock_zh_a_minute(symbol=symbol, period=period)

        if not df.empty and '时间' in df.columns:
            df['时间'] = pd.to_datetime(df['时间'])
            df = df.sort_values('时间').reset_index(drop=True)
        return df
    except Exception as e:
        print(f"获取分时数据失败: {e}")
        return pd.DataFrame()


def get_hist_kline(
        symbol: str,
        period: str = "daily",
        start_date: str = "20200101",
        end_date: str = "20251231",
        adjust: str = "qfq"
) -> pd.DataFrame:
    """
    统一获取历史K线数据的入口函数[1](@ref)

    参数:
        period: 周期类型, "daily"(日线), "weekly"(周线), "monthly"(月线)[7](@ref)
        其他参数同get_daily_kline
    """
    period_map = {
        "daily": get_daily_kline,
        "weekly": get_weekly_kline,
        "monthly": get_monthly_kline
    }

    if period not in period_map:
        print(f"不支持的周期类型: {period}，使用默认日线")
        period = "daily"

    return period_map[period](symbol, start_date, end_date, adjust)


# 使用示例
if __name__ == "__main__":
    stock_code = "000001"  # 平安银行

    # 1. 获取日K线数据
    daily_data = get_daily_kline(stock_code, "20250101", "20251231")
    print(f"日K线数据量: {len(daily_data)}")

    # 2. 获取周K线数据
    weekly_data = get_weekly_kline(stock_code, "20240101", "20251231")
    print(f"周K线数据量: {len(weekly_data)}")

    # 3. 获取月K线数据
    monthly_data = get_monthly_kline(stock_code, "20200101", "20251231")
    print(f"月K线数据量: {len(monthly_data)}")

    # 4. 获取今日分时数据 (1分钟线)
    intraday_data = get_intraday_minute_data(stock_code, period="1")
    print(f"分时数据量: {len(intraday_data)}")

    # 5. 使用统一入口函数
    data = get_hist_kline(stock_code, "weekly", "20240101", "20241231")
    print(f"通过统一入口获取的数据量: {len(data)}")