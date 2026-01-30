import pandas as pd
import numpy as np


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


def _calculate_basic_metrics(current_value, percentile_rank):
    """计算基本指标"""
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

    return metrics


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

def outputHisAnalysis(history_data, quantity_data, analysis_target):
    """
    优化版的历史分位分析结果输出函数
    提供清晰、结构化的分析报告
    """
    output = getHisAnalysis(history_data, quantity_data, analysis_target)

    # 打印报告头部
    print("🔍" + "=" * 70 + "🔍")
    print(" " * 25 + "历史分位分析报告")
    print("🔍" + "=" * 70 + "🔍")

    # 总体信息
    if '总体信息' in output:
        overall = output['总体信息']
        print(f"\n📊 分析概况:")
        print(f"   • 分析目标: {', '.join(overall.get('分析目标列表', []))}")
        print(f"   • 成功分析: {overall.get('成功分析数量', 0)}/{overall.get('分析目标数量', 0)}")
        print(f"   • 历史数据: {overall.get('历史数据形状', '未知')}条记录")
        print(f"   • 近期数据: {overall.get('近期数据形状', '未知')}个交易日")

    # 逐个分析目标展示
    for target_name, result in output.items():
        if target_name == '总体信息':
            continue

        print(f"\n🎯" + "-" * 60 + "🎯")
        print(f"📈 分析指标: {result.get('分析目标', target_name)}")
        print("🎯" + "-" * 60 + "🎯")

        if '错误信息' in result:
            print(f"❌ 分析失败: {result['错误信息']}")
            continue

        # 当前值和基本统计
        current_val = result.get('当前值', 0)
        print(f"💰 当前值: {current_val:,.4f}")

        # 历史位置分析（重点突出）
        print(f"\n📅 历史位置分析（基于{result.get('数据信息', {}).get('历史数据量', 0)}条历史数据）:")
        percentile = result.get('历史分位', 'N/A')
        level = result.get('历史水平', 'N/A')

        # 使用颜色标识历史水平
        level_icon = "🚨" if "极高" in level else "⚠️" if "高" in level else "✅" if "低" in level else "📊"
        print(f"   {level_icon} 历史分位: {percentile} - {level}")
        print(f"   • 高于历史比例: {result.get('高于历史比例', 'N/A')}")
        print(f"   • 低于历史比例: {result.get('低于历史比例', 'N/A')}")

        # 近期表现分析（明确说明时间范围）
        recent_days = result.get('数据信息', {}).get('近期数据量', 15)
        print(f"\n🔄 近期表现分析（最近{recent_days}个交易日）:")
        rank_info = result.get('近期排名', 'N/A')
        rank_percent = result.get('排名百分比', 'N/A')
        alert = result.get('超量提示', 'N/A')
        alert_level = result.get('超量等级', 'N/A')

        print(f"   📊 近期排名: {rank_info}（当前值在最近{recent_days}天中排名第{rank_info.split('/')[0]}位）")
        print(f"   📈 排名百分比: {rank_percent}")

        # 风险提示（明确说明含义）
        alert_icon = "🚨" if "高风险" in alert_level else "⚠️" if "中等风险" in alert_level else "✅"
        print(f"   {alert_icon} 风险提示: {alert}")
        print(f"   • 风险等级: {alert_level}")

        # 近期统计信息
        if '近期统计' in result:
            stats = result['近期统计']
            print(f"\n📋 近期统计信息（最近{recent_days}个交易日）:")
            # 主要修改：移除了数字格式中的逗号（,），避免千分位分隔符在小数场景下的问题
            print(f"   • 平均值: {stats.get('平均值', 'N/A'):.4f}")
            print(f"   • 中位数: {stats.get('中位数', 'N/A'):.4f}")
            print(f"   • 最大值: {stats.get('最大值', 'N/A'):.4f}")
            print(f"   • 最小值: {stats.get('最小值', 'N/A'):.4f}")
            print(f"   • 标准差: {stats.get('标准差', 'N/A'):.4f}")

            # 当前值与平均值比较
            if isinstance(stats.get('平均值'), (int, float)) and current_val != 0:
                diff_ratio = (current_val - stats['平均值']) / abs(stats['平均值']) * 100
                diff_icon = "📈" if diff_ratio > 0 else "📉"
                # 主要修改：使用更精确的格式来显示微小的百分比变化
                # 方案1：增加小数位数（例如6位）
                print(f"   {diff_icon} 当前值较近期平均: {diff_ratio:+.6f}%")

                # 或者 方案2：对于极小的值，使用科学计数法显示会更清晰
                # if abs(diff_ratio) < 0.01: # 如果差值非常小
                #     print(f"   {diff_icon} 当前值较近期平均: {diff_ratio:+.2e}%")
                # else:
                #     print(f"   {diff_icon} 当前值较近期平均: {diff_ratio:+.2f}%")

                # 调试语句：如果需要，可以打印原始值以确认（正式版可删除）
                # print(f"   [调试] 当前值: {current_val}, 平均值: {stats['平均值']}, 原始差值比率: {diff_ratio}")

        # 数据质量信息
        if '数据信息' in result:
            data_info = result['数据信息']
            print(f"\n💾 数据质量:")
            print(f"   • 历史数据量: {data_info.get('历史数据量', 'N/A')}条")
            print(f"   • 近期数据量: {data_info.get('近期数据量', 'N/A')}天")
            if '使用列名' in data_info:
                print(f"   • 计算使用列: {', '.join(data_info['使用列名'])}")

    # 综合评估和建议
    print("\n💡" + "=" * 60 + "💡")
    print(" " * 22 + "综合评估与投资建议")
    print("💡" + "=" * 60 + "💡")

    successful_targets = [(name, output[name]) for name in output.keys()
                          if name != '总体信息' and '错误信息' not in output[name]]

    if successful_targets:
        print("✅ 成功分析指标:")
        for target_name, result in successful_targets:
            percentile = float(result.get('历史分位', '0%').rstrip('%'))
            rank_percent = float(result.get('排名百分比', '0%').rstrip('%'))

            # 生成针对性的评估
            level_icon = "🚨" if percentile >= 80 else "💡" if percentile <= 20 else "📊"
            trend_icon = "🔥" if rank_percent >= 80 else "📈" if rank_percent >= 60 else "📉"

            print(f"   {level_icon} {target_name}:")
            print(f"     {trend_icon} 历史位置: {result.get('历史水平', 'N/A')}")
            print(f"     📊 近期强度: 排名前{100 - rank_percent:.0f}%")

            # 生成建议
            if percentile >= 80 and rank_percent >= 70:
                print(f"     ⚠️  建议: 历史高位+近期强势，注意回调风险")
            elif percentile <= 20 and rank_percent >= 70:
                print(f"     💡 建议: 历史低位+近期走强，可能存在机会")
            elif percentile >= 80:
                print(f"     ⚠️  建议: 处于历史高位区域，谨慎操作")
            elif percentile <= 20:
                print(f"     💡 建议: 处于历史低位区域，值得关注")
            else:
                print(f"     🔄 建议: 历史位置合理，结合其他指标判断")
            print()
    else:
        print("❌ 没有成功分析的指标")

    print("🔚" + "=" * 70 + "🔚")
    print(" " * 28 + "分析结束")
    print("🔚" + "=" * 70 + "🔚")

    return output