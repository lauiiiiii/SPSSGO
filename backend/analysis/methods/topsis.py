# -*- coding: utf-8 -*-
# TOPSIS 这里合并 SPSSPRO 单入口和 SPSSAU“TOPSIS/熵权TOPSIS”双入口口径。
# 样本为行、指标为列；正向/负向方向先统一，再根据权重方式执行 TOPSIS。
from backend.analysis.common import *

METHOD_KEY = "topsis"

WEIGHT_METHOD_CHOICES = [
    {"value": "entropy", "label": "熵权法"},
    {"value": "equal", "label": "不设置权重"},
    {"value": "custom", "label": "自定义权重"},
]
WEIGHT_METHOD_MAP = {item["value"]: item for item in WEIGHT_METHOD_CHOICES}
WEIGHT_METHOD_ALIAS = {
    "熵权法": "entropy",
    "entropy": "entropy",
    "entropy_weight": "entropy",
    "熵权TOPSIS": "entropy",
    "熵权topsis": "entropy",
    "不设置权重": "equal",
    "等权": "equal",
    "equal": "equal",
    "TOPSIS": "equal",
    "topsis": "equal",
    "自定义权重": "custom",
    "custom": "custom",
}

METHOD_META = {
    "label": "优劣解距离法(TOPSIS)",
    "category": "综合评价",
    "description": "基于正负理想解距离评价方案优劣，支持等权、熵权和自定义权重",
    "order": 50,
    "aliases": ["TOPSIS", "熵权TOPSIS", "熵权TOPSIS法", "优劣解距离法"],
    "slots": [
        {
            "key": "positive_vars",
            "label": "变量",
            "prefixLabel": "正向指标",
            "type": "multiple",
            "accept": "numeric",
            "min": 0,
            "required": False,
            "hint": "拖入正向指标",
        },
        {
            "key": "negative_vars",
            "label": "变量",
            "prefixLabel": "负向指标",
            "type": "multiple",
            "accept": "numeric",
            "min": 0,
            "required": False,
            "hint": "拖入负向指标",
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
            "hint": "可选，放入样本名称或编号",
        },
        {
            "key": "weight_var",
            "label": "变量",
            "prefixLabel": "指标权重",
            "type": "single",
            "accept": "numeric",
            "min": 0,
            "max": 1,
            "required": False,
            "visible_if": {"weight_method": "custom"},
            "hint": "选择自定义权重时，按指标顺序读取前 N 个有效数值",
        },
    ],
    "options": [
        {
            "key": "weight_method",
            "label": "变量权重",
            "choices": WEIGHT_METHOD_CHOICES,
            "default": "entropy",
            "hint": "熵权法对应 SPSSAU 的熵权TOPSIS；不设置权重对应普通 TOPSIS；自定义权重需放入指标权重列或通过 API 传 custom_weights/weights。",
        },
        {
            "key": "save_process",
            "label": "保存过程值",
            "type": "checkbox",
            "default": False,
            "hint": "选中后生成新数据版本，保存 D+、D-、相对接近度 C 和排序结果。",
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


def _as_bool(value, default=False):
    if value in (None, ""):
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on", "是", "勾选"}


def _clean_weight_method(value):
    if value in (None, ""):
        return "entropy"
    text = str(value).strip()
    if text in WEIGHT_METHOD_ALIAS:
        return WEIGHT_METHOD_ALIAS[text]
    return WEIGHT_METHOD_ALIAS.get(text.lower(), "entropy")


def _first_resolved(df, value):
    resolved = _resolve_cols(df, _as_list(value))
    return resolved[0] if resolved else ""


def _unique_preserve(items):
    result = []
    for item in items:
        if item not in result:
            result.append(item)
    return result


def _directional_normalize(data, positive_vars, negative_vars):
    """统一正负向指标方向；常量列保留为 1，别让 TOPSIS 因除零中断。"""
    normalized = pd.DataFrame(index=data.index)
    for variable in positive_vars + negative_vars:
        series = pd.to_numeric(data[variable], errors="coerce").astype(float)
        min_value = float(series.min())
        max_value = float(series.max())
        spread = max_value - min_value
        if spread == 0:
            normalized[variable] = 1.0
        elif variable in negative_vars:
            normalized[variable] = (max_value - series) / spread
        else:
            normalized[variable] = (series - min_value) / spread
    return normalized.fillna(0.0)


def _label_for_row(df, row_index, index_var):
    if index_var:
        value = df.loc[row_index, index_var]
        if pd.notna(value) and str(value).strip():
            return str(value).strip()
    return str(row_index)


def _normalize_weights(values, variables):
    series = pd.Series(values, index=variables, dtype="float64")
    if series.isna().any() or np.isinf(series.to_numpy(dtype=float)).any():
        return None, "自定义权重中存在非数值或无穷值。"
    if (series < 0).any():
        return None, "自定义权重不能为负数。"
    total = float(series.sum())
    if total <= 0:
        return None, "自定义权重之和必须大于 0。"
    return series / total, ""


def _parse_weight_text(value):
    text = str(value or "").strip()
    if not text:
        return []
    try:
        loaded = json.loads(text)
    except Exception:
        loaded = None
    if isinstance(loaded, (list, dict)):
        return loaded
    return re.split(r"[,，;；\s]+", text)


def _custom_weights(df, params, variables, weight_var):
    raw = params.get("custom_weights", params.get("weights"))
    if isinstance(raw, str):
        raw = _parse_weight_text(raw)
    if isinstance(raw, dict):
        return _normalize_weights([raw.get(variable) for variable in variables], variables)
    if isinstance(raw, (list, tuple)):
        if len(raw) < len(variables):
            return None, f"自定义权重数量不足，需要 {len(variables)} 个。"
        return _normalize_weights(list(raw)[:len(variables)], variables)
    if weight_var:
        values = pd.to_numeric(df[weight_var], errors="coerce").dropna().tolist()
        if len(values) < len(variables):
            return None, f"指标权重列至少需要 {len(variables)} 个有效数值。"
        return _normalize_weights(values[:len(variables)], variables)
    return None, "选择自定义权重时，请放入指标权重列，或通过 API 传 custom_weights/weights。"


def _entropy_weights(normalized, variables):
    safe = normalized[variables].clip(lower=0)
    column_sum = safe.sum(axis=0).replace(0, np.nan)
    proportion = safe.div(column_sum, axis=1).fillna(0.0)
    safe_proportion = proportion.replace(0, 1e-12)
    k = 1.0 / np.log(len(proportion))
    entropy = (-k * (safe_proportion * np.log(safe_proportion)).sum(axis=0)).clip(0, 1)
    divergence = (1 - entropy).clip(lower=0)
    if float(divergence.sum()) > 0:
        weights = divergence / divergence.sum()
    else:
        weights = pd.Series([1 / len(variables)] * len(variables), index=variables)
    return weights, entropy, divergence


def _resolve_weights(df, normalized, params, variables, weight_method, weight_var):
    if weight_method == "entropy":
        weights, entropy, divergence = _entropy_weights(normalized, variables)
        return weights, entropy, divergence, ""
    if weight_method == "custom":
        weights, error = _custom_weights(df, params, variables, weight_var)
        return weights, None, None, error
    weights = pd.Series([1 / len(variables)] * len(variables), index=variables)
    return weights, None, None, ""


def _topsis_calculate(normalized, weights, variables):
    matrix = normalized[variables].astype(float)
    vector_norm = np.sqrt((matrix ** 2).sum(axis=0)).replace(0, np.nan)
    standardized = matrix.div(vector_norm, axis=1).fillna(0.0)
    weighted = standardized.mul(weights, axis=1)
    ideal = weighted.max(axis=0)
    anti_ideal = weighted.min(axis=0)
    d_pos = np.sqrt(((weighted - ideal) ** 2).sum(axis=1))
    d_neg = np.sqrt(((weighted - anti_ideal) ** 2).sum(axis=1))
    closeness = d_neg / (d_pos + d_neg).replace(0, np.nan)
    closeness = closeness.fillna(0.0)
    return standardized, weighted, ideal, anti_ideal, d_pos, d_neg, closeness


def _weight_rows(variables, weights, entropy, divergence):
    rows = []
    for variable in variables:
        rows.append([
            variable,
            _fmt(entropy[variable], 3) if entropy is not None else "—",
            _fmt(divergence[variable], 3) if divergence is not None else "—",
            _fmt(weights[variable] * 100, 3),
        ])
    return rows


def _describe_rows(data, variables):
    rows = []
    for variable in variables:
        series = pd.to_numeric(data[variable], errors="coerce").dropna()
        rows.append([
            variable,
            str(len(series)),
            _fmt(series.mean(), 3),
            _fmt(series.std(ddof=1), 3) if len(series) > 1 else "0.000",
        ])
    return rows


def _rank_rows(df, data, index_var, d_pos, d_neg, closeness):
    rank_series = closeness.rank(method="min", ascending=False).astype(int)
    ordered = closeness.sort_values(ascending=False)
    rows = []
    for row_index, value in ordered.items():
        rows.append([
            _label_for_row(df, row_index, index_var),
            _fmt(d_pos.loc[row_index], 3),
            _fmt(d_neg.loc[row_index], 3),
            _fmt(value, 3),
            str(int(rank_series.loc[row_index])),
        ])
    return rows, rank_series


def _score_chart(rows):
    top_rows = rows[:30]
    return {
        "chartType": "metric_comparison",
        "title": "TOPSIS相对接近度排序",
        "data": {
            "metric": "相对接近度C",
            "labels": [row[0] for row in top_rows],
            "values": [float(row[3]) for row in top_rows],
            "defaultMode": "bar",
            "displayModes": [
                {"value": "bar", "label": "柱形图"},
                {"value": "line", "label": "折线图"},
                {"value": "horizontalBar", "label": "条形图"},
            ],
        },
    }


def _score_columns(df, d_pos, d_neg, closeness, rank_series):
    row_count = len(df)
    row_positions = {row_index: position for position, row_index in enumerate(df.index)}
    columns = [
        ("TOPSIS_D正", d_pos),
        ("TOPSIS_D负", d_neg),
        ("TOPSIS_相对接近度C", closeness),
        ("TOPSIS_排序结果", rank_series),
    ]
    result = []
    for base_name, series in columns:
        values = [None] * row_count
        for row_index, value in series.items():
            position = row_positions.get(row_index)
            if position is None:
                continue
            values[position] = None if pd.isna(value) else round(float(value), 6)
        result.append({"base_name": base_name, "values": values})
    return result


def _analysis_steps(weight_label):
    return (
        "1. 将正向指标和负向指标统一方向，并处理量纲问题。\n"
        f"2. 按{weight_label}计算指标权重；熵权法对应 SPSSAU 的熵权TOPSIS，不设置权重对应普通 TOPSIS。\n"
        "3. 构造加权标准化矩阵，求出正理想解 A+ 和负理想解 A-。\n"
        "4. 计算各评价对象到 A+ 的距离 D+、到 A- 的距离 D-，并得到相对接近度 C。\n"
        "5. 按 C 值由大到小排序，C 越大说明越接近最优方案。"
    )


def run(df, params):
    """
    执行 TOPSIS 综合评价。

    @param df: 当前数据集，样本为行、指标为列
    @param params: positive_vars、negative_vars、index_var、weight_method、weight_var
    @return: 对齐 SPSSPRO 单入口和 SPSSAU TOPSIS/熵权TOPSIS 的结果 sections
    """
    params = params or {}
    positive_vars = _resolve_cols(df, _as_list(params.get("positive_vars", [])))
    negative_vars = _resolve_cols(df, _as_list(params.get("negative_vars", [])))
    if not positive_vars and not negative_vars:
        positive_vars = _resolve_cols(df, _as_list(params.get("variables", [])))
    duplicate_vars = sorted(set(positive_vars) & set(negative_vars))
    if duplicate_vars:
        return _error(f"同一指标不能同时作为正向和负向指标：{', '.join(duplicate_vars)}。")

    variables = _unique_preserve(positive_vars + negative_vars)
    index_var = _first_resolved(df, params.get("index_var"))
    weight_var = _first_resolved(df, params.get("weight_var"))
    weight_method = _clean_weight_method(params.get("weight_method"))
    weight_label = WEIGHT_METHOD_MAP[weight_method]["label"]
    if weight_method == "custom" and weight_var in variables:
        return _error("指标权重列不能同时作为评价指标。")

    if len(variables) < 2:
        return _error("TOPSIS 至少需要 2 个正向或负向指标。")
    numeric = df[variables].apply(pd.to_numeric, errors="coerce")
    complete_mask = numeric.notna().all(axis=1)
    valid_count = int(complete_mask.sum())
    if valid_count < 2:
        return _error("有效样本不足，TOPSIS 至少需要 2 条完整样本。")

    data = numeric.loc[complete_mask, variables]
    normalized = _directional_normalize(data, positive_vars, negative_vars)
    weights, entropy, divergence, weight_error = _resolve_weights(
        df, normalized, params, variables, weight_method, weight_var
    )
    if weight_error:
        return _error(weight_error)

    _, _, ideal, anti_ideal, d_pos, d_neg, closeness = _topsis_calculate(normalized, weights, variables)
    rows, rank_series = _rank_rows(df, data, index_var, d_pos, d_neg, closeness)
    headers = ["评价对象", "正理想解距离D+", "负理想解距离D-", "相对接近度C", "排序结果"]
    best = rows[0]

    sections = [
        _sec_table(
            "算法配置",
            ["项", "值"],
            [
                ["正向指标", "、".join(positive_vars) or "未设置"],
                ["负向指标", "、".join(negative_vars) or "未设置"],
                ["索引项", index_var or "使用样本索引"],
                ["变量权重", weight_label],
                ["指标权重列", weight_var or "未设置"],
            ],
            description="SPSSGO 采用 SPSSPRO 单入口设计：熵权TOPSIS、普通TOPSIS和自定义权重TOPSIS通过变量权重切换。",
        ),
        _sec_table(
            "样本处理",
            ["项", "样本量"],
            [
                ["原始样本量", str(len(df))],
                ["有效样本量", str(valid_count)],
                ["排除样本量", str(len(df) - valid_count)],
            ],
            description="若某样本在任意评价指标上缺失，该样本不进入 TOPSIS 计算。",
        ),
        _sec_advice(_analysis_steps(weight_label), title="分析步骤"),
        _sec_table(
            "输出结果1：指标权重计算",
            ["项", "信息熵值e", "信息效用值d", "权重(%)"],
            _weight_rows(variables, weights, entropy, divergence),
            description=(
                "熵权法会输出信息熵值和信息效用值；不设置权重和自定义权重时，信息熵相关列不参与计算。"
            ),
        ),
        _sec_table(
            "输出结果2：TOPSIS评价法计算结果",
            headers,
            rows,
            description="相对接近度 C 越大，评价对象越接近正理想解并远离负理想解，排序越靠前。",
        ),
        _sec_table(
            "输出结果3：正负理想解",
            ["项", "正理想解A+", "负理想解A-"],
            [[variable, _fmt(ideal[variable], 3), _fmt(anti_ideal[variable], 3)] for variable in variables],
            description="正理想解 A+ 为各评价指标的最大值，负理想解 A- 为各评价指标的最小值。",
        ),
        _sec_table(
            "输出结果4：描述统计",
            ["项", "样本量", "平均值", "标准差"],
            _describe_rows(data, variables),
            description="描述统计展示进入 TOPSIS 模型的有效样本、均值和标准差。",
        ),
        _sec_charts("输出结果5：相对接近度排序图", [_score_chart(rows)], "展示相对接近度最高的前 30 个评价对象。"),
        _sec_advice(
            "如果研究需要复现 SPSSAU 的熵权TOPSIS，请使用变量权重=熵权法；"
            "如果指标权重来自专家或外部模型，请使用自定义权重。所有逆向指标必须放入负向指标槽。"
        ),
        _sec_smart(
            f"TOPSIS 分析完成，有效样本量 N={valid_count}；当前最优评价对象为 {best[0]}，"
            f"相对接近度 C={best[3]}，排序第 {best[4]}。"
        ),
        _sec_refs(_REFS_GENERAL),
    ]
    result = {
        "name": METHOD_META["label"],
        "headers": headers,
        "rows": rows,
        "description": f"TOPSIS 分析完成，共评估 {valid_count} 个样本，变量权重为{weight_label}。",
        "sections": sections,
    }
    if _as_bool(params.get("save_process"), default=False):
        result["score_columns"] = _score_columns(df, d_pos, d_neg, closeness, rank_series)
    return result
