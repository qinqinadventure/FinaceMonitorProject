import akshare as ak
import datetime
import pandas as pd

# 根据股票代码获取股票信息
def get_stock_base_info(code):
    """
    根据股票代码获取基本信息，并整理为数据库字段格式
    """
    try:
        # 获取该股票的详细信息
        info_df = ak.stock_individual_info_em(symbol=code)
        # 将返回的DataFrame转换为字典，便于处理
        info_dict = dict(zip(info_df['item'], info_df['value']))

        # 构建符合数据库结构的数据字典
        stock_data = {
            'stock_code': f"sh.{code}" if code.startswith(('6', '9')) else f"sz.{code}",  # 添加市场前缀
            'stock_name': info_dict.get('股票简称', 'N/A'),
            'market': 'SH' if code.startswith(('6', '9')) else 'SZ',  # 简单判断市场
            'industry': info_dict.get('行业', 'N/A'),
            'listed_date': pd.to_datetime(info_dict.get('上市时间'), format='%Y%m%d').strftime(
                '%Y-%m-%d') if info_dict.get('上市时间') else None,
            'total_shares': int(float(info_dict.get('总股本', 0))),  # 注意单位转换，原始数据可能是万股或亿元
            'circulating_shares': int(float(info_dict.get('流通股', 0))),
            'created_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        return stock_data

    except Exception as e:
        print(f"获取股票 {code} 信息时出错: {e}")
        return None