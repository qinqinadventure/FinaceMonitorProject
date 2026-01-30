import crawler.k_data as kdata
import json
import const.config_const as config

# 获取日K线
def getDayKline(stock_code):
    # 获取配置
    cfg = json.loads(config.setting_path)
    # 获取初始的窗口大小

    # 获取k线
    dayKline = kdata.get_daily_kline(stock_code,cfg['start_date'],cfg['end_date'])

# 获取近五日线
def getFiveDayKline(line_data):
    pass

# 获取周K线
def getDayKline(line_data):
    pass

# 获取月K线
def getDayKline(line_data):
    pass
