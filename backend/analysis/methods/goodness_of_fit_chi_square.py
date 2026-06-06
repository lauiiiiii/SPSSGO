# -*- coding: utf-8 -*-
# 卡方拟合优度检验：只处理单个分类变量，期望比例由前端传入或按等比例兜底。
from backend.analysis.common import *

METHOD_KEY = "goodness_of_fit_chi_square"
METHOD_META = {
    "label": "卡方拟合优度检验",
    "category": "数据检验",
    "description": "判断期望频数与观察频数是否有显著差异",
    "order": 55,
    "slots": [
        {
            "key": "variable",
            "label": "变量",
            "type": "single",
            "accept": "categorical",
            "hint": "放入 1 个定类变量",
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


def _as_ratio_value(value):
    number = _safe_float(value)
    if not np.isfinite(number) or number < 0:
        return np.nan
    return number


def _expected_ratio_map(params):
    raw = params.get("expected_ratios") or params.get("expected_ratio") or {}
    if isinstance(raw, dict):
        return {str(key): _as_ratio_value(value) for key, value in raw.items()}
    if isinstance(raw, list):
        return {str(item.get("label")): _as_ratio_value(item.get("value")) for item in raw if isinstance(item, dict)}
    return {}


def _resolve_ratios(labels, params):
    ratio_map = _expected_ratio_map(params)
    ratios = np.array([ratio_map.get(str(label), np.nan) for label in labels], dtype=float)
    if not len(ratios) or not np.all(np.isfinite(ratios)) or np.any(ratios < 0) or ratios.sum() <= 0:
        ratios = np.repeat(1 / len(labels), len(labels))
    # 前端按百分比传 50/50，历史接口也允许按 0.5/0.5 传，这里统一归一化。
    ratios = ratios / ratios.sum()
    return ratios


def _result_chart(labels, observed, expected):
    return {
        "chartType": "metric_comparison",
        "title": "实际频数和期望频数",
        "data": {
            "metric": "频数",
            "labels": labels,
            "values": observed,
            "multiSeries": True,
            "metrics": {
                "实际频数": observed,
                "期望频数": expected,
            },
            "defaultMode": "bar",
            "displayModes": [
                {"value": "bar", "label": "柱形图"},
                {"value": "line", "label": "折线图"},
            ],
            "defaultShowDataLabels": True,
        },
    }


def _smart_text(variable, p_value):
    sig_text = "呈现显著性，拒绝原假设，因此数据的分布与预期相比有显著性差异" if p_value < 0.05 else "不呈现显著性，接受原假设，因此数据的分布与预期结果不呈现差异性"
    return f"卡方拟合优度检验的结果显示，基于变量{variable}，显著性P值为{_p_with_sig(p_value)}，水平上{sig_text}。"


def goodness_of_fit_chi_square(df, params):
    """
    卡方拟合优度检验。

    @param df: 数据 DataFrame
    @param params: variable 为分类变量，expected_ratios 可传 {类别: 百分比或比例}
    @return: SPSSPRO 风格拟合优度主表、频数对比图和结论说明
    """
    variable = params.get("variable", "")
    if variable not in df.columns:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "分类变量不存在。"}
    counts = df[variable].dropna().astype(str).value_counts().sort_index()
    if len(counts) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "至少需要 2 个类别。"}

    labels = [str(label) for label in counts.index.tolist()]
    observed = counts.values.astype(float)
    total = float(observed.sum())
    ratios = _resolve_ratios(labels, params)
    expected = total * ratios
    stat, p_val = chisquare(counts.values, f_exp=expected)
    actual_ratios = observed / total
    residuals = observed - expected
    p_text = _p_with_sig(float(p_val))
    rows = []
    for index, label in enumerate(labels):
        rows.append([
            label,
            str(int(observed[index])),
            _fmt(expected[index], 3),
            _fmt(actual_ratios[index], 3),
            _fmt(ratios[index], 3),
            _fmt(residuals[index], 3),
            _fmt(stat, 3) if index == 0 else "",
            p_text if index == 0 else "",
        ])
    result_section = _sec_table(
        "输出结果1：卡方拟合优度检验",
        ["项", "实际频数", "期望频数", "实际比例", "期望比例", "残差", "χ²", "P"],
        rows,
        note="注：****、***、**、* 分别代表0.1%、1%、5%、10%的显著性水平",
        description="上表展示本次拟合优度检验结果，包括频数、期望比例、统计量、卡方值、显著性P值等。",
    )
    result_section["headerRows"] = [
        [
            {"text": "", "rowspan": 2},
            {"text": "卡方拟合优度检验", "colspan": 7},
        ],
        ["项", "实际频数", "期望频数", "实际比例", "期望比例", "残差", "χ²", "P"],
    ]
    chart_section = _sec_charts(
        "输出结果2：期望频数图",
        [_result_chart(labels, observed.tolist(), expected.round(6).tolist())],
        "上图展示了各组期望比例与实际比例的频数柱状图，可直观观测实际与预期差异不大。",
    )
    sections = [
        _sec_table(
            "分析配置",
            ["项目", "内容"],
            [
                ["算法", METHOD_META["label"]],
                ["变量", variable],
                ["期望比例", "；".join(f"{label}:{_fmt(ratio, 3)}" for label, ratio in zip(labels, ratios))],
                ["有效样本量", str(int(total))],
                ["缺失值处理", "剔除缺失值后统计各类别频数"],
            ],
        ),
        result_section,
        _sec_advice(
            "1. 查看卡方拟合优度检验的P值是否呈现显著性。\n"
            "2. 若P值小于0.05，检验呈现显著性，即拒绝原假设，与预期相比有显著性差异。\n"
            "3. 若P值大于0.05，检验不呈显著性，即接受原假设，与预期结果一致，不存在明显差异。",
            title="分析步骤",
        ),
        _sec_smart(_smart_text(variable, float(p_val))),
        chart_section,
        _sec_refs(_REFS_GENERAL + [
            "[2] 王重，刘黎明. 拟合优度检验统计量的设定方法[J]. 统计与决策, 2010(5):154-156.",
        ]),
    ]
    return {
        "name": f"{METHOD_META['label']}_{variable}",
        "headers": result_section["headers"],
        "rows": rows,
        "description": _smart_text(variable, float(p_val)),
        "sections": sections,
    }


run = goodness_of_fit_chi_square
