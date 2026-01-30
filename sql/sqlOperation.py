import sql.connect as connect
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('stock_data')


def getStockDataByCode(code, date=None):
    """
    根据股票代码和日期查询股票数据

    Args:
        code (str): 股票代码，例如 'sh.600000'
        date (str): 日期，格式 'YYYY-MM-DD'，默认为None

    Returns:
        tuple: (success, data)
        - success (bool): 查询是否成功
        - data: 成功时返回查询结果，失败时返回错误信息
    """
    try:
        if date:
            sql = "SELECT * FROM stock_data WHERE stock_code = %s AND trade_date = %s ORDER BY trade_date DESC"
            params = (code, date)
        else:
            sql = "SELECT * FROM stock_data WHERE stock_code = %s ORDER BY trade_date DESC"
            params = (code,)

        success, result = connect.executeSQL(sql)
        return (success, result)

    except Exception as e:
        logger.error(f"查询股票数据失败: {e}")
        return (False, f"查询失败: {str(e)}")


def insertStockData(stock_data):
    """
    插入股票数据

    Args:
        stock_data (dict): 包含股票数据的字典，应有以下字段：
            - trade_date: 交易日期
            - stock_code: 股票代码
            - open_price: 开盘价
            - close_price: 收盘价
            - high_price: 最高价
            - low_price: 最低价
            - volume: 成交量
            - turnover: 成交额
            - amplitude: 振幅
            - pct_change: 涨跌幅
            - change_amount: 涨跌额
            - turnover_rate: 换手率

    Returns:
        tuple: (success, message)
    """
    required_fields = [
        'trade_date', 'stock_code', 'open_price', 'close_price',
        'high_price', 'low_price', 'volume', 'turnover',
        'amplitude', 'pct_change', 'change_amount', 'turnover_rate'
    ]

    # 验证数据完整性
    for field in required_fields:
        if field not in stock_data:
            return (False, f"缺少必要字段: {field}")

    try:
        sql = """INSERT INTO stock_data
                 (trade_date, stock_code, open_price, close_price, high_price, low_price,
                  volume, turnover, amplitude, pct_change, change_amount, turnover_rate, created_time)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        params = (
            stock_data['trade_date'],
            stock_data['stock_code'],
            stock_data['open_price'],
            stock_data['close_price'],
            stock_data['high_price'],
            stock_data['low_price'],
            stock_data['volume'],
            stock_data['turnover'],
            stock_data['amplitude'],
            stock_data['pct_change'],
            stock_data['change_amount'],
            stock_data['turnover_rate'],
            datetime.now()
        )

        success, result = connect.executeSQL(sql, params)
        if success:
            return (True, "插入成功")
        else:
            return (False, f"插入失败: {result}")

    except Exception as e:
        logger.error(f"插入股票数据失败: {e}")
        return (False, f"插入失败: {str(e)}")

def deleteStockData(code, date=None):
    """
    删除股票数据

    Args:
        code (str): 股票代码
        date (str): 日期，格式 'YYYY-MM-DD'，如果为None则删除该股票所有数据

    Returns:
        tuple: (success, message)
    """
    try:
        if date:
            sql = "DELETE FROM stock_data WHERE stock_code = %s AND trade_date = %s"
            params = (code, date)
            message = f"删除股票 {code} 在 {date} 的数据"
        else:
            sql = "DELETE FROM stock_data WHERE stock_code = %s"
            params = (code,)
            message = f"删除股票 {code} 的所有数据"

        success, result = connect.executeSQL(sql)
        if success:
            return (True, f"{message}，执行成功")
        else:
            return (False, f"删除失败: {result}")

    except Exception as e:
        logger.error(f"删除股票数据失败: {e}")
        return (False, f"删除失败: {str(e)}")


def updateStockData(code, date, update_fields):
    """
    更新股票数据

    Args:
        code (str): 股票代码
        date (str): 交易日期
        update_fields (dict): 要更新的字段和值

    Returns:
        tuple: (success, message)
    """
    if not update_fields:
        return (False, "没有提供要更新的字段")

    try:
        # 动态构建SET子句
        set_clause = ", ".join([f"{field} = %s" for field in update_fields.keys()])
        sql = f"UPDATE stock_data SET {set_clause}, updated_time = %s WHERE stock_code = %s AND trade_date = %s"

        # 准备参数
        params = list(update_fields.values())
        params.extend([datetime.now(), code, date])

        success, result = connect.executeSQL(sql)
        if success:
            if hasattr(result, 'rowcount') and result.rowcount == 0:
                return (False, "未找到匹配的数据")
            return (True, "更新成功")
        else:
            return (False, f"更新失败: {result}")

    except Exception as e:
        logger.error(f"更新股票数据失败: {e}")
        return (False, f"更新失败: {str(e)}")