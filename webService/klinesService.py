import crawler.k_data as kdata
import json
import const.config_const as config

# 获取日K线
def getDayKline(stock_code):
    # 获取配置
    cfg = json.loads(config.setting_path)
    # 获取
    dayKline = kdata.get_daily_kline(stock_code,)

# 获取近五日线
def getFiveDayKline(line_data):
    pass

# 获取周K线
def getDayKline(line_data):
    pass

# 获取月K线
def getDayKline(line_data):
    pass
