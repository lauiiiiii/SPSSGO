# -*- coding: utf-8 -*-
# Cochran's Q 检验：只处理三个及以上相关二分类变量，输出主检验、频数百分比和公共堆叠图。
from backend.analysis.common import *

METHOD_KEY = "cochrans_q_test"
METHOD_META = {
    "label": "Cochran's Q检验",
    "category": "数据检验",
    "description": "比较三个及以上相关二分类变量的比例差异",
    "order": 60,
    "slots": [
        {
            "key": "variables",
            "label": "变量",
            "type": "multiple",
            "accept": "categorical",
            "min": 3,
            "hint": "放入三个及以上二分类变量",
        },
    ],
    "options": [],
    "param_builder": "direct",
}


def _p_with_sig(p_value):
    if p_value is None or not np.isfinite(p_value):
        return "—"
    if p_value < 0.001:
        return f"{_fmt(p_value, 3)}****"
    if p_value < 0.01:
        return f"{_fmt(p_value, 3)}***"
    if p_value < 0.05:
        return f"{_fmt(p_value, 3)}**"
    if p_value < 0.1:
        return f"{_fmt(p_value, 3)}*"
    return _fmt(p_value, 3)


def _binary_values(df, variables):
    values_by_var = {}
    for variable in variables:
        values = sorted(pd.Series(df[variable]).dropna().astype(str).unique().tolist(), key=str)
        if len(values) != 2:
            return {}, "类别数量必须为2项！"
        values_by_var[variable] = values
    return values_by_var, ""


def _normalize_binary_frame(df, variables, values_by_var):
    temp = df[variables].dropna().copy()
    if temp.empty:
        return temp
    normalized = pd.DataFrame(index=temp.index)
    for variable in variables:
        positive_label = values_by_var[variable][-1]
        normalized[variable] = (temp[variable].astype(str) == positive_label).astype(int)
    return normalized


def _frequency_rows(binary, variables, values_by_var):
    rows = []
    for variable in variables:
        n = len(binary)
        positive_count = int(binary[variable].sum())
        negative_count = int(n - positive_count)
        positive_label = values_by_var[variable][-1]
        negative_label = values_by_var[variable][0]
        rows.append([
            variable,
            str(positive_count),
            str(negative_count),
            f"{_fmt(positive_count / n * 100 if n else 0, 3)}%",
            f"{_fmt(negative_count / n * 100 if n else 0, 3)}%",
            positive_label,
            negative_label,
        ])
    return rows


def _result_table(variables, freq_rows, result, n):
    headers = ["变量", "1", "0", "样本量", "Cochran's Q", "df", "P"]
    rows = []
    for index, row in enumerate(freq_rows):
        suffix = []
        if index == 0:
            suffix = [
                {"text": str(n), "rowspan": len(freq_rows)},
                {"text": _fmt(result.statistic, 3), "rowspan": len(freq_rows)},
                {"text": str(len(variables) - 1), "rowspan": len(freq_rows)},
                {"text": _p_with_sig(float(result.pvalue)), "rowspan": len(freq_rows)},
            ]
        rows.append([row[0], row[1], row[2], *suffix])
    section = _sec_table(
        "输出结果1：Cochran's Q 检验",
        headers,
        rows,
        note="注：****、***、**、* 分别代表0.1%、1%、5%、10%的显著性水平",
        description=(
            "上表展示了本次模型检验的结果，包括样本量、频数百分比、自由度、Cochran's Q值、显著性P值。"
        ),
    )
    section["headerRows"] = [
        [
            {"text": "", "rowspan": 2},
            {"text": "频数百分比", "colspan": 2},
            {"text": "样本量", "rowspan": 2},
            {"text": "Cochran's Q", "rowspan": 2},
            {"text": "df", "rowspan": 2},
            {"text": "P", "rowspan": 2},
        ],
        ["1", "0"],
    ]
    return section


def _frequency_table(freq_rows):
    rows = [[row[0], row[1], row[2], row[3], row[4]] for row in freq_rows]
    section = _sec_table(
        "频数分析结果",
        ["变量", "1", "0", "1 百分比", "0 百分比"],
        rows,
        description="上表展示各二分类变量的频数和百分比，用于描述基础数据情况。",
    )
    section["inlineTitle"] = True
    return section


def _chart(freq_rows):
    labels = [row[0] for row in freq_rows]
    positive = [int(row[1]) for row in freq_rows]
    negative = [int(row[2]) for row in freq_rows]
    return {
        "chartType": "crosstab_distribution",
        "title": "频数分布对比图",
        "data": {
            "groupVariable": "变量",
            "xVariable": "类别",
            "groupLabels": labels,
            "xLabels": ["1", "0"],
            "matrix": [positive, negative],
            "total": sum(positive) + sum(negative),
            "percentBase": "column",
            "defaultMode": "stackedColumn",
            "defaultLabelMode": "percent",
            "displayModes": [
                {"value": "stackedColumn", "label": "堆积柱形图"},
                {"value": "column", "label": "柱形图"},
                {"value": "stackedBar", "label": "堆积条形图"},
                {"value": "bar", "label": "条形图"},
            ],
        },
    }


def _smart_text(variables, result):
    p_value = float(result.pvalue)
    sig = p_value < 0.05
    return (
        f"Cochran's Q检验的结果显示，基于变量，{', '.join(variables)}，"
        f"整体的显著性P值为{_p_with_sig(p_value)}，水平上{'呈现显著性' if sig else '不呈现显著性'}，"
        f"{'拒绝' if sig else '不能拒绝'}原假设，因此说明数据总体{'存在' if sig else '不存在'}差异性。"
    )


def run(df, params):
    """
    Cochran's Q 检验。

    @param df: 数据 DataFrame
    @param params: variables 为三个及以上二分类变量
    @return: SPSSAU/SPSSPRO 风格主检验表、频数百分比表、堆叠分布图和结论说明
    """
    variables = _resolve_cols(df, params.get("variables", []))
    if len(variables) < 3:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "Cochran's Q 检验至少需要 3 个二分类变量。"}

    values_by_var, error = _binary_values(df, variables)
    if error:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": error}

    binary = _normalize_binary_frame(df, variables, values_by_var)
    if len(binary) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效样本不足。"}

    result = cochrans_q(binary.to_numpy())
    freq_rows = _frequency_rows(binary, variables, values_by_var)
    result_section = _result_table(variables, freq_rows, result, len(binary))
    chart_section = _sec_charts(
        "输出结果2：频数分析堆叠图",
        [_chart(freq_rows)],
        "上图以堆叠方式展示各二分类变量的频数和百分比情况。",
    )
    sections = [
        _sec_table(
            "分析配置",
            ["项目", "内容"],
            [
                ["算法", METHOD_META["label"]],
                ["变量", "、".join(variables)],
                ["有效样本量", str(len(binary))],
                ["缺失值处理", "任一分析变量缺失时剔除整行样本"],
            ],
        ),
        _sec_advice(
            "Cochran's Q检验用于研究多组相关样本(多个关联样本)的差异性。\n"
            "第一：描述基本数据情况；\n"
            "第二：描述Cochran's Q检验结果，分析是否存在差异；\n"
            "第三：对分析进行总结。",
            title="分析步骤",
        ),
        result_section,
        _sec_smart(_smart_text(variables, result)),
        _frequency_table(freq_rows),
        chart_section,
        _sec_refs(_REFS_GENERAL + [
            "[2] MERLE W T, SARAM B. Note on the Cochran Q Test[J]. Journal of the American Statistical Association, 1970, 65(329):155-160.",
        ]),
    ]
    return {
        "name": f"Cochran's Q检验_{'_'.join(variables[:3])}",
        "headers": result_section["headers"],
        "rows": result_section["rows"],
        "description": _smart_text(variables, result),
        "sections": sections,
    }
