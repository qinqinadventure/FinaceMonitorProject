import analysis.analysis_trend_func.hisfunc as hisfunc
from datetime import datetime
import crawler.stockdata as stockdata
import tools.fileTools as fileTools

def outputHisAnalysis(stock_code):
    # 加载配置
    # 使用原始字符串避免转义问题
    analysis_cfg = fileTools.jsonToDict("D:\project\pycharm\FinaceMonitorProject\config\\analysis_setting.json")
    # 获取关键参数
    history_days = analysis_cfg["history_days"]["value"]
    quantity_days = analysis_cfg["quantity_days"]["value"]
    analysis_target = analysis_cfg["analysis_target"]["value"]
    # 获取数据
    history_data = stockdata.getData(stock_code, history_days)
    quantity_data = stockdata.getData(stock_code, quantity_days)
    analysis_target = None
    """
    历史分位分析结果输出函数 - 返回字典格式便于前端使用
    Returns:
        dict: 结构化的分析结果，包含总体信息和各指标分析详情
    """
    # 获取分析结果
    analysis_result = hisfunc.getHisAnalysis(history_data, quantity_data, analysis_target)
    final_output = {
        "status": "success",
        "message": "历史分位分析完成",
        "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "overall_info": {},
        "detailed_analysis": {},
        "summary_assessment": {}
    }

    # 处理总体信息
    if '总体信息' in analysis_result:
        overall = analysis_result['总体信息']
        final_output["overall_info"] = {
            "target_count": overall.get('分析目标数量', 0),
            "success_count": overall.get('成功分析数量', 0),
            "target_list": overall.get('分析目标列表', []),
            "history_data_shape": overall.get('历史数据形状', '未知'),
            "recent_data_shape": overall.get('近期数据形状', '未知')
        }

    # 处理各指标的详细分析结果
    successful_targets = []

    for target_name, result in analysis_result.items():
        if target_name == '总体信息':
            continue

        target_analysis = {
            "analysis_target": result.get('分析目标', target_name),
            "status": "success" if '错误信息' not in result else "error",
            "current_value": result.get('当前值', 0),
            "historical_percentile": result.get('历史分位', 'N/A'),
            "historical_level": result.get('历史水平', 'N/A'),
            "above_history_ratio": result.get('高于历史比例', 'N/A'),
            "below_history_ratio": result.get('低于历史比例', 'N/A')
        }

        # 如果有错误信息，记录下来
        if '错误信息' in result:
            target_analysis["error_message"] = result['错误信息']
            target_analysis["available_columns"] = result.get('可用列名', [])
        else:
            # 添加近期表现分析
            target_analysis.update({
                "recent_ranking": result.get('近期排名', 'N/A'),
                "ranking_percentage": result.get('排名百分比', 'N/A'),
                "volume_alert": result.get('超量提示', 'N/A'),
                "risk_level": result.get('超量等级', 'N/A')
            })

            # 添加近期统计信息
            if '近期统计' in result:
                stats = result['近期统计']
                target_analysis["recent_statistics"] = {
                    "mean": stats.get('平均值', 0),
                    "median": stats.get('中位数', 0),
                    "max": stats.get('最大值', 0),
                    "min": stats.get('最小值', 0),
                    "std": stats.get('标准差', 0)
                }

            # 添加数据质量信息
            if '数据信息' in result:
                data_info = result['数据信息']
                target_analysis["data_quality"] = {
                    "history_data_count": data_info.get('历史数据量', 0),
                    "recent_data_count": data_info.get('近期数据量', 0),
                    "used_columns": data_info.get('使用列名', [])
                }

            # 添加关键价位分析 [5](@ref)
            if '关键价位分析' in result:
                levels_info = result['关键价位分析']
                target_analysis["key_level_analysis"] = {
                    "position_description": levels_info.get('动态描述', 'N/A'),
                    "detailed_levels": levels_info.get('详细价位', {})
                }

            successful_targets.append((target_name, result))

        final_output["detailed_analysis"][target_name] = target_analysis

    # 生成综合评估和建议 [1,2](@ref)
    assessment = {
        "successful_indicators_count": len(successful_targets),
        "overall_risk_assessment": "低风险",
        "trading_recommendations": [],
        "key_observations": []
    }

    if successful_targets:
        # 分析每个成功指标的风险等级
        risk_levels = []
        for target_name, result in successful_targets:
            percentile = float(result.get('历史分位', '0%').rstrip('%'))
            rank_percent = float(result.get('排名百分比', '0%').rstrip('%'))

            # 风险评估逻辑
            if percentile >= 80 and rank_percent >= 70:
                risk_levels.append("高风险")
                assessment["trading_recommendations"].append(
                    f"{target_name}: 历史高位+近期强势，注意回调风险"
                )
            elif percentile <= 20 and rank_percent >= 70:
                risk_levels.append("中等风险")
                assessment["trading_recommendations"].append(
                    f"{target_name}: 历史低位+近期走强，可能存在机会"
                )
            elif percentile >= 80:
                risk_levels.append("中等风险")
                assessment["trading_recommendations"].append(
                    f"{target_name}: 处于历史高位区域，谨慎操作"
                )
            elif percentile <= 20:
                risk_levels.append("低风险")
                assessment["trading_recommendations"].append(
                    f"{target_name}: 处于历史低位区域，值得关注"
                )
            else:
                risk_levels.append("低风险")
                assessment["trading_recommendations"].append(
                    f"{target_name}: 历史位置合理，结合其他指标判断"
                )

        # 确定整体风险评估
        if "高风险" in risk_levels:
            assessment["overall_risk_assessment"] = "高风险"
        elif "中等风险" in risk_levels:
            assessment["overall_risk_assessment"] = "中等风险"
        else:
            assessment["overall_risk_assessment"] = "低风险"

        # 生成关键观察点
        for target_name, result in successful_targets:
            percentile = float(result.get('历史分位', '0%').rstrip('%'))
            level = result.get('历史水平', 'N/A')

            assessment["key_observations"].append(
                f"{target_name}: 历史分位{percentile:.1f}% ({level})"
            )

    final_output["summary_assessment"] = assessment

    return final_output