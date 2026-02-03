import analysis.analysis_level_func.level as level
from datetime import datetime

def outputLevelInfo(stock_data, valuation_data=None, current_pe=None, current_pb=None):
    """
    返回完整的股票分析信息（结构化字典格式）

    Args:
        stock_data: 股票数据
        valuation_data: 估值数据（可选）
        current_pe: 当前PE（可选）
        current_pb: 当前PB（可选）

    Returns:
        dict: 结构化的股票分析信息
    """
    # 调用分析函数
    result = level.getLevel(stock_data, valuation_data, current_pe, current_pb)

    # 构建结构化返回字典
    structured_result = {
        "status": "success",
        "analysis_time": result.get('分析时间', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "data": {
            "trend_analysis": {
                "current_price": result['趋势分析']['收盘价'],
                "ma10": result['趋势分析']['MA10'],
                "ma20": result['趋势分析']['MA20'],
                "ma30": result['趋势分析']['MA30'],
                "trend_status": result['趋势分析']['趋势']
            },
            "resistance_analysis": result['压力位分析'],
            "ma_relationship": result['均线关系分析'],
            "historical_analysis": {},
            "valuation_analysis": {},
            "comprehensive_suggestion": result.get('综合建议', '暂无建议')
        }
    }

    # 处理历史位置分析
    historical = result['历史位置分析']
    if isinstance(historical, dict):
        structured_result["data"]["historical_analysis"] = {
            "current_price": historical.get('当前价格'),
            "historical_high": historical.get('历史高点'),
            "historical_low": historical.get('历史低点'),
            "position_percentage": historical.get('位置百分比'),
            "position_level": historical.get('位置级别'),
            "analysis_period": historical.get('分析周期')
        }
    else:
        structured_result["data"]["historical_analysis"] = {
            "message": historical
        }

    # 处理估值分析
    valuation = result['估值分析']
    if valuation is not None:
        if '综合估值' in valuation:
            # 详细估值分析模式
            structured_result["data"]["valuation_analysis"] = {
                "pe_percentile": valuation.get('PE分位'),
                "pb_percentile": valuation.get('PB分位'),
                "comprehensive_valuation": valuation.get('综合估值'),
                "current_pe": valuation.get('当前PE'),
                "current_pb": valuation.get('当前PB'),
                "analysis_type": "detailed"
            }
        else:
            # 简化估值分析模式
            structured_result["data"]["valuation_analysis"] = {
                "pe_level": valuation.get('PE水平'),
                "pb_level": valuation.get('PB水平'),
                "current_pe": valuation.get('当前PE'),
                "current_pb": valuation.get('当前PB'),
                "analysis_type": "simplified"
            }
    else:
        structured_result["data"]["valuation_analysis"] = {
            "message": "无估值数据",
            "analysis_type": "none"
        }

    return structured_result