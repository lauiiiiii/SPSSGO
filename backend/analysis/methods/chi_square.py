# -*- coding: utf-8 -*-
# 卡方检验：负责一个分组变量 X 对多个定类变量 Y 的检验、热力图和效应量输出。
from backend.analysis.common import *

METHOD_KEY = "chi_square"
METHOD_META = {
    "label": "卡方检验",
    "category": "差异对比分析包",
    "description": "用于探索多组定类变量之间的差异性分析",
    "slots": [
        {
            "key": "var1",
            "label": "变量X",
            "prefixLabel": "分组",
            "type": "single",
            "accept": "categorical",
            "hint": "放入 1 个定类分组变量",
        },
        {
            "key": "variables",
            "label": "变量Y",
            "type": "multiple",
            "accept": "categorical",
            "min": 1,
            "hint": "放入 1 个或多个定类分析变量",
        },
    ],
    "options": [
        {
            "key": "test_type",
            "label": "类型",
            "choices": ["Pearson卡方检验", "Yates校正卡方检验", "Fisher精确检验", "自动卡方检验"],
            "default": "Pearson卡方检验",
        },
    ],
    "param_builder": "direct",
}
METADATA_INJECTOR = "cross_labels"


def _analysis_variables(params):
    x_var = params.get("var1") or params.get("group_var") or ""
    variables = params.get("variables") or []
    if isinstance(variables, str):
        variables = [variables]
    legacy_y = params.get("var2") or ""
    if legacy_y and legacy_y not in variables:
        variables = [legacy_y] + list(variables)

    unique_variables = []
    for variable in variables:
        if variable and variable != x_var and variable not in unique_variables:
            unique_variables.append(variable)
    return x_var, unique_variables


def _label_for(labels, value):
    return labels.get(str(value), str(value))


def _p_with_sig(p):
    try:
        value = float(p)
    except (TypeError, ValueError):
        return "—"
    if not np.isfinite(value):
        return "—"
    return f"{_fmt(value, 3)}{_chi_sig(value)}"


def _chi_sig(p):
    # 卡方报告按截图口径展示：***=1%，**=5%，*=10%，别套用全局 p<0.001 规则。
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.1:
        return "*"
    return ""


def _selected_test_type(params):
    raw = str(params.get("test_type") or params.get("type") or params.get("method") or "")
    if raw in {"yates", "Yates校正卡方检验", "校正卡方检验"}:
        return "yates", "yates校正卡方检验"
    if raw in {"fisher", "Fisher精确检验", "Fisher精确卡方检验"}:
        return "fisher", "fisher精确检验"
    if raw in {"auto", "自动卡方检验"}:
        return "auto", "自动卡方检验"
    return "pearson", "pearson卡方检验"


def _safe_chi_square(ct, correction=False):
    if ct.shape[0] < 2 or ct.shape[1] < 2:
        return np.nan, np.nan, 0, np.full(ct.shape, np.nan)
    try:
        return chi2_contingency(ct, correction=correction)
    except Exception:
        return np.nan, np.nan, 0, np.full(ct.shape, np.nan)


def _lambda_for_rows(ct):
    n_total = int(ct.to_numpy().sum())
    if n_total <= 0:
        return np.nan
    row_sums = ct.sum(axis=1)
    without_x = n_total - int(row_sums.max())
    if without_x <= 0:
        return 0.0
    with_x = int(sum(ct[col].sum() - ct[col].max() for col in ct.columns))
    return max(0.0, (without_x - with_x) / without_x)


def _effect_level(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "—"
    if not np.isfinite(number):
        return "—"
    if number >= 0.5:
        return "较强"
    if number >= 0.3:
        return "中等"
    return "较弱"


def _test_result(ct, params):
    requested_key, requested_label = _selected_test_type(params)
    pearson_chi2, pearson_p, dof, expected = _safe_chi_square(ct, correction=False)
    test_key = requested_key
    test_label = requested_label
    chi2 = pearson_chi2
    p_value = pearson_p

    is_2x2 = ct.shape == (2, 2)
    if requested_key == "auto":
        low_expected = np.isfinite(expected).all() and (expected < 5).any()
        test_key = "fisher" if is_2x2 and low_expected else "pearson"
        test_label = "fisher精确检验" if test_key == "fisher" else "pearson卡方检验"

    if test_key == "yates":
        if is_2x2:
            chi2, p_value, dof, expected = _safe_chi_square(ct, correction=True)
        else:
            test_label = "pearson卡方检验"
    elif test_key == "fisher":
        if is_2x2:
            try:
                _, p_value = stats.fisher_exact(ct.to_numpy())
                chi2 = np.nan
                dof = 1
            except Exception:
                p_value = np.nan
                chi2 = np.nan
        else:
            test_label = "pearson卡方检验"

    n_total = int(ct.to_numpy().sum())
    phi = np.sqrt(pearson_chi2 / n_total) if n_total > 0 and np.isfinite(float(pearson_chi2)) else np.nan
    min_dim = min(ct.shape[0], ct.shape[1]) - 1
    cramers_v = np.sqrt(pearson_chi2 / (n_total * min_dim)) if n_total > 0 and min_dim > 0 and np.isfinite(float(pearson_chi2)) else np.nan
    contingency = np.sqrt(pearson_chi2 / (pearson_chi2 + n_total)) if n_total > 0 and np.isfinite(float(pearson_chi2)) else np.nan
    lambda_value = _lambda_for_rows(ct)
    return {
        "chi2": chi2,
        "pearson_chi2": pearson_chi2,
        "p": p_value,
        "dof": dof,
        "expected": expected,
        "method": test_label,
        "n": n_total,
        "phi": phi,
        "cramers_v": cramers_v,
        "contingency": contingency,
        "lambda": lambda_value,
    }


def _build_pair(df, x_var, y_var, params, x_values, x_labels):
    labels_by_variable = params.get("labels_by_variable") or {}
    y_labels = labels_by_variable.get(y_var) or params.get("var2_labels", {})
    temp = df[[x_var, y_var]].dropna()
    if temp.empty:
        return None

    ct = pd.crosstab(temp[y_var], temp[x_var])
    ct = ct.reindex(columns=x_values, fill_value=0)
    result = _test_result(ct, params)
    y_values = list(ct.index)
    y_level_labels = [_label_for(y_labels, value) for value in y_values]

    rows = []
    for row_index, value in enumerate(y_values):
        row_total = int(ct.loc[value].sum())
        prefix = [{"text": y_var, "rowspan": len(y_values)}] if row_index == 0 else []
        stat_suffix = []
        if row_index == 0:
            stat_suffix = [
                {"text": result["method"], "rowspan": len(y_values)},
                {"text": _fmt(result["chi2"], 3), "rowspan": len(y_values)},
                {"text": _p_with_sig(result["p"]), "rowspan": len(y_values)},
            ]
        rows.append([
            *prefix,
            _label_for(y_labels, value),
            *[str(int(ct.loc[value, col])) for col in ct.columns],
            str(row_total),
            *stat_suffix,
        ])
    rows.append([
        {"text": "合计", "colspan": 2},
        *[str(int(value)) for value in ct.sum(axis=0).tolist()],
        str(result["n"]),
        "",
        "",
        "",
    ])

    chart = {
        "chartType": "crosstab_distribution",
        "title": f"{x_var}-{y_var}热力图",
        "varName": y_var,
        "data": {
            "groupVariable": x_var,
            "xVariable": y_var,
            "groupLabels": x_labels,
            "xLabels": y_level_labels,
            "matrix": [[int(ct.loc[row, col]) for col in ct.columns] for row in ct.index],
            "total": result["n"],
            "percentBase": "column",
            "defaultMode": "heatmap",
            "defaultLabelMode": "count",
        },
    }
    smart = (
        f"{result['method']}分析的结果显示，基于{x_var}和{y_var}，"
        f"显著性P值为{_p_with_sig(result['p'])}，"
        f"水平上{'呈现显著性' if np.isfinite(float(result['p'])) and result['p'] < 0.05 else '未呈现显著性'}，"
        f"{'拒绝' if np.isfinite(float(result['p'])) and result['p'] < 0.05 else '接受'}原假设，"
        f"因此{x_var}和{y_var}数据{'存在' if np.isfinite(float(result['p'])) and result['p'] < 0.05 else '不存在'}显著性差异。"
    )
    return {
        "rows": rows,
        "chart": chart,
        "smart": smart,
        "effect_row": [
            y_var,
            _fmt(result["phi"], 3),
            _fmt(result["cramers_v"], 3),
            _fmt(result["contingency"], 3),
            _fmt(result["lambda"], 3),
        ],
        "cramers_v": result["cramers_v"],
    }


def chi_square_test(df, params):
    """
    卡方检验。

    @param df: 数据 DataFrame
    @param params: 包含 var1 和 variables/var2 的参数字典
    @return: 含检验表、热力图、效应量和智能分析的结果字典
    """
    x_var, variables = _analysis_variables(params)
    if x_var not in df.columns or not variables:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "请放入 1 个变量X 和至少 1 个变量Y。"}

    valid_variables = [variable for variable in variables if variable in df.columns]
    if not valid_variables:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "变量不存在。"}

    x_var_labels = params.get("var1_labels") or params.get("group_labels", {})
    x_values = sorted(pd.Series(df[x_var]).dropna().unique().tolist(), key=lambda value: str(value))
    x_labels = [_label_for(x_var_labels, value) for value in x_values]
    header_rows = [
        [
            {"text": "题目", "rowspan": 2},
            {"text": "名称", "rowspan": 2},
            {"text": x_var, "colspan": len(x_labels)},
            {"text": "总计", "rowspan": 2},
            {"text": "检验方法", "rowspan": 2},
            {"text": "X²", "rowspan": 2},
            {"text": "P", "rowspan": 2},
        ],
        x_labels,
    ]
    headers = ["题目", "名称", *x_labels, "总计", "检验方法", "X²", "P"]
    table_rows = []
    charts = []
    effect_rows = []
    smart_messages = []
    for variable in valid_variables:
        pair = _build_pair(df, x_var, variable, params, x_values, x_labels)
        if not pair:
            smart_messages.append(f"基于{x_var}和{variable}的有效样本不足，无法完成卡方检验。")
            continue
        table_rows.extend(pair["rows"])
        charts.append(pair["chart"])
        effect_rows.append(pair["effect_row"])
        smart_messages.append(pair["smart"])

    if not table_rows:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效样本不足，无法完成卡方检验。"}

    table_section = _sec_table(
        "输出结果1：卡方检验分析结果",
        headers,
        table_rows,
        note="注：***、**、*分别代表1%、5%、10%的显著性水平",
        description=(
            "上表展示了模型检验的结果，包括数据的频数、卡方值、显著性P值。"
            "分析模型是否呈现出显著性(P<0.05)。若呈现显著性，拒绝原假设，说明各样本之间存在显著性差异。"
        ),
    )
    table_section["headerRows"] = header_rows

    effect_section = _sec_table(
        "输出结果3：效应量化分析",
        ["字段名/分析项", "Phi", "Crammer's V", "列联系数", "lambda"],
        effect_rows,
        description="上表展示了效应量化分析的结果，包括phi、Crammer's V、列联系数、lambda，用于分析样本的相关程度。",
    )
    charts_section = _sec_charts(
        "输出结果2：卡方交叉热力图",
        charts,
        description="上图展示了热力图的形式展示了交叉列联表的值，主要通过颜色深浅去表示值的大小。",
    )

    advice = (
        "1. 分析卡方检验是否呈现显著性(P<0.05)。\n"
        "2. 若呈现显著性，具体根据类别的差异百分比进行描述。\n"
        "3. 若呈现显著性，可接着根据效应指标对差异进行深入量化分析。"
    )
    effect_smart = []
    for row in effect_rows:
        effect_smart.append(
            f"效应量化分析的结果显示，分析项：{row[0]}\n"
            f"Crammer's V值为{row[2]}，因此{row[0]}和{x_var}的差异程度为{_effect_level(row[2])}程度差异。"
        )
    sections = [
        _sec_advice(advice, title="详细结论"),
        table_section,
        _sec_smart("\n".join(smart_messages)),
        charts_section,
        effect_section,
        _sec_smart("\n".join(effect_smart)),
        _sec_refs(_REFS_GENERAL),
    ]

    name_suffix = f"{x_var} × " + "、".join(valid_variables)
    return {
        "name": f"卡方检验：{name_suffix}",
        "headers": headers,
        "rows": table_rows,
        "description": "\n".join(smart_messages),
        "sections": sections,
    }


run = chi_square_test
