import json
import const.config_const as conf

# 获取所有的分析结果
def get_all(stock_code):
    analysis_setting = json.load(conf.analysis_setting_path)


# 过滤利好消息
def get_good_filiter(stock_code):
    pass

# 过滤利空消息
def get_bad_filiter(stock_code):
    pass