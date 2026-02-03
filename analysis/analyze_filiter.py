import json
import const.config_const as conf
import tools.fileTools as fileTools
import analyze_level
import analyze_trend

# 获取所有的分析结果
def get_all(stock_code):
    # 加载分析信息
    analysis_setting = fileTools.jsonToDict(conf.analysis_setting_path)
    # 加载信息
    # 从 analysis_setting 中提取数据
    # 获取 press_level 字典
    press_level_data = analysis_setting.get('press_level', {})
    # 提取历史分位判断的天数
    history_days_value = press_level_data.get('history_days', {}).get('value')
    # 提取量比分析的天数
    quantity_days_value = press_level_data.get('quantity_days', {}).get('value')
    # 提取待分析指标列表
    analysis_target_value = press_level_data.get('analysis_target', {}).get('value')
    #

    # 获取压力位分析结果
    level_message = analyze_level.outputHisAnalysis()

# 过滤利好消息
def get_good_filiter(stock_code):
    pass

# 过滤利空消息
def get_bad_filiter(stock_code):
    pass