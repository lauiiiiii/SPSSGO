# -*- coding: utf-8 -*-
# MaxDiff（最大差异分析）：偏好测量方法，属于离散选择实验家族。
# 支持两种数据格式：
# 1. MaxDiff Pro（原始数据）：最重要变量 + 最不重要变量 + 选项变量
# 2. MaxDiff（汇总数据）：最重要次数 + 最不重要次数 + 总次数 + 索引项
# 算法：计数法，统计 Best/Worst 次数，计算净得分和重要度百分比。
from backend.analysis.common import *


def inject_metadata(metadata_map, params):
    """注入变量标题，让输出用题目名而非变量名显示。"""
    enriched = dict(params or {})
    # 收集所有变量
    all_vars = []
    all_vars.extend(_as_list(enriched.get("best_variable", [])))
    all_vars.extend(_as_list(enriched.get("worst_variable", [])))
    all_vars.extend(_as_list(enriched.get("option_variables", [])))
    all_vars.extend(_as_list(enriched.get("best_count_variable", [])))
    all_vars.extend(_as_list(enriched.get("worst_count_variable", [])))
    all_vars.extend(_as_list(enriched.get("total_count_variable", [])))
    all_vars.extend(_as_list(enriched.get("index_variable", [])))
    enriched["variable_labels"] = {
        variable: metadata_map.get(variable, {}).get("display_name") or variable
        for variable in all_vars
    }
    return enriched


METHOD_KEY = "maxdiff"
METHOD_META = {
    "label": "MaxDiff模型",
    "category": "综合评价",
    "description": "最大差异分析，测量偏好排序，支持原始数据和汇总数据两种格式",
    "order": 75,
    "aliases": ["MaxDiff", "最大差异分析", "最大差异模型", "maxdiff", "MaxDiff Pro"],
    "slots": [
        {
            "key": "best_variable",
            "label": "最重要变量",
            "type": "single",
            "accept": "categorical",
            "hint": "放入受访者选择的最重要选项变量（定类）",
            "optional": True,
        },
        {
            "key": "worst_variable",
            "label": "最不重要变量",
            "type": "single",
            "accept": "categorical",
            "hint": "放入受访者选择的最不重要选项变量（定类）",
            "optional": True,
        },
        {
            "key": "option_variables",
            "label": "选项变量",
            "type": "multiple",
            "accept": "categorical",
            "min": 2,
            "hint": "放入所有选项变量（定类，变量数≥2）",
            "optional": True,
        },
        {
            "key": "best_count_variable",
            "label": "最重要次数",
            "type": "single",
            "accept": "numeric",
            "hint": "放入最重要出现次数变量（定量）",
            "optional": True,
        },
        {
            "key": "worst_count_variable",
            "label": "最不重要次数",
            "type": "single",
            "accept": "numeric",
            "hint": "放入最不重要出现次数变量（定量）",
            "optional": True,
        },
        {
            "key": "total_count_variable",
            "label": "总出现次数",
            "type": "single",
            "accept": "numeric",
            "hint": "放入总出现次数变量（定量）",
            "optional": True,
        },
        {
            "key": "index_variable",
            "label": "索引项",
            "type": "single",
            "accept": "categorical",
            "hint": "放入索引项变量（定类，选项名称）",
            "optional": True,
        },
    ],
    "options": [],
    "param_builder": "direct",
}

_REFS_MAXDIFF = _REFS_GENERAL + [
    "[3] Louviere J J, Flynn T N, Carson R T. Discrete choice experiments are not conjoint analysis[J]. Journal of Choice Modelling, 2010, 3(2): 57-72.",
    "[4] Marley A A J, Louviere J J. Some probabilistic models of best, worst, and best–worst choices[J]. Journal of Mathematical Psychology, 2005, 49(6): 464-480.",
]


def _error(message):
    return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": message}


def _as_list(value):
    if value is None or value == "":
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple)):
        return list(value)
    return []


def _detect_mode(params):
    """
    检测数据模式。

    @return: "pro" (原始数据) 或 "summary" (汇总数据) 或 None
    """
    has_best_var = bool(params.get("best_variable"))
    has_worst_var = bool(params.get("worst_variable"))
    has_option_vars = bool(params.get("option_variables"))
    has_best_count = bool(params.get("best_count_variable"))
    has_worst_count = bool(params.get("worst_count_variable"))
    has_total_count = bool(params.get("total_count_variable"))
    has_index = bool(params.get("index_variable"))

    # Pro 模式：最重要 + 最不重要 + 选项变量
    if has_best_var and has_worst_var and has_option_vars:
        return "pro"

    # 汇总模式：最重要次数 + 最不重要次数 + 总次数 + 索引项
    if has_best_count and has_worst_count and has_total_count and has_index:
        return "summary"

    return None


def _compute_utility_stats(best_count, worst_count, total_count):
    """
    计算效用系数、标准误差、z 统计量、p 值。

    基于计数法 MaxDiff 的近似统计检验：
    - 效用系数 = 净得分 / 总出现次数
    - 标准误差 ≈ sqrt(p*(1-p)/n)，p = (Best+Worst)/(2*总次数)
    - z = 效用系数 / 标准误差
    - p 值从标准正态分布计算
    """
    net = best_count - worst_count
    utility = net / total_count if total_count > 0 else 0

    # 标准误差近似
    p_hat = (best_count + worst_count) / (2 * total_count) if total_count > 0 else 0.5
    p_hat = max(0.001, min(0.999, p_hat))  # 避免边界值
    se = np.sqrt(p_hat * (1 - p_hat) / total_count) if total_count > 0 else 1.0

    # z 统计量和 p 值
    z = utility / se if se > 0 else 0
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))  # 双侧检验

    return utility, se, z, p_value


def _run_maxdiff_pro(df, params, display_labels):
    """
    MaxDiff Pro 模式：原始数据。

    数据格式：每行=一个受访者，最重要/最不重要变量存储选项名，选项变量存储是否出现。
    """
    best_var = _as_list(params.get("best_variable", []))[0]
    worst_var = _as_list(params.get("worst_variable", []))[0]
    option_vars = _resolve_cols(df, _as_list(params.get("option_variables", [])))

    if len(option_vars) < 2:
        return _error("MaxDiff Pro 至少需要 2 个选项变量。")

    # 验证数据
    complete_mask = df[best_var].notna() & df[worst_var].notna()
    for var in option_vars:
        complete_mask = complete_mask & df[var].notna()
    valid_count = int(complete_mask.sum())
    data = df.loc[complete_mask]
    if len(data) < 1:
        return _error("有效样本不足，MaxDiff Pro 至少需要 1 条完整数据。")

    # 统计每个选项的 Best/Worst/出现次数
    best_counts = {}
    worst_counts = {}
    total_counts = {}
    for option in option_vars:
        option_name = str(option)
        best_counts[option_name] = int((data[best_var] == option_name).sum())
        worst_counts[option_name] = int((data[worst_var] == option_name).sum())
        total_counts[option_name] = len(data)  # 每个选项在每轮都出现

    # 计算效用系数、统计检验、偏好份额
    utilities = {}
    se_values = {}
    z_values = {}
    p_values = {}
    for opt in option_vars:
        opt_name = str(opt)
        utility, se, z, p = _compute_utility_stats(
            best_counts[opt_name], worst_counts[opt_name], total_counts[opt_name]
        )
        utilities[opt_name] = utility
        se_values[opt_name] = se
        z_values[opt_name] = z
        p_values[opt_name] = p

    # 偏好份额 = |效用系数| / Σ|效用系数| × 100%
    total_abs_utility = sum(abs(u) for u in utilities.values())
    preference_shares = {}
    if total_abs_utility > 0:
        for opt in option_vars:
            opt_name = str(opt)
            preference_shares[opt_name] = abs(utilities[opt_name]) / total_abs_utility * 100
    else:
        for opt in option_vars:
            preference_shares[str(opt)] = 100.0 / len(option_vars)

    # 生成结果表（对齐 SPSSPRO 格式）
    result_headers = ["属性", "效用系数", "标准误差", "z 统计量", "p 值", "最重要", "最不重要", "出现次数", "偏好份额"]
    result_rows = []
    for option in option_vars:
        option_name = str(option)
        p_val = p_values[option_name]
        p_str = _fmt(p_val, 3)
        if p_val < 0.001:
            p_str += "***"
        elif p_val < 0.01:
            p_str += "**"
        elif p_val < 0.05:
            p_str += "*"

        result_rows.append([
            display_labels.get(option_name, option_name),
            _fmt(utilities[option_name], 3),
            _fmt(se_values[option_name], 3),
            _fmt(z_values[option_name], 3),
            p_str,
            str(best_counts[option_name]),
            str(worst_counts[option_name]),
            str(total_counts[option_name]),
            _fmt(preference_shares[option_name], 3) + "%",
        ])

    return result_headers, result_rows, valid_count, len(option_vars)


def _run_maxdiff_summary(df, params, display_labels):
    """
    MaxDiff 汇总模式：已统计好的次数数据。

    数据格式：每行=一个选项，列=最重要次数、最不重要次数、总次数、索引项。
    """
    best_count_var = _as_list(params.get("best_count_variable", []))[0]
    worst_count_var = _as_list(params.get("worst_count_variable", []))[0]
    total_count_var = _as_list(params.get("total_count_variable", []))[0]
    index_var = _as_list(params.get("index_variable", []))[0]

    # 验证数据
    complete_mask = (
        df[best_count_var].notna() &
        df[worst_count_var].notna() &
        df[total_count_var].notna() &
        df[index_var].notna()
    )
    valid_count = int(complete_mask.sum())
    data = df.loc[complete_mask]
    if len(data) < 3:
        return _error("MaxDiff 汇总数据至少需要 3 个选项行。")

    # 提取数据
    best_counts = {}
    worst_counts = {}
    total_counts = {}
    option_names = []
    for _, row in data.iterrows():
        option_name = str(row[index_var])
        option_names.append(option_name)
        best_counts[option_name] = int(row[best_count_var])
        worst_counts[option_name] = int(row[worst_count_var])
        total_counts[option_name] = int(row[total_count_var])

    # 计算效用系数、统计检验、偏好份额
    utilities = {}
    se_values = {}
    z_values = {}
    p_values = {}
    for opt in option_names:
        utility, se, z, p = _compute_utility_stats(
            best_counts[opt], worst_counts[opt], total_counts[opt]
        )
        utilities[opt] = utility
        se_values[opt] = se
        z_values[opt] = z
        p_values[opt] = p

    # 偏好份额 = |效用系数| / Σ|效用系数| × 100%
    total_abs_utility = sum(abs(u) for u in utilities.values())
    preference_shares = {}
    if total_abs_utility > 0:
        for opt in option_names:
            preference_shares[opt] = abs(utilities[opt]) / total_abs_utility * 100
    else:
        for opt in option_names:
            preference_shares[opt] = 100.0 / len(option_names)

    # 生成结果表（对齐 SPSSPRO 格式）
    result_headers = ["属性", "效用系数", "标准误差", "z 统计量", "p 值", "最重要", "最不重要", "出现次数", "偏好份额"]
    result_rows = []
    for option in option_names:
        p_val = p_values[option]
        p_str = _fmt(p_val, 3)
        if p_val < 0.001:
            p_str += "***"
        elif p_val < 0.01:
            p_str += "**"
        elif p_val < 0.05:
            p_str += "*"

        result_rows.append([
            display_labels.get(option, option),
            _fmt(utilities[option], 3),
            _fmt(se_values[option], 3),
            _fmt(z_values[option], 3),
            p_str,
            str(best_counts[option]),
            str(worst_counts[option]),
            str(total_counts[option]),
            _fmt(preference_shares[option], 3) + "%",
        ])

    return result_headers, result_rows, valid_count, len(option_names)


def _preference_chart(rows):
    """生成偏好份额条形图。"""
    # 按偏好份额（第 9 列）降序排列
    ordered = sorted(rows, key=lambda row: float(row[8].rstrip("%")), reverse=True)
    return {
        "chartType": "metric_comparison",
        "title": "偏好份额",
        "data": {
            "metric": "偏好份额(%)",
            "labels": [row[0] for row in ordered],
            "values": [float(row[8].rstrip("%")) for row in ordered],
            "defaultMode": "bar",
            "displayModes": [
                {"value": "bar", "label": "柱形图"},
                {"value": "horizontalBar", "label": "条形图"},
            ],
            "axisLabels": {"x": "属性", "y": "偏好份额(%)"},
        },
    }


def run(df, params):
    """
    执行 MaxDiff（最大差异分析）。

    自动检测数据模式：
    - Pro 模式（原始数据）：最重要变量 + 最不重要变量 + 选项变量
    - 汇总模式：最重要次数 + 最不重要次数 + 总次数 + 索引项

    @param df: 当前数据集
    @param params: 根据模式不同，传入不同变量
    @return: 对齐 SPSSAU 的 MaxDiff 结果、图表和建议 sections
    """
    params = params or {}

    # 用题目名替代变量名显示
    variable_labels = params.get("variable_labels", {})
    display_labels = dict(variable_labels)

    # 检测模式
    mode = _detect_mode(params)
    if mode is None:
        return _error(
            "数据格式不正确。\n"
            "MaxDiff Pro（原始数据）需要：最重要变量 + 最不重要变量 + 选项变量\n"
            "MaxDiff（汇总数据）需要：最重要次数 + 最不重要次数 + 总次数 + 索引项"
        )

    # 执行对应模式
    if mode == "pro":
        result = _run_maxdiff_pro(df, params, display_labels)
        mode_label = "MaxDiff Pro"
    else:
        result = _run_maxdiff_summary(df, params, display_labels)
        mode_label = "MaxDiff"

    # 检查是否返回错误
    if isinstance(result, dict) and result.get("headers") == []:
        return result

    result_headers, result_rows, valid_count, option_count = result

    # 找出效用最高和最低的选项（按效用系数，第 2 列）
    top_item = max(result_rows, key=lambda row: float(row[1]))
    bottom_item = min(result_rows, key=lambda row: float(row[1]))

    # 统计显著属性数量
    significant_count = sum(1 for row in result_rows if "*" in row[4])
    # 计算偏好属性数量（效用系数为正）
    positive_count = sum(1 for row in result_rows if float(row[1]) > 0)
    negative_count = sum(1 for row in result_rows if float(row[1]) < 0)

    # 生成详细的结果分析
    analysis_content = (
        f"{mode_label} 分析完成，共 {option_count} 个属性，有效样本 N={valid_count}。\n\n"
        f"【整体结果概览】\n"
        f"在 {option_count} 个属性中，{positive_count} 个属性呈现正向偏好（效用系数>0），"
        f"{negative_count} 个属性呈现负向偏好（效用系数<0），"
        f"其中 {significant_count} 个属性的偏好达到统计显著水平（p<0.05）。\n\n"
        f"【最受偏好属性】\n"
        f"{top_item[0]} 的效用系数最高（{top_item[1]}），z 统计量为{top_item[3]}，"
        f"p 值{top_item[4]}，偏好份额为{top_item[8]}，是最受受访者偏好的属性。\n"
        f"该属性被选为'最重要'的次数为{top_item[5]}次，被选为'最不重要'的次数为{top_item[6]}次，"
        f"净偏好强度为{int(top_item[5]) - int(top_item[6])}。\n\n"
        f"【最不受偏好属性】\n"
        f"{bottom_item[0]} 的效用系数最低（{bottom_item[1]}），z 统计量为{bottom_item[3]}，"
        f"p 值{bottom_item[4]}，偏好份额为{bottom_item[8]}，是最不受受访者偏好的属性。\n"
        f"该属性被选为'最重要'的次数为{bottom_item[5]}次，被选为'最不重要'的次数为{bottom_item[6]}次，"
        f"净偏好强度为{int(bottom_item[5]) - int(bottom_item[6])}。\n\n"
        f"【统计指标解读】\n"
        f"● 效用系数（Utility Coefficient）：反映属性的相对偏好强度。正值表示该属性被选为最重要的次数多于最不重要，"
        f"负值则相反。效用系数的绝对值越大，表示偏好强度越强。\n"
        f"● 标准误差（Standard Error）：衡量效用系数估计的精确度。标准误差越小，估计越可靠。\n"
        f"● z 统计量（z-statistic）：效用系数与标准误差的比值，用于检验偏好是否显著不同于零。"
        f"|z|>1.96 表示 p<0.05，|z|>2.58 表示 p<0.01，|z|>3.29 表示 p<0.001。\n"
        f"● p 值（p-value）：统计显著性检验结果。p<0.05 表示该属性的偏好显著不同于随机选择，"
        f"***表示 p<0.001，**表示 p<0.01，*表示 p<0.05。\n"
        f"● 偏好份额（Preference Share）：各属性偏好强度的相对占比，所有属性的偏好份额之和为 100%。\n\n"
        f"【方法学说明】\n"
        f"MaxDiff（最大差异分析）属于离散选择实验（Discrete Choice Experiment）方法，"
        f"通过强制受访者在多个属性中选出最重要和最不重要的选项，获得比传统 Likert 量表更高的区分度。\n"
        f"本研究采用计数法（Counting Analysis）进行参数估计，适用于大样本快速分析。\n"
        f"若需要更精确的个体层面参数估计，可考虑使用 Hierarchical Bayes (HB) 或 Latent Class 模型。"
    )

    # 对齐 SPSSPRO MaxDiff 输出：属性估计结果表 + 偏好份额图 + 分析建议 + 参考文献
    sections = [
        _sec_table(
            f"{mode_label} 属性估计结果",
            result_headers,
            result_rows,
            description="上表格展示了 MaxDiff 属性结果及偏好份额，包括效用系数、标准误差、统计量、p 值、偏好份额等，用于评估用户对属性的偏好。\n"
                        "● 效用系数：正分意味着该属性被选为最重要的次数多于最不重要的次数；负分意味着该属性被选为最不重要的次数比最重要的次数要多。\n"
                        "● 偏好份额：直观展现了各个属性的重要程度，值越大说明该属性越重要。",
        ),
        _sec_charts(
            "偏好份额",
            [_preference_chart(result_rows)],
        ),
        _sec_advice(
            analysis_content,
            title="结果分析",
        ),
        _sec_refs(_REFS_MAXDIFF),
    ]

    return {
        "name": METHOD_META["label"],
        "headers": result_headers,
        "rows": result_rows,
        "description": f"{mode_label} 分析完成，共 {option_count} 个选项，有效样本 N={valid_count}。",
        "sections": sections,
    }
