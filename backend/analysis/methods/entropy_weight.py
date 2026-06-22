# -*- coding: utf-8 -*-
# 权重分析统一入口：按 SPSSAU 的"分析方法"下拉分派 AHP、熵值法和优序图法。
# 老任务没传 analysis_method 时仍走原熵权法，别把历史结果口径改炸。
from backend.analysis.common import *


def inject_metadata(metadata_map, params):
    """注入变量标题，让输出用题目名而非变量名显示。"""
    enriched = dict(params or {})
    variables = _as_list(enriched.get("variables", []))
    enriched["variable_labels"] = {
        variable: metadata_map.get(variable, {}).get("display_name") or variable
        for variable in variables
    }
    return enriched

METHOD_KEY = "entropy_weight"
METHOD_META = {
    "label": "权重分析",
    "category": "高级问卷分析包",
    "description": "支持 AHP 权重、熵值法和优序图法计算指标权重",
    "order": 160,
    "aliases": ["权重分析(熵权法)", "熵权法", "熵值法", "AHP权重", "优序图法"],
    "slots": [
        {
            "key": "variables",
            "label": "指标变量",
            "type": "multiple",
            "accept": "numeric",
            "min": 2,
            "hint": "放入综合评价指标",
        }
    ],
    "options": [
        {
            "key": "analysis_method",
            "label": "分析方法",
            "choices": [
                {"value": "ahp", "label": "AHP权重"},
                {"value": "entropy", "label": "熵值法"},
                {"value": "ranking", "label": "优序图法"},
            ],
            "default": "ranking",
        },
    ],
    "param_builder": "direct",
}

ANALYSIS_METHOD_MAP = {
    "ahp": "ahp",
    "ahp_weight": "ahp",
    "AHP权重": "ahp",
    "AHP": "ahp",
    "entropy": "entropy",
    "entropy_weight": "entropy",
    "熵权法": "entropy",
    "熵值法": "entropy",
    "ranking": "ranking",
    "ranking_method": "ranking",
    "优序图": "ranking",
    "优序图法": "ranking",
}
ANALYSIS_METHOD_LABELS = {
    "ahp": "AHP权重",
    "entropy": "熵值法",
    "ranking": "优序图法",
}

_REFS_ENTROPY = _REFS_GENERAL + [
    "[3] Shannon C E. A mathematical theory of communication[J]. Bell System Technical Journal, 1948, 27(3): 379-423.",
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


def _selected_analysis_method(params):
    # 老版本只有“权重分析(熵权法)”入口，没有 analysis_method，必须继续默认熵权法。
    if "analysis_method" not in params or params.get("analysis_method") in (None, ""):
        return "entropy"
    raw = str(params.get("analysis_method")).strip()
    return ANALYSIS_METHOD_MAP.get(raw, "")


def _with_weight_analysis_name(result, method_key, variables=None):
    if not isinstance(result, dict):
        return result
    result["name"] = METHOD_META["label"]
    method_label = ANALYSIS_METHOD_LABELS.get(method_key, method_key)
    if result.get("description"):
        result["description"] = f"{method_label}：{result['description']}"
    # 对齐 SPSSAU：不再注入"算法配置"section
    return result


def _weight_chart(rows):
    ordered = sorted(rows, key=lambda row: float(row[3]), reverse=True)
    return {
        "chartType": "metric_comparison",
        "title": "权重值",
        "data": {
            "metric": "权重(%)",
            "labels": [row[0] for row in ordered],
            "values": [float(row[3]) for row in ordered],
            "defaultMode": "bar",
            "displayModes": [
                {"value": "bar", "label": "柱形图"},
                {"value": "horizontalBar", "label": "条形图"},
            ],
            "axisLabels": {"x": "指标", "y": "权重(%)"},
        },
    }


def _run_ahp_weight(df, params, variables):
    from backend.analysis.methods import ahp_simplified

    next_params = {
        "input_mode": "data_auto",
        "variables": variables,
        "variable_labels": params.get("variable_labels", {}),
        "weight_method": params.get("weight_method") or "sum_product",
        "include_missing_analysis": params.get("include_missing_analysis", False),
    }
    result = ahp_simplified.run(df, next_params)
    return _with_weight_analysis_name(result, "ahp", variables)


def _run_ranking_weight(df, params, variables):
    from backend.analysis.methods import ranking_method

    result = ranking_method.run(df, {
        "variables": variables,
        "variable_labels": params.get("variable_labels", {}),
    })
    return _with_weight_analysis_name(result, "ranking", variables)


def _run_entropy_weight(df, params, variables):
    """
    执行熵权法权重分析。

    @param df: 当前数据集，样本为行、指标为列
    @param params: variables、analysis_method、variable_labels
    @return: 对齐 SPSSAU 的熵权法结果、图表和描述统计 sections
    """
    data = df[variables].apply(pd.to_numeric, errors="coerce").dropna()
    if len(data) < 2:
        return _error("有效样本不足，熵权法至少需要 2 条完整样本。")

    normalized = data.copy()
    for variable in variables:
        series = normalized[variable]
        range_value = series.max() - series.min()
        if range_value == 0:
            normalized[variable] = 1.0
        else:
            normalized[variable] = (series - series.min()) / range_value + 1e-12

    proportion = normalized.div(normalized.sum(axis=0), axis=1).replace(0, 1e-12)
    sample_count = len(proportion)
    k = 1.0 / np.log(sample_count)
    entropy = -k * (proportion * np.log(proportion)).sum(axis=0)
    divergence = 1 - entropy
    if float(divergence.sum()) == 0:
        weights = pd.Series([1 / len(variables)] * len(variables), index=variables)
    else:
        weights = divergence / divergence.sum()

    # 用题目名替代变量名显示
    variable_labels = params.get("variable_labels", {})
    display_labels = {v: variable_labels.get(v, v) for v in variables}

    headers = ["项", "熵值", "差异系数", "权重(%)"]
    rows = [
        [display_labels[variable], _fmt(entropy[variable], 4), _fmt(divergence[variable], 4), _fmt(weights[variable] * 100, 3)]
        for variable in variables
    ]
    top_weight = max(rows, key=lambda row: float(row[3]))

    # 对齐 SPSSAU 熵值法输出：权重计算结果 + 分析建议 + 权重图 + 参考文献
    sections = [
        _sec_table(
            "权重计算结果",
            headers,
            rows,
            description="熵值越低、差异系数越高，通常意味着该指标提供的信息量越大，权重也越高。",
        ),
        _sec_advice(
            f"熵权法对 {len(rows)} 个指标进行客观赋权，有效样本量 N={len(data)}。"
            f"结果显示，{top_weight[0]} 的权重最高（{top_weight[3]}%），说明该指标在当前样本中的离散程度最大，"
            f"提供的信息量相对更多。"
            f"\n第一：熵权法属于客观赋权方法，权重反映的是样本数据的离散程度，不等同于理论或业务上的主观重要性；\n"
            f"第二：当前实现按正向指标进行标准化，若存在逆向指标请先在数据处理环节完成方向统一；\n"
            f"第三：熵权法更适合客观赋权场景，若研究需要主观权重，可结合 AHP 等方法联合使用。",
            title="分析建议",
        ),
        _sec_charts(
            "权重值",
            [_weight_chart(rows)],
        ),
        _sec_refs(_REFS_ENTROPY),
    ]

    return {
        "name": METHOD_META["label"],
        "headers": headers,
        "rows": rows,
        "description": f"熵权分析完成，共计算 {len(variables)} 个指标的客观权重，有效样本量 N={len(data)}。",
        "sections": sections,
    }


def run(df, params):
    """
    执行权重分析统一入口。

    @param df: 当前数据集，样本为行、指标为列
    @param params: variables、analysis_method；旧任务未传 analysis_method 时默认熵权法
    @return: 所选权重分析方法的结果 sections
    """
    params = params or {}
    variables = _resolve_cols(df, _as_list(params.get("variables", [])))
    if len(variables) < 2:
        return _error("权重分析至少需要 2 个数值型指标。")

    analysis_method = _selected_analysis_method(params)
    if not analysis_method:
        return _error("分析方法不支持，请选择 AHP权重、熵值法或优序图法。")
    if analysis_method == "ahp":
        return _run_ahp_weight(df, params, variables)
    if analysis_method == "ranking":
        return _run_ranking_weight(df, params, variables)
    return _run_entropy_weight(df, params, variables)
