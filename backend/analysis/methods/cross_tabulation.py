# -*- coding: utf-8 -*-
# 列联交叉分析：支持 1 个分组变量对应多个 X 变量，兼容旧 var1/var2 入参。
from backend.analysis.common import *

METHOD_KEY = "cross_tabulation"
METHOD_META = {
    "label": "卡方（交叉）分析",
    "category": "常用方法",
    "description": "用于探索多组变量之间交叉列联分布和关联强度",
    "order": 20,
    "slots": [
        {
            "key": "group_var",
            "label": "变量",
            "prefixLabel": "分组",
            "type": "single",
            "accept": "any",
            "hint": "放入 1 个分组变量",
        },
        {
            "key": "variables",
            "label": "变量X",
            "type": "multiple",
            "accept": "any",
            "min": 1,
            "hint": "放入 1 个或多个需要交叉分析的 X 变量",
        },
    ],
    "options": [
        {
            "key": "percent_base",
            "label": "占比口径",
            "choices": ["百分数(按列)", "百分数(按行)"],
            "default": "百分数(按列)",
        },
    ],
    "param_builder": "direct",
}
METADATA_INJECTOR = "cross_labels"


def _cross_variables(params):
    group_var = params.get("group_var") or params.get("var1", "")
    variables = params.get("variables") or []
    if isinstance(variables, str):
        variables = [variables]
    legacy_var = params.get("var2", "")
    if legacy_var and legacy_var not in variables:
        variables = [legacy_var] + list(variables)
    unique_variables = []
    for value in variables:
        if value and value != group_var and value not in unique_variables:
            unique_variables.append(value)
    return group_var, unique_variables


def _label_for(labels, value):
    return labels.get(str(value), str(value))


def _p_with_sig(p):
    if p is None:
        return "—"
    try:
        value = float(p)
    except (TypeError, ValueError):
        return "—"
    if not np.isfinite(value):
        return "—"
    return f"{_fmt(value)}{_sig(value)}"


def _percent_base(params):
    raw = str(params.get("percent_base") or params.get("percentBase") or "")
    if raw in ("row", "按行", "百分数(按行)", "行百分比", "行占比"):
        return "row"
    return "column"


def _percent_base_label(percent_base):
    return "行百分比" if percent_base == "row" else "列百分比"


def _chi_square_result(ct):
    if ct.shape[0] < 2 or ct.shape[1] < 2:
        return np.nan, np.nan, 0, np.full(ct.shape, np.nan)
    try:
        return chi2_contingency(ct)
    except Exception:
        return np.nan, np.nan, 0, np.full(ct.shape, np.nan)


def _build_cross_pair(df, group_var, x_var, params, group_values, percent_base):
    group_labels = params.get("group_labels") or params.get("var1_labels", {})
    labels_by_variable = params.get("labels_by_variable") or {}
    x_labels = labels_by_variable.get(x_var) or params.get("var2_labels", {})
    pair_name = f"{group_var} × {x_var}"

    temp = df[[group_var, x_var]].dropna()
    if temp.empty:
        return None

    ct = pd.crosstab(temp[x_var], temp[group_var])
    ct = ct.reindex(columns=group_values, fill_value=0)
    chi2, p, dof, expected = _chi_square_result(ct)
    n_total = int(ct.to_numpy().sum())
    min_dim = min(ct.shape[0], ct.shape[1]) - 1
    cramers_v = np.nan
    if min_dim > 0 and n_total > 0 and np.isfinite(float(chi2)):
        cramers_v = np.sqrt(chi2 / (n_total * min_dim))
    v_level = "—" if not np.isfinite(float(cramers_v)) else (
        "强" if cramers_v >= 0.5 else (
        "中等" if cramers_v >= 0.3 else "弱"
        )
    )

    x_values = list(ct.index)
    group_level_labels = [_label_for(group_labels, value) for value in group_values]
    x_level_labels = [_label_for(x_labels, value) for value in x_values]
    column_sums = ct.sum(axis=0)
    row_sums = ct.sum(axis=1)
    rows = []
    count_rows = []
    percent_rows = []
    for row_index, idx in enumerate(ct.index):
        row_total = int(ct.loc[idx].sum())
        cells = []
        count_cells = []
        percent_cells = []
        for col in ct.columns:
            count = int(ct.loc[idx, col])
            if percent_base == "row":
                denominator = int(row_sums[idx])
            else:
                denominator = int(column_sums[col])
            pct = count / denominator * 100 if denominator else 0
            cells.append(f"{count}({_fmt(pct, 2)})")
            count_cells.append(str(count))
            percent_cells.append(f"{_fmt(pct, 2)}%")
        total_pct = row_total / n_total * 100 if n_total else 0
        common_prefix = [x_var if row_index == 0 else "", _label_for(x_labels, idx)]
        stat_suffix = [
            _fmt(chi2, 3) if row_index == 0 else "",
            _p_with_sig(p) if row_index == 0 else "",
        ]
        rows.append([
            *common_prefix,
            *cells,
            f"{row_total}({_fmt(total_pct, 2)})",
            *stat_suffix,
        ])
        count_rows.append([
            *common_prefix,
            *count_cells,
            str(row_total),
            *stat_suffix,
        ])
        percent_rows.append([
            *common_prefix,
            *percent_cells,
            f"{_fmt(total_pct, 2)}%",
            *stat_suffix,
        ])

    total_row = [
        "",
        "总计",
        *[str(int(value)) for value in column_sums.tolist()],
        str(n_total),
        "",
        "",
    ]
    rows.append(total_row)
    count_rows.append(total_row)
    percent_rows.append(total_row)
    smart = (
        f"对{pair_name}进行卡方（交叉）分析，共纳入{n_total}个有效样本。"
        f"卡方检验结果显示两变量之间"
        f"{'存在' if np.isfinite(float(p)) and p < 0.05 else '不存在'}显著关联"
        f"（χ²={_fmt(chi2, 3)}，df={dof}，{_p_expr(p) if np.isfinite(float(p)) else 'p=—'}），"
        f"Cramer's V={_fmt(cramers_v, 3)}，关联强度{v_level}。"
    )
    matrix = [[int(ct.loc[idx, col]) for col in ct.columns] for idx in ct.index]
    chart = {
        "chartType": "crosstab_distribution",
        "title": f"{group_var}和{x_var}的交叉图",
        "varName": x_var,
        "data": {
            "groupVariable": group_var,
            "xVariable": x_var,
            "groupLabels": group_level_labels,
            "xLabels": x_level_labels,
            "matrix": matrix,
            "total": n_total,
            "percentBase": percent_base,
        },
    }
    return {
        "group_headers": group_level_labels,
        "rows": rows,
        "count_rows": count_rows,
        "percent_rows": percent_rows,
        "merged_rows": rows,
        "chart": chart,
        "description": smart,
        "chi2": chi2,
        "p": p,
        "dof": dof,
        "cramers_v": cramers_v,
        "v_level": v_level,
    }


def cross_tabulation_analysis(df, params):
    """
    卡方（交叉）分析。

    @param df: 数据 DataFrame
    @param params: 新参数 group_var/variables，兼容旧 var1/var2
    @return: 含 sections 的结果字典
    """
    group_var, variables = _cross_variables(params)
    if group_var not in df.columns or not variables:
        return {
            "name": "卡方（交叉）分析",
            "headers": [],
            "rows": [],
            "description": "请放入 1 个分组变量和至少 1 个 X 变量。",
        }

    valid_variables = [variable for variable in variables if variable in df.columns]
    if not valid_variables:
        return {
            "name": "卡方（交叉）分析",
            "headers": [],
            "rows": [],
            "description": "变量不存在。",
        }

    group_labels = params.get("group_labels") or params.get("var1_labels", {})
    percent_base = _percent_base(params)
    percent_label = _percent_base_label(percent_base)
    group_values = sorted(
        pd.Series(df[group_var]).dropna().unique().tolist(),
        key=lambda value: str(value),
    )
    headers = [
        "题目",
        "名称",
        *[_label_for(group_labels, value) for value in group_values],
        "总计",
        "χ²",
        "p",
    ]
    rows = []
    count_rows = []
    percent_rows = []
    charts = []
    messages = []
    for x_var in valid_variables:
        pair = _build_cross_pair(
            df,
            group_var,
            x_var,
            params,
            group_values,
            percent_base,
        )
        if not pair:
            messages.append(f"{group_var} × {x_var} 有效样本不足，无法完成列联分析。")
            continue
        rows.extend(pair["merged_rows"])
        count_rows.extend(pair["count_rows"])
        percent_rows.extend(pair["percent_rows"])
        charts.append(pair["chart"])
        messages.append(pair["description"])

    if not rows:
        return {
            "name": "卡方（交叉）分析",
            "headers": [],
            "rows": [],
            "description": "有效样本不足，无法完成列联分析。",
        }

    table_section = _sec_table(
        "输出结果1：列联表",
        headers,
        rows,
        note="* p<0.05 ** p<0.01",
        description=(
            "上表展示分组变量与各 X 变量的交叉分布。"
            f"数字(占比)模式中，普通单元格为频数({percent_label})，"
            "总计列为频数(总体百分比)。"
        ),
    )
    table_section["displayModeTitle"] = "交叉(卡方)分析结果"
    table_section["defaultDisplayMode"] = "count_percent"
    table_section["displayModes"] = [
        {"key": "count_percent", "label": "数字(占比)", "rows": rows},
        {"key": "count", "label": "数字", "rows": count_rows},
        {"key": "percent", "label": "百分比", "rows": percent_rows},
    ]
    sections = [table_section]
    advice = (
        "卡方（交叉）分析用于查看分组变量与 X 变量之间的分布关系；\n"
        "第一：先看交叉频数和列百分比，判断不同类别之间的分布差异；\n"
        "第二：若卡方检验p<0.05，说明两个变量之间存在统计学显著关联；\n"
        "第三：可结合Cramer's V判断关联强度，V越大说明关联越强。"
    )
    sections.append(_sec_advice(advice))
    sections.append(_sec_smart("\n".join(messages)))
    if charts:
        sections.append(_sec_charts("输出结果2：交叉图", charts))
    sections.append(_sec_refs(_REFS_GENERAL))

    name_suffix = f"{group_var} × " + "、".join(valid_variables)
    return {
        "name": f"卡方（交叉）分析：{name_suffix}",
        "headers": headers,
        "rows": rows,
        "description": "\n".join(messages),
        "sections": sections,
    }


run = cross_tabulation_analysis
