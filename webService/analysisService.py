import json
import analysis.analyze_level as analyze_level
import analysis.analyze_trend as analyze_trend
import analysis.analyze_filiter as analyze_filter
import tools.codeTools as codeTools
import multiprocessing
import tools.fileTools as fileTools
from concurrent.futures import ProcessPoolExecutor
import concurrent

# 分析多只股票
def analysis_multi():
    pass

# 分析单只股票
def analysis_sigle(stock_code):
    level_message = analyze_level.outputHisAnalysis()

# 获取单个股票利好信息
def alarm_single_good(stock_code):
    good_message = {
        "stock_code": stock_code,
        "good_message": analyze_filter.get_good_filiter(stock_code),
    }
    return good_message

# 获取单个股票利空信息
def alarm_single_bad(stock_code):
    good_message = {
        "stock_code": stock_code,
        "bad_message": analyze_filter.get_bad_filiter(stock_code),
    }
    return good_message

# 获取所有股票的信息
def alarm_all():
    # 获取所有股票信息
    stock_code_list = codeTools.get_all_stock_codes()
    result_dict = {}
    # 获取多进程配置
    multi_config = fileTools.jsonToDict("config/multi_setting.json")
    num_workers = multi_config["num_workers"]["value"]
    # 遍历所有股票信息
    # 总结其中的利好利空信息
    # 多进程版本 (能真正利用多核CPU)
    with ProcessPoolExecutor(max_workers=num_workers) as executor:  # 关键修改
        # 分析趋势信息
        trends = {executor.submit(analyze_trend.outputLevelInfo, stock_code): stock_code for stock_code in stock_code_list}
        for trend in trends:
            try:
                result_dict["trend"] = trend.result()
            except Exception as e:
                print("遍历过程中发生错误:" + str(e))
        # 分析压力信息
        presses = {executor.submit(analyze_level.outputHisAnalysis, stock_code): stock_code for stock_code in stock_code_list}
        for press in presses:
            try:
                result_dict["press"] = press.result()
            except Exception as e:
                print("遍历过程中发生错误:" + str(e))
    return result_dict


