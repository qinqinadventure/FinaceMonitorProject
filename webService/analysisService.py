import analysis.analyze_level as analyze_level
import analysis.analyze_press as analyze_press
import analysis.analyze_filiter as analyze_filter
import tools.codeTools as codeTools

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

# 获取所有股票的利好信息
def alarm_all():
    # 获取所有股票信息
    stock_code_list = codeTools.get_all_stock_codes()
    init_message = {}
    # 遍历所有股票信息
    # 总结其中的利好利空信息
    for stock_code in stock_code_list:
        pass

