# -*- coding: utf-8 -*-
# 灰色关联分析入口：对齐 SPSSPRO 的特征序列、母序列、索引项和参数报告颗粒度。
# 样本为序列观测点，变量为序列；旧 reference_var/compare_vars 参数继续兼容。
from backend.analysis.common import *

METHOD_KEY = "grey_relational_analysis"

DIMENSIONLESS_CHOICES = [
    {"value": "initial", "label": "初值化"},
    {"value": "mean", "label": "均值化"},
    {"value": "none", "label": "不处理"},
]
DIMENSIONLESS_LABELS = {item["value"]: item["label"] for item in DIMENSIONLESS_CHOICES}
DIMENSIONLESS_ALIASES = {
    "初值化": "initial",
    "初始化": "initial",
    "initial": "initial",
    "init": "initial",
    "start": "initial",
    "均值化": "mean",
    "平均值化": "mean",
    "mean": "mean",
    "average": "mean",
    "不处理": "none",
    "原始值": "none",
    "none": "none",
    "raw": "none",
}
COEFFICIENT_PREVIEW_LIMIT = 15

METHOD_META = {
    "label": "灰色关联分析",
    "category": "综合评价",
    "description": "通过特征序列与母序列的几何形态相似程度评估关联强弱",
    "order": 120,
    "aliases": ["灰色关联", "灰关联分析", "Grey Relational Analysis", "GRA"],
    "slots": [
        {
            "key": "feature_vars",
            "label": "变量",
            "prefixLabel": "特征序列",
            "type": "multiple",
            "accept": "numeric",
            "min": 2,
            "hint": "放入至少 2 个需要和母序列比较的定量变量",
        },
        {
            "key": "mother_var",
            "label": "变量",
            "prefixLabel": "母序列",
            "type": "single",
            "accept": "numeric",
            "min": 1,
            "max": 1,
            "hint": "放入 1 个作为关联对象的定量变量",
        },
        {
            "key": "index_var",
            "label": "变量",
            "prefixLabel": "索引项",
            "type": "single",
            "accept": "categorical",
            "min": 0,
            "max": 1,
            "required": False,
            "hint": "可选，放入观测点名称或编号",
        },
    ],
    "options": [
        {
            "key": "dimensionless_method",
            "label": "无量纲处理方式",
            "choices": DIMENSIONLESS_CHOICES,
            "default": "mean",
            "hint": "初值化适合稳定递增或递减的数据；均值化适合没有明显升降趋势的数据；不处理直接使用原始数值。",
        },
        {
            "key": "rho",
            "label": "分辨系数ρ",
            "type": "number",
            "min": 0.0001,
            "max": 0.9999,
            "step": 0.01,
            "default": 0.5,
            "hint": "分辨系数ρ∈(0,1)，ρ越小分辨力越大，通常取ρ=0.5。",
        },
    ],
    "param_builder": "direct",
}


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


def _first_resolved(df, value):
    resolved = _resolve_cols(df, _as_list(value))
    return resolved[0] if resolved else ""


def _unique_preserve(items):
    result = []
    for item in items:
        if item not in result:
            result.append(item)
    return result


def _clean_dimensionless_method(params):
    for key in ("dimensionless_method", "dimensionless", "normalization_method", "dimensionless_processing"):
        value = params.get(key)
        if value not in (None, ""):
            text = str(value).strip()
            return DIMENSIONLESS_ALIASES.get(text, DIMENSIONLESS_ALIASES.get(text.lower(), "mean"))
    return "mean"


def _clean_rho(params):
    value = params.get("rho", params.get("resolution_coefficient", params.get("distinguishing_coefficient", 0.5)))
    rho = _safe_float(value, 0.5)
    if not np.isfinite(rho) or rho <= 0 or rho >= 1:
        return None, "分辨系数ρ必须是 0 到 1 之间的小数，通常取 0.5。"
    return float(rho), ""


def _resolve_inputs(df, params):
    feature_vars = _resolve_cols(df, _as_list(params.get("feature_vars", [])))
    mother_var = _first_resolved(df, params.get("mother_var"))
    if not feature_vars:
        feature_vars = _resolve_cols(df, _as_list(params.get("compare_vars", params.get("variables", []))))
    if not mother_var:
        mother_var = _first_resolved(df, params.get("reference_var"))

    feature_vars = _unique_preserve(feature_vars)
    if mother_var and mother_var in feature_vars:
        return None, None, None, f"母序列不能同时作为特征序列：{mother_var}。"
    index_var = _first_resolved(df, params.get("index_var"))
    return feature_vars, mother_var, index_var, ""


def _dimensionless(data, variables, method):
    adjusted = pd.DataFrame(index=data.index)
    for variable in variables:
        series = pd.to_numeric(data[variable], errors="coerce").astype(float)
        if method == "initial":
            base = float(series.iloc[0])
            if abs(base) <= 1e-12:
                return None, f"初值化要求各序列首个有效值不为 0，{variable} 不满足。"
            adjusted[variable] = series / base
        elif method == "mean":
            base = float(series.mean())
            if abs(base) <= 1e-12:
                return None, f"均值化要求各序列均值不为 0，{variable} 不满足。"
            adjusted[variable] = series / base
        else:
            adjusted[variable] = series
    return adjusted, ""


def _label_for_row(df, row_index, index_var):
    if index_var:
        value = df.loc[row_index, index_var]
        if pd.notna(value) and str(value).strip():
            return str(value).strip()
    return str(row_index)


def _coefficient_matrix(normalized, feature_vars, mother_var, rho):
    mother = normalized[mother_var]
    delta = normalized[feature_vars].sub(mother, axis=0).abs()
    delta_min = float(delta.min().min())
    delta_max = float(delta.max().max())
    if delta_max <= 1e-12:
        return pd.DataFrame(1.0, index=delta.index, columns=feature_vars)
    return (delta_min + rho * delta_max) / (delta + rho * delta_max)


def _fmt_coeff(value):
    try:
        number = float(value)
        if not np.isfinite(number):
            return "—"
        return f"{number:.16g}"
    except (ValueError, TypeError):
        return str(value)


def _coefficient_rows(df, coeff, index_var):
    rows = []
    for row_index in coeff.index:
        rows.append([
            _label_for_row(df, row_index, index_var),
            *[_fmt_coeff(coeff.loc[row_index, variable]) for variable in coeff.columns],
        ])
    return rows


def _grade_rows(grades):
    ranks = grades.rank(method="min", ascending=False).astype(int)
    ordered = grades.sort_values(ascending=False)
    return [[variable, _fmt(value, 3), str(int(ranks[variable]))] for variable, value in ordered.items()]


def _coefficient_chart(df, coeff, feature_vars, index_var):
    """生成关联系数多序列折线图，对齐 SPSSPRO 的关联系数图。"""
    labels = [_label_for_row(df, row_index, index_var) for row_index in coeff.index]
    metrics = {}
    for variable in feature_vars:
        metrics[variable] = [float(coeff.loc[row_index, variable]) for row_index in coeff.index]
    return {
        "chartType": "metric_comparison",
        "title": "关联系数图",
        "data": {
            "metric": "关联系数",
            "labels": labels,
            "values": [],
            "multiSeries": True,
            "metrics": metrics,
            "defaultMode": "line",
            "displayModes": [
                {"value": "line", "label": "折线图"},
                {"value": "bar", "label": "柱形图"},
            ],
            "axisLabels": {"x": "观测点", "y": "关联系数"},
            "yRange": [0, 1],
        },
    }


def _grade_chart(rows):
    return {
        "chartType": "metric_comparison",
        "title": "关联度柱形图",
        "data": {
            "metric": "关联度",
            "labels": [row[0] for row in rows],
            "values": [float(row[1]) for row in rows],
            "defaultMode": "bar",
            "displayModes": [
                {"value": "bar", "label": "柱形图"},
                {"value": "line", "label": "折线图"},
                {"value": "horizontalBar", "label": "条形图"},
            ],
            "axisLabels": {"x": "特征序列", "y": "关联度"},
            "yRange": [0, 1],
        },
    }


def _relationship_text(rows, mother_var, valid_count):
    if not rows:
        return "灰色关联分析未得到有效结果。"
    pairs = "、".join(f"{row[0]}与{mother_var}的关联度为{row[1]}" for row in rows)
    top = rows[0]
    bottom = rows[-1]
    return (
        f"灰色关联分析是对特征序列与母序列的关联度进行计算，有效样本量 N={valid_count}："
        f"{pairs}。其中与{mother_var}关联度最大的是{top[0]}，与{mother_var}关联度最小的是{bottom[0]}。"
    )


def _analysis_steps(method_label, rho):
    return (
        f"1. 针对数据进行无量纲化处理，本次使用{method_label}。\n"
        "2. 计算母序列和各特征序列在每个观测点上的绝对差值。\n"
        f"3. 按分辨系数ρ={_fmt(rho, 2)}计算灰色关联系数，ρ越小分辨力越大。\n"
        "4. 对每个特征序列的关联系数取平均，得到灰色关联度。\n"
        "5. 按灰色关联度由高到低排序，关联度越高说明与母序列变化趋势越接近。\n"
        "PS：初值化是将序列除以首个有效值，适合稳定递增或递减的数据；"
        "均值化是将序列除以均值，适合没有明显升降趋势的数据。"
    )


def run(df, params):
    """
    执行灰色关联分析。

    @param df: 当前数据集，行是序列观测点，列是母序列或特征序列
    @param params: feature_vars、mother_var、index_var、dimensionless_method、rho；兼容 reference_var/compare_vars
    @return: 对齐 SPSSPRO 输入和结果颗粒度的灰色关联系数、关联度与排序
    """
    params = params or {}
    feature_vars, mother_var, index_var, input_error = _resolve_inputs(df, params)
    if input_error:
        return _error(input_error)
    if not mother_var:
        return _error("灰色关联分析需要 1 个母序列变量。")
    if not feature_vars:
        return _error("灰色关联分析至少需要 1 个特征序列变量。")

    rho, rho_error = _clean_rho(params)
    if rho_error:
        return _error(rho_error)
    method = _clean_dimensionless_method(params)
    method_label = DIMENSIONLESS_LABELS[method]

    variables = [mother_var] + feature_vars
    numeric = df[variables].apply(pd.to_numeric, errors="coerce")
    complete_mask = numeric.notna().all(axis=1)
    valid_count = int(complete_mask.sum())
    if valid_count < 2:
        return _error("有效样本不足，灰色关联分析至少需要 2 条完整样本。")

    data = numeric.loc[complete_mask, variables]
    normalized, normalize_error = _dimensionless(data, variables, method)
    if normalize_error:
        return _error(normalize_error)

    coeff = _coefficient_matrix(normalized, feature_vars, mother_var, rho)
    grades = coeff.mean(axis=0)
    rows = _grade_rows(grades)
    relationship = _relationship_text(rows, mother_var, valid_count)
    coeff_rows = _coefficient_rows(df, coeff, index_var)
    coeff_preview_rows = coeff_rows[:COEFFICIENT_PREVIEW_LIMIT]
    coeff_note = None
    if len(coeff_rows) > len(coeff_preview_rows):
        coeff_note = f"以上表格为预览结果，当前展示前 {len(coeff_preview_rows)} 行；全部 {len(coeff_rows)} 行请点击下载导出。"
    coeff_section = _sec_table(
        "输出结果1：灰色关联系数",
        ["行索引"] + feature_vars,
        coeff_preview_rows,
        note=coeff_note,
        description="灰色关联系数反映每个观测点上特征序列与母序列的局部接近程度，后续关联度为各观测点关联系数的平均值。",
    )
    if len(coeff_rows) > len(coeff_preview_rows):
        # 页面只预览前 15 行；导出必须保留全量，别在这里截断计算结果。
        coeff_section["previewLimit"] = COEFFICIENT_PREVIEW_LIMIT
        coeff_section["exportRows"] = coeff_rows
    headers = ["评价项", "关联度", "排名"]
    sections = [
        _sec_table(
            "算法配置",
            ["项", "值"],
            [
                ["特征序列", "、".join(feature_vars)],
                ["母序列", mother_var],
                ["索引项", index_var or "使用样本索引"],
                ["无量纲处理方式", method_label],
                ["分辨系数ρ", _fmt(rho, 2)],
            ],
            description="SPSSGO 采用 SPSSPRO 的特征序列、母序列、索引项入口，并保留旧版参考序列/比较序列参数兼容。",
        ),
        _sec_table(
            "样本处理",
            ["项", "样本量"],
            [
                ["原始样本量", str(len(df))],
                ["有效样本量", str(valid_count)],
                ["排除样本量", str(len(df) - valid_count)],
            ],
            description="若某观测点在母序列或任一特征序列上缺失，该观测点不进入灰色关联计算。",
        ),
        _sec_advice(relationship, title="分析结果"),
        _sec_advice(_analysis_steps(method_label, rho), title="分析步骤"),
        coeff_section,
        _sec_charts(
            "输出结果2：关联系数图",
            [_coefficient_chart(df, coeff, feature_vars, index_var)],
            "关联系数代表着该子序列对与母序列对应维度上的关联程度值（数字越大，代表关联性越强）。",
        ),
        _sec_table(
            "输出结果3：灰色关联度结果",
            headers,
            rows,
            description="关联度越接近 1，说明该特征序列与母序列的几何形态越相似，关联程度越强。",
        ),
        _sec_charts(
            "输出结果4：灰色关联度排序图",
            [_grade_chart(rows)],
            "图中按灰色关联度展示特征序列与母序列的关联强弱，默认按关联度由高到低排序。",
        ),
        _sec_advice(
            "第一：灰色关联分析强调序列形态相似性，不等同于线性相关系数；\n"
            "第二：无量纲处理方式会影响差值尺度，稳定单调序列可用初值化，常规无明显趋势序列优先均值化；\n"
            "第三：分辨系数ρ通常取 0.5，调整ρ时应在报告中说明理由。"
        ),
        _sec_smart(relationship),
        _sec_refs(_REFS_GENERAL),
    ]
    return {
        "name": METHOD_META["label"],
        "headers": headers,
        "rows": rows,
        "description": f"灰色关联分析完成，有效样本量 N={valid_count}，关联度最高的特征序列为 {rows[0][0]}。",
        "sections": sections,
    }
