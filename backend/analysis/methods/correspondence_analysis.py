# -*- coding: utf-8 -*-
# 对应分析：统一入口放入多个定类变量，二变量走标准 CA，多变量走 MCA 类别映射。
from backend.analysis.common import *

METHOD_KEY = "correspondence_analysis"
METHOD_META = {
    "label": "对应分析",
    "category": "问卷分析包",
    "description": "用于可视化探索多组定类变量之间的关系",
    "order": 70,
    "slots": [
        {
            "key": "variables",
            "label": "变量",
            "type": "multiple",
            "accept": "categorical",
            "min": 2,
            "hint": "放入用于对应分析的定类变量，变量数至少为2",
        },
    ],
    "options": [],
    "param_builder": "direct",
}

_REFS_CORRESPONDENCE = _REFS_GENERAL + [
    "[3] Greenacre M. Correspondence Analysis in Practice[M]. 3rd ed. Boca Raton: CRC Press, 2017.",
    "[4] 高惠璇. 应用多元统计分析[M]. 北京: 北京大学出版社, 2005.",
]


def inject_metadata(metadata_map, params):
    enriched = dict(params)
    variables = _analysis_variables(enriched)
    enriched["variable_labels"] = {
        variable: metadata_map.get(variable, {}).get("display_name") or variable
        for variable in variables
    }
    enriched["labels_by_variable"] = {
        variable: normalized_label_dict(metadata_map.get(variable, {}).get("value_labels", {}))
        for variable in variables
    }
    return enriched


def _analysis_variables(params):
    variables = params.get("variables") or []
    if isinstance(variables, str):
        variables = [variables]
    legacy = [params.get("var1"), params.get("var2")]
    for variable in legacy:
        if variable and variable not in variables:
            variables.append(variable)
    unique = []
    for variable in variables:
        if variable and variable not in unique:
            unique.append(variable)
    return unique


def _label(variable_labels, variable):
    return variable_labels.get(variable, variable)


def _level_label(labels_by_variable, variable, value):
    labels = labels_by_variable.get(variable) or {}
    return labels.get(str(value), str(value))


def _fmt_percent(value):
    return _fmt(value, 3)


def _p_with_sig(p):
    if p is None:
        return "—"
    try:
        value = float(p)
    except (TypeError, ValueError):
        return "—"
    if not np.isfinite(value):
        return "—"
    return f"{_fmt(value, 3)}{_sig(value)}"


def _safe_chi_square(ct):
    try:
        return chi2_contingency(ct)
    except Exception:
        return np.nan, np.nan, 0, np.full(ct.shape, np.nan)


def _summary_rows(singular_values, inertia, spss_style=False):
    display_singulars = inertia if spss_style else singular_values
    display_inertia = inertia ** 2 if spss_style else inertia
    total_inertia = float(display_inertia.sum())
    rows = []
    cumulative = 0.0
    for index, singular_value in enumerate(display_singulars):
        pct = float(display_inertia[index] / total_inertia * 100) if total_inertia else 0.0
        cumulative += pct
        rows.append([
            f"维度{index + 1}",
            _fmt(singular_value, 3),
            _fmt(display_inertia[index], 3),
            _fmt_percent(pct),
            _fmt_percent(cumulative),
        ])
    return rows


def _orient_coordinates(*coord_arrays):
    if not coord_arrays:
        return coord_arrays
    oriented = [coords.copy() for coords in coord_arrays]
    dim_count = min(coords.shape[1] for coords in oriented if len(coords.shape) == 2)
    for dim in range(dim_count):
        values = np.concatenate([coords[:, dim] for coords in oriented])
        non_zero = values[np.abs(values) > 1e-12]
        if len(non_zero) and non_zero[0] > 0:
            for coords in oriented:
                coords[:, dim] *= -1
    return tuple(oriented)


def _ca_core(matrix):
    total = float(matrix.sum())
    if total <= 0:
        return None
    P = matrix / total
    row_masses = P.sum(axis=1)
    col_masses = P.sum(axis=0)
    expected = np.outer(row_masses, col_masses)
    with np.errstate(divide="ignore", invalid="ignore"):
        residuals = np.divide(
            P - expected,
            np.sqrt(expected),
            out=np.zeros_like(P, dtype=float),
            where=expected > 0,
        )
    U, singular_values, VT = np.linalg.svd(residuals, full_matrices=False)
    dim_count = min(len(singular_values), matrix.shape[0] - 1, matrix.shape[1] - 1)
    if dim_count <= 0:
        return None
    singular_values = singular_values[:dim_count]
    U = U[:, :dim_count]
    VT = VT[:dim_count, :]
    with np.errstate(divide="ignore", invalid="ignore"):
        row_coords = np.divide(
            U * singular_values,
            np.sqrt(row_masses).reshape(-1, 1),
            out=np.zeros((matrix.shape[0], dim_count), dtype=float),
            where=row_masses.reshape(-1, 1) > 0,
        )
        col_coords = np.divide(
            VT.T * singular_values,
            np.sqrt(col_masses).reshape(-1, 1),
            out=np.zeros((matrix.shape[1], dim_count), dtype=float),
            where=col_masses.reshape(-1, 1) > 0,
        )
    return {
        "singular_values": singular_values,
        "inertia": singular_values ** 2,
        "row_masses": row_masses,
        "col_masses": col_masses,
        "row_coords": row_coords,
        "col_coords": col_coords,
    }


def _point_rows(series_labels, item_labels, coords, display_dim_count):
    rows = []
    for index, label in enumerate(item_labels):
        coord_values = [_fmt(coords[index, dim], 3) for dim in range(display_dim_count)]
        rows.append([
            series_labels[index],
            label,
            *coord_values,
        ])
    return rows


def _correspondence_chart(title, x_label, y_label, points, series):
    return {
        "chartType": "correspondence_map",
        "title": title,
        "data": {
            "xLabel": x_label,
            "yLabel": y_label,
            "points": points,
            "series": series,
        },
    }


def _analysis_steps(variable_names, is_multiple):
    scope = "多个定类变量" if is_multiple else "两个定类变量"
    return "\n".join([
        f"多重对应分析MCA通常用于群体细分(定位)研究，本次基于{scope}进行研究。",
        "第一、模型汇总表列出降维后各维度的特征根值(惯量)、解释率和累积解释率。",
        "第二、为了便于图形展示和分析，对应分析图默认展示前2个维度。",
        "第三、如果前2个维度的累积解释率较高，意味着对应分析效果较好。",
    ])


def _smart(name, n_valid, summary_rows):
    cumulative_2 = summary_rows[1][4] if len(summary_rows) >= 2 else (summary_rows[0][4] if summary_rows else "—")
    quality = "较好" if _safe_float(str(cumulative_2).replace("%", ""), 0) >= 80 else "一般"
    return (
        f"本次对{name}进行对应分析，共纳入{n_valid}个有效样本。"
        f"前两个维度累计贡献率为{cumulative_2}%，二维对应图对原始类别关系的表达效果{quality}。"
        "解释时优先看远离原点、贡献率较高且彼此接近的类别点。"
    )


def _score_advice():
    return "\n".join([
        "维度得分为各类别项在各维度上的坐标具体值，其代表各点在空间中的距离和位置，可反映点之间的关系情况（用于画对应图）。",
        "第一、维度得分的绝对值越大，意味着该点与其它点的联系越强。",
        "第二、建议基于对应分析图进行深入分析各项间的关联关系。",
        "第三、建议查看帮助文档，深入研究对应图解析。",
    ])


def _build_contingency_section(ct, row_labels, col_labels, var1_label, var2_label):
    headers = [var1_label, *col_labels, "总计"]
    rows = []
    for index, raw_value in enumerate(ct.index):
        row_total = int(ct.loc[raw_value].sum())
        rows.append([
            row_labels[index],
            *[str(int(ct.loc[raw_value, column])) for column in ct.columns],
            str(row_total),
        ])
    rows.append(["总计", *[str(int(value)) for value in ct.sum(axis=0).tolist()], str(int(ct.values.sum()))])
    return _sec_table(
        "输出结果1：交叉列联表",
        headers,
        rows,
        description="上表展示两个定类变量的原始交叉频数，是对应分析降维的基础。",
    )


def _run_two_variable_ca(df, params, variables):
    variable_labels = params.get("variable_labels") or {}
    labels_by_variable = params.get("labels_by_variable") or {}
    var1, var2 = variables[:2]
    var1_label = _label(variable_labels, var1)
    var2_label = _label(variable_labels, var2)

    temp = df[[var1, var2]].dropna()
    ct = pd.crosstab(temp[var1], temp[var2])
    if ct.shape[0] < 2 or ct.shape[1] < 2:
        return {"name": "对应分析", "headers": [], "rows": [], "description": "对应分析至少需要2×2的列联表。"}

    core = _ca_core(ct.to_numpy(dtype=float))
    if not core:
        return {"name": "对应分析", "headers": [], "rows": [], "description": "列联表有效维度不足。"}
    row_coords, col_coords = _orient_coordinates(core["row_coords"], core["col_coords"])

    row_labels = [_level_label(labels_by_variable, var1, value) for value in ct.index]
    col_labels = [_level_label(labels_by_variable, var2, value) for value in ct.columns]
    display_dim_count = min(3, len(core["singular_values"]))
    dim_headers = [f"维度{index + 1}" for index in range(display_dim_count)]

    summary_headers = ["维度", "奇异值", "特征根值(惯量)", "解释率", "累积解释率"]
    summary_rows = _summary_rows(core["singular_values"], core["inertia"], spss_style=True)
    n_valid = int(ct.values.sum())

    row_point_rows = _point_rows(
        [var1_label] * len(row_labels),
        row_labels,
        row_coords,
        display_dim_count,
    )
    col_point_rows = _point_rows(
        [var2_label] * len(col_labels),
        col_labels,
        col_coords,
        display_dim_count,
    )
    point_headers = ["字段名", "项", *dim_headers]
    point_rows = row_point_rows + col_point_rows

    chart_points = []
    for index, label in enumerate(row_labels):
        chart_points.append({
            "label": label,
            "series": var1_label,
            "x": float(row_coords[index, 0]),
            "y": float(row_coords[index, 1]) if row_coords.shape[1] > 1 else 0.0,
        })
    for index, label in enumerate(col_labels):
        chart_points.append({
            "label": label,
            "series": var2_label,
            "x": float(col_coords[index, 0]),
            "y": float(col_coords[index, 1]) if col_coords.shape[1] > 1 else 0.0,
        })

    name = f"{var1_label} × {var2_label}"
    smart = _smart(name, n_valid, summary_rows)
    sections = [
        _sec_table("输出结果1：模型汇总", summary_headers, summary_rows),
        _sec_advice(_analysis_steps([var1_label, var2_label], False), "分析建议"),
        _sec_smart(smart),
        _sec_table("输出结果2：维度得分", point_headers, point_rows),
        _sec_advice(_score_advice(), "分析建议"),
        _sec_charts(
            "输出结果3：维度对应图",
            [_correspondence_chart("维度1和维度2对应图", "维度1", "维度2", chart_points, [var1_label, var2_label])],
            "上图展示两个变量各类别点在前两个维度上的位置，点越接近表示分布结构越相似。",
        ),
        _sec_refs(_REFS_CORRESPONDENCE),
    ]
    return {
        "name": f"对应分析：{name}",
        "headers": summary_headers,
        "rows": summary_rows,
        "description": smart,
        "sections": sections,
    }


def _indicator_matrix(temp, variables, variable_labels, labels_by_variable):
    columns = []
    series_labels = []
    item_labels = []
    for variable in variables:
        values = sorted(temp[variable].dropna().unique().tolist(), key=lambda value: str(value))
        for value in values:
            columns.append((variable, value))
            series_labels.append(_label(variable_labels, variable))
            item_labels.append(_level_label(labels_by_variable, variable, value))
    matrix = np.zeros((len(temp), len(columns)), dtype=float)
    for column_index, (variable, value) in enumerate(columns):
        matrix[:, column_index] = (temp[variable].to_numpy() == value).astype(float)
    return matrix, columns, series_labels, item_labels


def _run_multiple_variable_mca(df, params, variables):
    variable_labels = params.get("variable_labels") or {}
    labels_by_variable = params.get("labels_by_variable") or {}
    valid_labels = [_label(variable_labels, variable) for variable in variables]
    temp = df[variables].dropna()
    if len(temp) < 2:
        return {"name": "对应分析", "headers": [], "rows": [], "description": "有效样本不足。"}

    matrix, columns, series_labels, item_labels = _indicator_matrix(temp, variables, variable_labels, labels_by_variable)
    if matrix.shape[1] <= len(variables):
        return {"name": "对应分析", "headers": [], "rows": [], "description": "各变量有效分类不足，无法完成多重对应分析。"}

    core = _ca_core(matrix)
    if not core:
        return {"name": "对应分析", "headers": [], "rows": [], "description": "有效维度不足，无法完成多重对应分析。"}

    col_coords = _orient_coordinates(core["col_coords"])[0]

    display_dim_count = min(3, len(core["singular_values"]))
    dim_headers = [f"维度{index + 1}" for index in range(display_dim_count)]
    summary_headers = ["维度", "奇异值", "特征根值(惯量)", "解释率", "累积解释率"]
    summary_rows = _summary_rows(core["singular_values"], core["inertia"], spss_style=True)
    point_headers = ["字段名", "项", *dim_headers]
    point_rows = _point_rows(
        series_labels,
        item_labels,
        col_coords,
        display_dim_count,
    )
    chart_points = []
    for index, label in enumerate(item_labels):
        chart_points.append({
            "label": label,
            "series": series_labels[index],
            "x": float(col_coords[index, 0]),
            "y": float(col_coords[index, 1]) if col_coords.shape[1] > 1 else 0.0,
        })

    name = "、".join(valid_labels)
    smart = _smart(name, len(temp), summary_rows)
    sections = [
        _sec_table("输出结果1：模型汇总", summary_headers, summary_rows),
        _sec_advice(_analysis_steps(valid_labels, True), "分析建议"),
        _sec_smart(smart),
        _sec_table("输出结果2：维度得分", point_headers, point_rows),
        _sec_advice(_score_advice(), "分析建议"),
        _sec_charts(
            "输出结果3：维度对应图",
            [_correspondence_chart("维度1和维度2对应图", "维度1", "维度2", chart_points, valid_labels)],
            "上图展示多个变量各类别点在前两个维度上的位置，点越接近表示类别模式越相似。",
        ),
        _sec_refs(_REFS_CORRESPONDENCE),
    ]
    return {
        "name": f"对应分析：{name}",
        "headers": summary_headers,
        "rows": summary_rows,
        "description": smart,
        "sections": sections,
    }


def correspondence_analysis(df, params):
    """
    对应分析。

    @param df: 数据 DataFrame
    @param params: variables 多个定类变量；兼容旧 var1/var2
    @return: 维度摘要、类别点坐标、对应分析图和解释建议
    """
    variables = _analysis_variables(params)
    if len(variables) < 2:
        return {"name": "对应分析", "headers": [], "rows": [], "description": "请至少放入2个定类变量。"}
    missing = [variable for variable in variables if variable not in df.columns]
    if missing:
        return {"name": "对应分析", "headers": [], "rows": [], "description": f"变量不存在：{', '.join(missing)}。"}
    if len(variables) == 2:
        return _run_two_variable_ca(df, params, variables)
    return _run_multiple_variable_mca(df, params, variables)


run = correspondence_analysis
