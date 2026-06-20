# -*- coding: utf-8 -*-
# 模糊综合评价这里按 SPSSAU/SPSSPRO 的入口和结果颗粒度编排。
# 当前口径是样本为行、评价项为列；评价集固定为差/中/优，后续扩展别破坏 sections 协议。
from backend.analysis.common import *

METHOD_KEY = "fuzzy_comprehensive_evaluation"

FUZZY_OPERATOR_CHOICES = [
    {
        "value": "main_factor_decision",
        "label": "主因素决定型：M(∧,V)",
        "recommendation": "更多考虑指标权重，输入数据在一定程度上不会有明显影响，不推荐使用。",
    },
    {
        "value": "main_factor_prominent",
        "label": "主因素突出型：M(*,V)",
        "recommendation": "在主因素决定型基础上修正输入数据的上界程度，不推荐使用。",
    },
    {
        "value": "bounded_sum_min",
        "label": "取小与有界型：M(∧,+)",
        "recommendation": "更多使用输入数据信息，推荐使用。",
    },
    {
        "value": "weighted_average",
        "label": "加权平均型：M(*,+)",
        "recommendation": "综合利用指标权重和输入数据信息，推荐使用。",
    },
]
FUZZY_OPERATOR_MAP = {item["value"]: item for item in FUZZY_OPERATOR_CHOICES}
FUZZY_OPERATOR_ALIAS = {
    "M(∧,∨)": "main_factor_decision",
    "M(A,V)": "main_factor_decision",
    "M(∧,V)": "main_factor_decision",
    "主因素决定型": "main_factor_decision",
    "主因素决定型：M(∧,∨)": "main_factor_decision",
    "M(*,∨)": "main_factor_prominent",
    "M(*,V)": "main_factor_prominent",
    "主因素突出型": "main_factor_prominent",
    "主因素突出型：M(*,∨)": "main_factor_prominent",
    "M(∧,+)": "bounded_sum_min",
    "M(A,+)": "bounded_sum_min",
    "取小与有界型": "bounded_sum_min",
    "取小与有界型：M(∧,+)": "bounded_sum_min",
    "M(*,+)": "weighted_average",
    "加权平均型": "weighted_average",
    "加权平均型：M(*,+)": "weighted_average",
}

WEIGHT_METHOD_CHOICES = [
    {"value": "entropy", "label": "熵权法"},
    {"value": "equal", "label": "不设置权重"},
    {"value": "custom", "label": "自定义权重"},
]
WEIGHT_METHOD_MAP = {item["value"]: item for item in WEIGHT_METHOD_CHOICES}
WEIGHT_METHOD_ALIAS = {
    "熵权法": "entropy",
    "entropy_weight": "entropy",
    "entropy": "entropy",
    "不设置权重": "equal",
    "等权": "equal",
    "equal": "equal",
    "自定义权重": "custom",
    "custom": "custom",
}

GRADE_LABELS = ["差", "中", "优"]
GRADE_SCORES = np.array([1.0, 3.0, 5.0], dtype=float)
GRADE_FALLBACK = np.array([1 / 3, 1 / 3, 1 / 3], dtype=float)

METHOD_META = {
    "label": "模糊综合评价",
    "category": "综合评价",
    "description": "通过指标权重、模糊算子和评价集隶属度得到综合评价结果",
    "order": 45,
    "slots": [
        {
            "key": "variables",
            "label": "评价项",
            "type": "multiple",
            "accept": "numeric",
            "min": 2,
            "hint": "放入评价指标",
        },
        {
            "key": "index_var",
            "label": "索引项",
            "type": "single",
            "accept": "categorical",
            "min": 0,
            "max": 1,
            "required": False,
            "hint": "可选，放入样本名称或编号",
        },
        {
            "key": "weight_var",
            "label": "评价指标权重",
            "type": "single",
            "accept": "numeric",
            "min": 0,
            "max": 1,
            "required": False,
            "visible_if": {"weight_method": "custom"},
            "hint": "可选，选择自定义权重时按评价项顺序读取前 N 个有效数值",
        },
    ],
    "options": [
        {
            "key": "weight_method",
            "label": "变量权重",
            "choices": WEIGHT_METHOD_CHOICES,
            "default": "entropy",
            "hint": "熵权法按指标离散程度自动赋权；不设置权重表示等权；自定义权重需放入评价指标权重列或通过 API 传 custom_weights/weights。",
        },
        {
            "key": "fuzzy_operator",
            "label": "模糊算子",
            "choices": FUZZY_OPERATOR_CHOICES,
            "default": "weighted_average",
            "hint": (
                "主因素决定型 M(∧,V)：更多考虑指标权重，不推荐。\n"
                "主因素突出型 M(*,V)：修正输入数据上界，不推荐。\n"
                "取小与有界型 M(∧,+)：更多使用输入数据信息，推荐。\n"
                "加权平均型 M(*,+)：综合利用权重和输入信息，推荐。"
            ),
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


def _clean_choice(value, alias_map, default):
    if value in (None, ""):
        return default
    text = str(value).strip()
    if text in alias_map:
        return alias_map[text]
    lowered = text.lower()
    return alias_map.get(lowered, default)


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
    if isinstance(loaded, list):
        return loaded
    if isinstance(loaded, dict):
        return loaded
    return re.split(r"[,，;；\s]+", text)


def _custom_weights(df, params, variables, weight_var):
    raw = params.get("custom_weights", params.get("weights"))
    if isinstance(raw, str):
        raw = _parse_weight_text(raw)
    if isinstance(raw, dict):
        values = [raw.get(variable) for variable in variables]
        return _normalize_weights(values, variables)
    if isinstance(raw, (list, tuple)):
        if len(raw) < len(variables):
            return None, f"自定义权重数量不足，需要 {len(variables)} 个。"
        return _normalize_weights(list(raw)[:len(variables)], variables)

    if weight_var:
        values = pd.to_numeric(df[weight_var], errors="coerce").dropna().tolist()
        if len(values) < len(variables):
            return None, f"评价指标权重列至少需要 {len(variables)} 个有效数值。"
        return _normalize_weights(values[:len(variables)], variables)

    return None, "选择自定义权重时，请放入评价指标权重列，或通过 API 传 custom_weights/weights。"


def _entropy_weights(data, variables):
    normalized = _normalize_benefit_frame(data)
    column_sum = normalized.sum(axis=0).replace(0, np.nan)
    proportion = normalized.div(column_sum, axis=1).fillna(0.0)
    safe_proportion = proportion.replace(0, 1e-12)
    k = 1.0 / np.log(len(proportion))
    entropy = (-k * (safe_proportion * np.log(safe_proportion)).sum(axis=0)).clip(0, 1)
    divergence = (1 - entropy).clip(lower=0)
    if float(divergence.sum()) > 0:
        weights = divergence / divergence.sum()
    else:
        weights = pd.Series([1 / len(variables)] * len(variables), index=variables)
    return normalized, weights, entropy, divergence


def _resolve_weights(df, data, params, variables, weight_method, weight_var):
    normalized = _normalize_benefit_frame(data)
    if weight_method == "entropy":
        return (*_entropy_weights(data, variables), "")
    if weight_method == "custom":
        weights, error = _custom_weights(df, params, variables, weight_var)
        if error:
            return normalized, None, None, None, error
        return normalized, weights, None, None, ""
    weights = pd.Series([1 / len(variables)] * len(variables), index=variables)
    return normalized, weights, None, None, ""


def _membership_tensor(normalized):
    values = normalized.to_numpy(dtype=float)
    low = np.clip(1 - values * 2, 0, 1)
    mid = np.clip(1 - np.abs(values - 0.5) * 2, 0, 1)
    high = np.clip(values * 2 - 1, 0, 1)
    return np.stack([low, mid, high], axis=2)


def _apply_operator(matrix, weights, operator):
    weight_column = weights.to_numpy(dtype=float).reshape(-1, 1)
    if operator == "main_factor_decision":
        raw = np.max(np.minimum(weight_column, matrix), axis=0)
    elif operator == "main_factor_prominent":
        raw = np.max(weight_column * matrix, axis=0)
    elif operator == "bounded_sum_min":
        raw = np.minimum(1.0, np.minimum(weight_column, matrix).sum(axis=0))
    else:
        raw = (weight_column * matrix).sum(axis=0)

    raw = np.clip(raw.astype(float), 0, 1)
    total = float(raw.sum())
    normalized = raw / total if total > 0 else GRADE_FALLBACK.copy()
    score = float(normalized.dot(GRADE_SCORES))
    return raw, normalized, score


def _weight_rows(variables, weights, entropy, divergence):
    rows = []
    for variable in variables:
        rows.append([
            variable,
            _fmt(entropy[variable], 4) if entropy is not None else "—",
            _fmt(divergence[variable], 4) if divergence is not None else "—",
            _fmt(weights[variable] * 100, 3),
        ])
    return rows


def _operator_table(operator):
    rows = []
    for item in FUZZY_OPERATOR_CHOICES:
        rows.append([
            item["label"],
            "当前选择" if item["value"] == operator else "可选",
            item["recommendation"],
        ])
    return rows


def _score_chart(rows):
    top_rows = rows[:30]
    return {
        "chartType": "metric_comparison",
        "title": "综合得分排序",
        "data": {
            "metric": "综合得分",
            "labels": [row[0] for row in top_rows],
            "values": [float(row[5]) for row in top_rows],
            "defaultMode": "bar",
            "displayModes": [
                {"value": "bar", "label": "柱形图"},
                {"value": "line", "label": "折线图"},
                {"value": "horizontalBar", "label": "条形图"},
            ],
        },
    }


def _analysis_steps(weight_label, operator_label):
    return (
        "1. 确定评价项和评价集，当前评价集固定为差、中、优。\n"
        f"2. 确定指标权重，当前权重方式为{weight_label}；可通过熵权法、等权或自定义权重生成权重向量 A。\n"
        "3. 将评价项标准化后构造隶属度矩阵 R，得到每个样本在差、中、优上的隶属度。\n"
        f"4. 使用{operator_label}进行模糊合成，并按归一化隶属度计算综合得分和排序。\n"
        "PS：模糊算子选择会影响结果解释。主因素决定型和主因素突出型不推荐；取小与有界型、加权平均型更适合常规综合评价。"
    )


def _advice(weight_method, operator):
    operator_info = FUZZY_OPERATOR_MAP[operator]
    weight_label = WEIGHT_METHOD_MAP[weight_method]["label"]
    return (
        f"当前使用{weight_label}和{operator_info['label']}。"
        "若希望结果更多体现原始数据差异，可优先使用取小与有界型；"
        "若希望同时利用指标权重和输入数据信息，优先使用加权平均型。"
        "所有评价项默认按正向指标处理，逆向指标需要先统一方向。"
    )


def run(df, params):
    """
    执行模糊综合评价。

    @param df: 当前数据集，样本为行、评价项为列
    @param params: variables、index_var、weight_var、weight_method、fuzzy_operator
    @return: 包含权重、隶属度、综合得分和算子说明的结果 sections
    """
    params = params or {}
    variables = _resolve_cols(df, _as_list(params.get("variables", [])))
    index_var = _first_resolved(df, params.get("index_var"))
    weight_var = _first_resolved(df, params.get("weight_var"))
    weight_method = _clean_choice(params.get("weight_method"), WEIGHT_METHOD_ALIAS, "entropy")
    operator = _clean_choice(params.get("fuzzy_operator"), FUZZY_OPERATOR_ALIAS, "weighted_average")

    if len(variables) < 2:
        return _error("模糊综合评价至少需要 2 个评价项。")
    if weight_method == "custom" and weight_var in variables:
        return _error("评价指标权重列不能同时作为评价项。")

    numeric = df[variables].apply(pd.to_numeric, errors="coerce")
    complete_mask = numeric.notna().all(axis=1)
    valid_count = int(complete_mask.sum())
    if valid_count < 2:
        return _error("有效样本不足，模糊综合评价至少需要 2 条完整样本。")

    data = numeric.loc[complete_mask, variables]
    normalized, weights, entropy, divergence, weight_error = _resolve_weights(
        df, data, params, variables, weight_method, weight_var
    )
    if weight_error:
        return _error(weight_error)

    labels = [_label_for_row(df, row_index, index_var) for row_index in data.index]
    tensor = _membership_tensor(normalized)
    raw_rows = []
    score_rows = []
    for position, label in enumerate(labels):
        raw, membership, score = _apply_operator(tensor[position], weights, operator)
        level = GRADE_LABELS[int(np.argmax(membership))]
        raw_rows.append([
            label,
            *[_fmt(value, 4) for value in raw],
            *[_fmt(value, 4) for value in membership],
        ])
        score_rows.append([
            label,
            *[_fmt(value, 4) for value in membership],
            level,
            _fmt(score, 4),
        ])

    score_rows.sort(key=lambda row: float(row[5]), reverse=True)
    for rank, row in enumerate(score_rows, start=1):
        row.append(str(rank))

    score_values = np.array([float(row[5]) for row in score_rows], dtype=float)
    weight_label = WEIGHT_METHOD_MAP[weight_method]["label"]
    operator_label = FUZZY_OPERATOR_MAP[operator]["label"]
    best = score_rows[0]
    headers = ["评价对象", "差隶属度", "中隶属度", "优隶属度", "最大隶属等级", "综合得分", "排序"]

    sections = [
        _sec_table(
            "算法配置",
            ["项", "值"],
            [
                ["评价项", "、".join(variables)],
                ["索引项", index_var or "使用样本索引"],
                ["变量权重", weight_label],
                ["评价指标权重列", weight_var or "未设置"],
                ["模糊算子", operator_label],
                ["评价集", "、".join(GRADE_LABELS)],
            ],
            description="模糊综合评价将评价项标准化后构造隶属度矩阵，再结合权重和模糊算子得到综合评价结果。",
        ),
        _sec_table(
            "样本处理",
            ["项", "样本量"],
            [
                ["原始样本量", str(len(df))],
                ["有效样本量", str(valid_count)],
                ["排除样本量", str(len(df) - valid_count)],
            ],
            description="若某样本在任意评价项上缺失，该样本不进入模糊综合评价计算。",
        ),
        _sec_advice(_analysis_steps(weight_label, operator_label), title="分析步骤"),
        _sec_table(
            "模糊算子说明",
            ["类型", "状态", "说明"],
            _operator_table(operator),
            description="SPSSAU/SPSSPRO 均提供多种模糊算子；默认采用更稳妥的加权平均型。",
        ),
        _sec_table(
            "输出结果1：指标权重计算",
            ["项", "信息熵值e", "信息效用值d", "权重(%)"],
            _weight_rows(variables, weights, entropy, divergence),
            description=(
                "熵权法会先输出信息熵和信息效用值；不设置权重和自定义权重时，信息熵相关列不参与计算。"
            ),
        ),
        _sec_table(
            "输出结果2：综合隶属度矩阵",
            ["评价对象", "差", "中", "优", "差(归一化)", "中(归一化)", "优(归一化)"],
            raw_rows,
            description="前 3 列为模糊算子合成后的隶属度，后 3 列为用于综合得分计算的归一化隶属度。",
        ),
        _sec_table(
            "输出结果3：综合得分计算",
            headers,
            score_rows,
            description="综合得分按差=1、中=3、优=5 进行加权计算，得分越高表示综合评价越好。",
        ),
        _sec_charts(
            "输出结果4：综合得分排序图",
            [_score_chart(score_rows)],
            "图中展示综合得分最高的前 30 个评价对象；样本不足 30 个时展示全部。",
        ),
        _sec_table(
            "综合得分概况",
            ["指标", "值"],
            [
                ["平均得分", _fmt(score_values.mean(), 4)],
                ["最大得分", _fmt(score_values.max(), 4)],
                ["最小得分", _fmt(score_values.min(), 4)],
                ["最高评价对象", best[0]],
            ],
        ),
        _sec_advice(_advice(weight_method, operator)),
        _sec_smart(
            f"模糊综合评价完成，有效样本量 N={valid_count}；当前综合得分最高的评价对象为 {best[0]}，"
            f"综合得分={best[5]}，最大隶属等级为{best[4]}。"
        ),
        _sec_refs(_REFS_GENERAL),
    ]
    return {
        "name": METHOD_META["label"],
        "headers": headers,
        "rows": score_rows,
        "description": f"模糊综合评价完成，共评估 {valid_count} 个样本，模糊算子为 {operator_label}。",
        "sections": sections,
    }
