import json
import pandas as pd
import numpy as np
from datetime import datetime
from tools.fileTools import jsonToDict

# 获取配置
cfg = jsonToDict("config/press_setting.json")

def _calculate_recent_metrics(quantity_data, column_name, current_value):
    """计算近期指标"""
    metrics = {}

    quantity_values = quantity_data[column_name].dropna()
    if len(quantity_values) > 0:
        # 计算排名
        sorted_values = np.sort(quantity_values)
        rank = np.searchsorted(sorted_values, current_value, side='right')
        rank_percentage = (rank / len(quantity_values)) * 100

        metrics['近期排名'] = f"{rank}/{len(quantity_values)}"
        metrics['排名百分比'] = f"{rank_percentage:.2f}%"

        # 超量提示
        if rank_percentage >= 70:
            metrics['超量提示'] = "⚠️ 超量：处于近期前30%"
            metrics['超量等级'] = "高风险" if rank_percentage >= 90 else "中等风险"
        else:
            metrics['超量提示'] = "正常范围"
            metrics['超量等级'] = "低风险"

        # 统计信息
        metrics['近期统计'] = {
            '平均值': float(np.mean(quantity_values)),
            '中位数': float(np.median(quantity_values)),
            '最大值': float(np.max(quantity_values)),
            '最小值': float(np.min(quantity_values)),
            '标准差': float(np.std(quantity_values))
        }

    return metrics

def _process_simple_column(history_data, quantity_data, column_name, available_columns):
    """处理简单列名分析"""
    if column_name not in available_columns:
        raise KeyError(f"列名 '{column_name}' 不存在。可用列名: {available_columns}")

    result = {'分析目标': column_name}

    # 获取当前值
    current_value = quantity_data[column_name].iloc[-1]

    # 历史分位分析
    history_values = history_data[column_name].dropna()
    if len(history_values) == 0:
        raise ValueError(f"列 '{column_name}' 的历史数据为空")

    percentile_rank = np.sum(history_values <= current_value) / len(history_values) * 100

    # 填充结果
    result.update(_calculate_basic_metrics(current_value, percentile_rank))
    result.update(_calculate_recent_metrics(quantity_data, column_name, current_value))
    result['数据信息'] = {
        '历史数据量': len(history_values),
        '近期数据量': len(quantity_data[column_name].dropna())
    }

    return result


def _process_compound_expression(history_data, quantity_data, expression, available_columns):
    """处理复合表达式分析"""
    # 解析表达式中的列名
    import re
    potential_columns = re.findall(r'[\u4e00-\u9fa5]+', expression)

    # 验证列名是否存在
    valid_columns = []
    for col in potential_columns:
        if col in available_columns:
            valid_columns.append(col)

    if len(valid_columns) < 2:
        raise ValueError(f"表达式中需要至少两个有效列名，找到的列: {valid_columns}。可用列名: {available_columns}")

    result = {'分析目标': expression}

    try:
        # 为历史数据和近期数据计算表达式结果
        history_data_copy = history_data.copy()
        quantity_data_copy = quantity_data.copy()

        # 安全地执行表达式
        history_data_copy['复合指标'] = history_data_copy.eval(expression, engine='python')
        quantity_data_copy['复合指标'] = quantity_data_copy.eval(expression, engine='python')

        # 获取当前值
        current_value = quantity_data_copy['复合指标'].iloc[-1]

        # 历史分位分析
        history_values = history_data_copy['复合指标'].dropna()
        if len(history_values) == 0:
            raise ValueError(f"复合表达式 '{expression}' 的历史数据为空")

        percentile_rank = np.sum(history_values <= current_value) / len(history_values) * 100

        # 填充结果
        result.update(_calculate_basic_metrics(current_value, percentile_rank))
        result.update(_calculate_recent_metrics(quantity_data_copy, '复合指标', current_value))
        result['数据信息'] = {
            '历史数据量': len(history_values),
            '近期数据量': len(quantity_data_copy['复合指标'].dropna()),
            '使用列名': valid_columns
        }

    except Exception as e:
        raise ValueError(f"计算表达式 '{expression}' 处理失败: {str(e)}")

    return result


def getHisAnalysis(history_data, quantity_data, analysis_target):
    """
    历史分位分析函数 - 支持analysis_target为列表，保持原始顺序
    """
    results = {}

    # 确保analysis_target是列表格式
    if isinstance(analysis_target, str):
        analysis_target = [analysis_target]

    # 获取所有可用列名
    available_columns = list(history_data.columns)

    for target in analysis_target:
        target_results = {}

        try:
            # 检查是否为复合表达式（包含运算符）
            if any(op in target for op in ['+', '-', '*', '/']):
                # 处理复合表达式
                target_results = _process_compound_expression(history_data, quantity_data, target, available_columns)
            else:
                # 处理简单列名
                target_results = _process_simple_column(history_data, quantity_data, target, available_columns)

        except Exception as e:
            target_results = {
                '分析目标': target,
                '错误信息': f"处理失败: {str(e)}",
                '可用列名': available_columns
            }

        # 使用原始目标名称作为键，确保与输入顺序一致
        results[target] = target_results

    # 添加总体信息
    results['总体信息'] = {
        '分析目标数量': len(analysis_target),
        '分析目标列表': analysis_target,  # 保持原始顺序
        '成功分析数量': sum(1 for target in analysis_target if '错误信息' not in results[target]),
        '历史数据形状': history_data.shape,
        '近期数据形状': quantity_data.shape
    }

    return results

def _calculate_pressure_support_levels(history_series, current_value):
    """
    计算关键时间窗口的压力位和支撑位（最高价/最低价）

    Returns:
        dict: 包含各时间窗口的压力位和支撑位信息
    """
    levels = {}

    for period_name, window_size in cfg.items():
        # 确保有足够的数据进行计算
        if len(history_series) < window_size:
            # 数据不足时使用全部可用数据
            window_data = history_series
            actual_period = f"全历史({len(history_series)}天)"
        else:
            window_data = history_series.tail(window_size)
            actual_period = period_name

        if len(window_data) > 0:
            resistance_level = float(window_data.max())  # 压力位（最高价）
            support_level = float(window_data.min())  # 支撑位（最低价）

            levels[actual_period] = {
                '压力位': resistance_level,
                '支撑位': support_level,
                '数据天数': len(window_data)
            }

    return levels


def _assess_position_relative_to_levels(current_value, levels_dict):
    """
    分析当前价格相对于关键价位的位置关系，并生成动态描述
    """
    if not levels_dict:
        return "数据不足进行关键价位分析"

    # 按时间从短到长排序，分析短期到长期的态势
    sorted_periods = sorted(levels_dict.keys(),
                            key=lambda x: list(cfg.keys()).index(x)
                            if x in cfg else len(cfg))

    current_desc = []
    breached_resistance = []  # 已突破的压力位
    breached_support = []  # 已跌破的支撑位
    approaching_resistance = []  # 正在逼近的压力位
    approaching_support = []  # 正在逼近的支撑位

    for period in sorted_periods:
        data = levels_dict[period]
        resistance = data['压力位']
        support = data['支撑位']

        # 判断与压力位的关系（考虑3%的突破容差）
        if current_value > resistance * 1.03:
            breached_resistance.append((period, resistance))
        elif current_value > resistance:
            current_desc.append(f"刚突破{period}压力位({resistance:.2f})")
        elif current_value > resistance * 0.97:
            approaching_resistance.append((period, resistance))

        # 判断与支撑位的关系
        if current_value < support * 0.97:
            breached_support.append((period, support))
        elif current_value < support:
            current_desc.append(f"刚跌破{period}支撑位({support:.2f})")
        elif current_value < support * 1.03:
            approaching_support.append((period, support))

    # 生成综合描述
    if breached_resistance:
        # 找出已突破的最强压力位
        strongest_breached = max(breached_resistance, key=lambda x: x[1])
        next_target = []

        # 寻找下一个待突破的压力位
        for period in sorted_periods:
            if period not in [x[0] for x in breached_resistance]:
                resistance = levels_dict[period]['压力位']
                if resistance > current_value:
                    next_target.append((period, resistance))
                    break

        if next_target:
            current_desc.append(
                f"已突破{strongest_breached[0]}压力位，向{next_target[0][0]}压力位({next_target[0][1]:.2f})突进")
        else:
            current_desc.append(f"已突破所有关键压力位，处于强势上升通道")

    elif breached_support:
        # 找出已跌破的最强支撑位
        strongest_breached = min(breached_support, key=lambda x: x[1])
        next_target = []

        # 寻找下一个支撑位
        for period in sorted_periods:
            if period not in [x[0] for x in breached_support]:
                support = levels_dict[period]['支撑位']
                if support < current_value:
                    next_target.append((period, support))
                    break

        if next_target:
            current_desc.append(
                f"已跌破{strongest_breached[0]}支撑位，向{next_target[0][0]}支撑位({next_target[0][1]:.2f})下探")
        else:
            current_desc.append(f"已跌破所有关键支撑位，处于弱势下行通道")

    elif approaching_resistance:
        current_desc.append(f"在{approaching_resistance[0][0]}压力位({approaching_resistance[0][1]:.2f})附近徘徊")

    elif approaching_support:
        current_desc.append(f"在{approaching_support[0][0]}支撑位({approaching_support[0][1]:.2f})附近震荡")

    else:
        current_desc.append("在关键价位区间内正常波动")

    return "；".join(current_desc) if current_desc else "价格处于平衡状态"


# 在 _calculate_basic_metrics 函数中集成关键价位分析
def _calculate_basic_metrics(current_value, percentile_rank, history_series):
    """计算基本指标（集成关键价位分析）"""
    metrics = {
        '当前值': float(current_value),
        '历史分位': f"{percentile_rank:.2f}%",
        '高于历史比例': f"{percentile_rank:.2f}%",
        '低于历史比例': f"{(100 - percentile_rank):.2f}%"
    }

    # 判断历史水平
    if percentile_rank >= 90:
        metrics['历史水平'] = "极高水平(前10%)"
    elif percentile_rank >= 70:
        metrics['历史水平'] = "高水平(前30%)"
    elif percentile_rank >= 30:
        metrics['历史水平'] = "中等水平"
    elif percentile_rank >= 10:
        metrics['历史水平'] = "低水平(后30%)"
    else:
        metrics['历史水平'] = "极低水平(后10%)"

    # 新增：关键价位分析
    if history_series is not None:
        levels = _calculate_pressure_support_levels(history_series, current_value)
        position_desc = _assess_position_relative_to_levels(current_value, levels)

        metrics['关键价位分析'] = {
            '动态描述': position_desc,
            '详细价位': levels
        }

    return metrics