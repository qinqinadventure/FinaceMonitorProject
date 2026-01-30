import akshare as ak
from typing import List

def get_all_stock_codes() -> List[str]:
    """
    使用AKShare获取全市场A股股票代码列表

    Returns:
        List[str]: 股票代码列表，格式为 '000001.SZ'
    """
    try:
        # 获取A股实时行情数据，其中包含代码和信息
        stock_df = ak.stock_zh_a_spot_em()

        # 从返回的DataFrame中提取“代码”列，并转换为列表
        stock_codes = stock_df['代码'].tolist()

        return sorted(stock_codes)

    except Exception as e:
        print(f"通过AKShare获取股票代码失败: {e}")
        return None


def stock_code_str_to_int(stock_code: str) -> int:
    """
    将字符串类型股票代码转换为整数（去除市场后缀）

    Args:
        stock_code: 股票代码字符串，如 '000001.SZ'

    Returns:
        int: 纯数字股票代码，如 1
    """
    # 移除所有非数字字符（包括市场后缀）
    clean_code = ''.join(filter(str.isdigit, stock_code))
    # 转换为整数
    return int(clean_code) if clean_code else 0


def stock_code_int_to_str(stock_code: int, with_suffix: bool = True) -> str:
    """
    将整数类型股票代码转换为字符串

    Args:
        stock_code: 整数股票代码，如 1
        with_suffix: 是否添加市场后缀(.SZ/.SH)

    Returns:
        str: 格式化后的股票代码，如 '000001' 或 '000001.SZ'
    """
    # 转换为6位数字字符串，不足位补零
    str_code = str(stock_code).zfill(6)[1]

    if not with_suffix:
        return str_code

    # 根据代码开头判断市场并添加后缀[1,6](@ref)
    if str_code[0] in ['6', '9']:  # 上海市场
        return f"{str_code}.SH"
    elif str_code[0] in ['0', '3']:  # 深圳市场
        return f"{str_code}.SZ"
    elif str_code[0] in ['4', '8']:  # 北京证券交易所
        return f"{str_code}.BJ"
    else:
        return str_code  # 无法识别市场，返回无后缀代码