# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "pearson_correlation"
METHOD_META = {'label': '相关性分析',
 'category': '问卷分析包',
 'description': '分析两个或多个定量变量之间的线性相关程度',
 'order': 40,
 'slots': [{'key': 'variables',
            'label': '分析变量',
            'type': 'multiple',
            'accept': 'numeric',
            'min': 2,
            'hint': '放入需要分析相关性的变量（至少2个）'}],
 'options': [{'key': 'correlation_method',
              'label': '相关系数',
              'choices': ['Pearson相关系数', 'Spearman相关系数', 'Kendall相关系数'],
              'default': 'Pearson相关系数'}],
 'param_builder': 'direct'}

def pearson_correlation(df, params):
    """
    相关系数分析，含相关系数矩阵、显著性和热力图。

    @param df: 数据 DataFrame
    @param params: 包含 variables 的参数字典
    @return: 含 sections 的结果字典
    """
    variables = _resolve_cols(df, params.get("variables", []))
    if len(variables) < 2:
        return {"name": "相关性分析", "headers": [], "rows": [], "description": "需要至少2个变量。"}

    method_configs = {
        "Pearson相关系数": {
            "label": "Pearson相关系数",
            "analysis_name": "Pearson积差相关分析",
            "symbol": "r",
            "func": pearsonr,
            "description": "Pearson相关分析用于衡量两个定量变量之间的线性相关程度",
        },
        "Spearman相关系数": {
            "label": "Spearman相关系数",
            "analysis_name": "Spearman等级相关分析",
            "symbol": "ρ",
            "func": spearmanr,
            "description": "Spearman等级相关是一种非参数相关分析方法，适用于顺序变量或不满足正态分布假设的数据",
        },
        "Kendall相关系数": {
            "label": "Kendall相关系数",
            "analysis_name": "Kendall相关分析",
            "symbol": "τ",
            "func": kendalltau,
            "description": "Kendall相关分析是一种非参数相关分析方法，适用于顺序变量或样本量较小的排序关系判断",
        },
    }
    method_key = params.get("correlation_method") or "Pearson相关系数"
    method_config = method_configs.get(method_key, method_configs["Pearson相关系数"])
    corr_func = method_config["func"]

    corr_m, p_m = {}, {}
    for v1 in variables:
        corr_m[v1], p_m[v1] = {}, {}
        for v2 in variables:
            s1 = pd.to_numeric(df[v1], errors="coerce")
            s2 = pd.to_numeric(df[v2], errors="coerce")
            mask = s1.notna() & s2.notna()
            if mask.sum() < 3 or s1[mask].nunique() < 2 or s2[mask].nunique() < 2:
                r, p = np.nan, np.nan
            else:
                r, p = corr_func(s1[mask], s2[mask])
            corr_m[v1][v2] = r
            p_m[v1][v2] = p

    headers = ["变量", "M", "SD", "统计量"] + variables

    def build_matrix_rows(display_mode="all"):
        rows = []
        for row_index, v in enumerate(variables):
            s = pd.to_numeric(df[v], errors="coerce").dropna()
            corr_row = [
                {"text": v, "rowspan": 2},
                {"text": _fmt(s.mean()), "rowspan": 2},
                {"text": _fmt(s.std()), "rowspan": 2},
                "相关系数",
            ]
            p_row = ["P值"]
            for col_index, v2 in enumerate(variables):
                hidden = (
                    (display_mode == "upper" and col_index < row_index)
                    or (display_mode == "lower" and col_index > row_index)
                )
                if hidden:
                    corr_row.append("")
                    p_row.append("")
                elif v == v2:
                    corr_row.append("1")
                    p_row.append("—")
                else:
                    corr_row.append(_fmt(corr_m[v][v2]) + _sig(p_m[v][v2]) if pd.notna(corr_m[v][v2]) else "—")
                    p_row.append(_fmt(p_m[v][v2]) if pd.notna(p_m[v][v2]) else "—")
            rows.append(corr_row)
            rows.append(p_row)
        return rows

    rows = build_matrix_rows("all")
    display_modes = [
        {"key": "all", "label": "全显示(默认)", "rows": rows},
        {"key": "upper", "label": "上三角", "rows": build_matrix_rows("upper")},
        {"key": "lower", "label": "下三角", "rows": build_matrix_rows("lower")},
    ]

    def build_heatmap_values(display_mode="all"):
        values = []
        for row_index, v1 in enumerate(variables):
            row = []
            for col_index, v2 in enumerate(variables):
                hidden = (
                    (display_mode == "upper" and col_index < row_index)
                    or (display_mode == "lower" and col_index > row_index)
                )
                if hidden:
                    row.append(None)
                elif v1 == v2:
                    row.append(1)
                else:
                    row.append(round(float(corr_m[v1][v2]), 4) if pd.notna(corr_m[v1][v2]) else None)
            values.append(row)
        return values

    heatmap_data = {
        "rowLabels": variables,
        "colLabels": variables,
        "values": build_heatmap_values("all"),
        "displayModes": [
            {"key": "all", "label": "全显示(默认)", "values": build_heatmap_values("all")},
            {"key": "upper", "label": "上三角", "values": build_heatmap_values("upper")},
            {"key": "lower", "label": "下三角", "values": build_heatmap_values("lower")},
        ],
        "defaultDisplayMode": "all",
    }

    descs = []
    for v1, v2 in combinations(variables, 2):
        r = corr_m[v1][v2]
        p = p_m[v1][v2]
        if pd.isna(r) or pd.isna(p):
            descs.append(f"{v1}与{v2}样本不足或变量为常量，无法计算{method_config['label']}。")
            continue
        direction = "正" if r > 0 else "负"
        if p < 0.05:
            descs.append(f"{v1}与{v2}之间呈显著{direction}相关（{method_config['symbol']}={_fmt(r, 3)}，{_p_expr(p)}）")
        else:
            descs.append(f"{v1}与{v2}之间的相关未达到统计学显著水平（{method_config['symbol']}={_fmt(r, 3)}，{_p_expr(p)}）")

    note = "注：*p<0.05，**p<0.01，***p<0.001。"
    desc = f"采用{method_config['analysis_name']}，结果如表所示。{'；'.join(descs)}。{note}"

    sections = []
    matrix_section = _sec_table("相关系数矩阵", headers, rows, note=note,
                                description=f"每个变量第一行展示{method_config['label']}及显著性标记，第二行展示对应 P 值；对角线相关系数为1。")
    matrix_section["displayModeTitle"] = ""
    matrix_section["displayModes"] = display_modes
    matrix_section["defaultDisplayMode"] = "all"
    sections.append(matrix_section)
    sections.append(_sec_charts(
        f"{method_config['label']}热力图",
        [{"chartType": "correlation_heatmap", "title": f"{method_config['label']}热力图", "data": heatmap_data}],
        "颜色越深表示相关系数绝对值越大；可切换全显示、上三角或下三角。"
    ))
    advice = (
        f"{method_config['description']}；\n"
        "第一：相关系数绝对值≥0.8为高度相关，0.5~0.8为中等相关，0.3~0.5为低相关，<0.3为微弱相关；\n"
        "第二：p<0.05表示相关系数具有统计学意义；\n"
        "第三：相关不等于因果，需结合专业知识和其他分析方法进行推断。"
    )
    sections.append(_sec_advice(advice))
    smart = f"采用{method_config['analysis_name']}。{'；'.join(descs)}。"
    sections.append(_sec_smart(smart))
    sections.append(_sec_refs(_REFS_CORRELATION))

    return {"name": "相关性分析", "headers": headers, "rows": rows, "description": desc, "sections": sections}

run = pearson_correlation
