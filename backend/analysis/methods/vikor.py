# -*- coding: utf-8 -*-
# VIKOR 多准则妥协解排序法，对齐 SPSSPRO 单入口设计。
# 样本为行、指标为列；正向/负向方向先统一，再根据权重方式计算 S、R、Q。
from backend.analysis.common import *

METHOD_KEY = "vikor"

RESULT_PREVIEW_LIMIT = 15

WEIGHT_METHOD_CHOICES = [
    {"value": "entropy", "label": "熵权法"},
    {"value": "equal", "label": "权重相同"},
    {"value": "custom", "label": "自定义权重"},
]
WEIGHT_METHOD_MAP = {item["value"]: item for item in WEIGHT_METHOD_CHOICES}
WEIGHT_METHOD_ALIAS = {
    "熵权法": "entropy",
    "entropy": "entropy",
    "entropy_weight": "entropy",
    "权重相同": "equal",
    "等权": "equal",
    "equal": "equal",
    "不设置权重": "equal",
    "自定义权重": "custom",
    "custom": "custom",
}

METHOD_META = {
    "label": "多准则妥协解排序法(VIKOR)",
    "category": "综合评价",
    "description": "根据群体效用与个体遗憾构建折中排序，支持正负向指标、熵权/等权/自定义权重和决策系数 v",
    "order": 130,
    "aliases": ["VIKOR", "多准则妥协排序法", "多准则妥协解排序法"],
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
            "label": "加权方式",
            "choices": WEIGHT_METHOD_CHOICES,
            "default": "entropy",
            "hint": "熵权法根据指标离散程度赋权；权重相同为等权；自定义权重需放入指标权重列或通过 API 传 custom_weights/weights。",
        },
        {
            "key": "v_coefficient",
            "label": "决策机制系数v",
            "type": "number",
            "default": 0.5,
            "hint": "v 取值范围 0~1，默认 0.5；v>0.5 侧重群体效用，v<0.5 侧重个体遗憾。",
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


def _parse_v(value):
    try:
        v = float(value)
    except (TypeError, ValueError):
        return 0.5
    return max(0.0, min(1.0, v))


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
    """统一正负向指标方向；常量列保留为 1，别让 VIKOR 因除零中断。"""
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


def _vikor_calculate(normalized, weights, variables, v):
    """VIKOR 核心：计算 S（群体效用）、R（个体遗憾）、Q（折中值）。"""
    matrix = normalized[variables].astype(float)
    # 正理想解 f*（每列最大值）和负理想解 f-（每列最小值）
    f_star = matrix.max(axis=0)
    f_minus = matrix.min(axis=0)
    denom = (f_star - f_minus).replace(0, np.nan)
    # 加权差距矩阵
    weighted_gap = ((f_star - matrix) / denom).fillna(0.0).mul(weights, axis=1)
    s = weighted_gap.sum(axis=1)
    r = weighted_gap.max(axis=1)
    s_min, s_max = s.min(), s.max()
    r_min, r_max = r.min(), r.max()
    s_range = s_max - s_min if s_max - s_min > 0 else 1e-12
    r_range = r_max - r_min if r_max - r_min > 0 else 1e-12
    q = v * (s - s_min) / s_range + (1 - v) * (r - r_min) / r_range
    return s, r, q, f_star, f_minus, s_min, s_max, r_min, r_max


def _weight_rows(variables, weights, entropy, divergence, weight_method):
    if weight_method != "entropy":
        return ["项", "权重(%)"], [
            [variable, _fmt(weights[variable] * 100, 3)]
            for variable in variables
        ]
    rows = []
    for variable in variables:
        rows.append([
            variable,
            _fmt(entropy[variable], 4) if entropy is not None else "—",
            _fmt(divergence[variable], 4) if divergence is not None else "—",
            _fmt(weights[variable] * 100, 3),
        ])
    return ["项", "信息熵值e", "信息效用值d", "权重(%)"], rows


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


def _rank_rows(df, data, index_var, s, r, q):
    rank_series = q.rank(method="min", ascending=True).astype(int)
    ordered = q.sort_values(ascending=True)
    rows = []
    for row_index, value in ordered.items():
        rows.append([
            _label_for_row(df, row_index, index_var),
            _fmt(s.loc[row_index], 4),
            _fmt(r.loc[row_index], 4),
            _fmt(value, 4),
            str(int(rank_series.loc[row_index])),
        ])
    return rows, rank_series


def _score_chart(rows):
    top_rows = rows[:30]
    return {
        "chartType": "metric_comparison",
        "title": "VIKOR折中值Q排序",
        "data": {
            "metric": "折中值Q",
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


def _analysis_steps(weight_label):
    return (
        "1. 如果选择权重计算，则先出各个指标根据计算出的权重结果。\n"
        "2. 选出多准则妥协解排序法(VIKOR)的总结，包括群体效用值（S）和个体遗憾值（R）的最优值和最差值。\n"
        "3. 根据多准则妥协解排序法(VIKOR)计算结果，得到最终的排序值。"
    )


def run(df, params):
    """
    执行 VIKOR 多准则妥协解排序法。

    @param df: 当前数据集，样本为行、指标为列
    @param params: positive_vars、negative_vars、index_var、weight_method、weight_var、v_coefficient
    @return: 对齐 SPSSPRO 的结果 sections
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
    v = _parse_v(params.get("v_coefficient", 0.5))
    weight_label = WEIGHT_METHOD_MAP[weight_method]["label"]
    if weight_method == "custom" and weight_var in variables:
        return _error("指标权重列不能同时作为评价指标。")

    if len(variables) < 2:
        return _error("VIKOR 至少需要 2 个正向或负向指标。")
    numeric = df[variables].apply(pd.to_numeric, errors="coerce")
    complete_mask = numeric.notna().all(axis=1)
    valid_count = int(complete_mask.sum())
    if valid_count < 2:
        return _error("有效样本不足，VIKOR 至少需要 2 条完整样本。")

    data = numeric.loc[complete_mask, variables]
    normalized = _directional_normalize(data, positive_vars, negative_vars)
    weights, entropy, divergence, weight_error = _resolve_weights(
        df, normalized, params, variables, weight_method, weight_var
    )
    if weight_error:
        return _error(weight_error)

    s, r, q, f_star, f_minus, s_min, s_max, r_min, r_max = _vikor_calculate(
        normalized, weights, variables, v
    )
    rows, rank_series = _rank_rows(df, data, index_var, s, r, q)
    headers = ["评价对象", "群体效用值(S)", "个体遗憾值(R)", "折中值(Q)", "排序结果"]
    best = rows[0]

    weight_headers, weight_rows = _weight_rows(variables, weights, entropy, divergence, weight_method)

    # 计算结果表行数多时只预览前 N 行，全量通过 exportRows 保留给导出和展开。
    preview_rows = rows[:RESULT_PREVIEW_LIMIT]
    result_note = None
    if len(rows) > RESULT_PREVIEW_LIMIT:
        result_note = f"以上表格为预览结果，当前展示前 {RESULT_PREVIEW_LIMIT} 行；全部 {len(rows)} 行请点击展开或下载导出。"

    sections = [
        _sec_table(
            "算法配置",
            ["项", "值"],
            [
                ["正向指标", "、".join(positive_vars) or "未设置"],
                ["负向指标", "、".join(negative_vars) or "未设置"],
                ["索引项", index_var or "使用样本索引"],
                ["加权方式", weight_label],
                ["指标权重列", weight_var or "未设置"],
                ["决策机制系数v", _fmt(v, 2)],
            ],
            description="SPSSGO 采用 SPSSPRO 单入口设计：熵权VIKOR、等权VIKOR和自定义权重VIKOR通过加权方式切换。",
        ),
        _sec_table(
            "样本处理",
            ["项", "样本量"],
            [
                ["原始样本量", str(len(df))],
                ["有效样本量", str(valid_count)],
                ["排除样本量", str(len(df) - valid_count)],
            ],
            description="若某样本在任意评价指标上缺失，该样本不进入 VIKOR 计算。",
        ),
        _sec_advice(_analysis_steps(weight_label), title="分析步骤"),
        _sec_table(
            "输出结果1：指标权重计算",
            weight_headers,
            weight_rows,
            description=(
                "熵权法会输出信息熵值和信息效用值；权重相同和自定义权重时，信息熵相关列不参与计算。"
            ),
        ),
        _sec_table(
            "输出结果2：多准则妥协解排序法(VIKOR)总结果",
            ["S+（S值的最优值）", "S-（S值的最劣值）", "R+（R值的最优值）", "R-（R值的最劣值）", "决策机制系数v"],
            [[_fmt(s_min, 3), _fmt(s_max, 3), _fmt(r_min, 3), _fmt(r_max, 3), _fmt(v, 1)]],
            description="上表展示了在全部方案中群体效用值（S）和个体遗憾值（R）的最优值和最劣值。",
        ),
        _sec_table(
            "输出结果3：多准则妥协解排序法(VIKOR)计算结果",
            headers,
            preview_rows,
            note=result_note,
            description=(
                "上表展示了多准则妥协解排序法(VIKOR)的计算结果。"
                "群体效用值（S）为各个评价方案到最优方案的加权距离的总和；其值越小越好，越小说明群体效应越大。"
                "个体遗憾值（R）为各个评价方案到最优方案的加权距离中的最大距离；其值越小越好，越小说明个体遗憾越小。"
                "折中值Q是群体效用值与个体遗憾值的综合，在此基础上计算决策指标Q值，指标Q值越小方案越优，最终得到排序。"
            ),
        ),
        _sec_table(
            "输出结果4：描述统计",
            ["项", "样本量", "平均值", "标准差"],
            _describe_rows(data, variables),
            description="描述统计展示进入 VIKOR 模型的有效样本、均值和标准差。",
        ),
        _sec_charts("输出结果5：折中值Q排序图", [_score_chart(rows)], "展示折中值 Q 最小的前 30 个评价对象。"),
        _sec_advice(
            "如果研究需要复现 SPSSAU 的熵权VIKOR，请使用加权方式=熵权法；"
            "如果指标权重来自专家或外部模型，请使用自定义权重。所有逆向指标必须放入负向指标槽。"
        ),
        _sec_smart(
            f"VIKOR 分析完成，有效样本量 N={valid_count}；当前最优评价对象为 {best[0]}，"
            f"折中值 Q={best[3]}，排序第 {best[4]}。"
        ),
        _sec_refs(_REFS_GENERAL),
    ]
    # 计算结果表超过预览限制时，设置展开和导出支持。
    if len(rows) > RESULT_PREVIEW_LIMIT:
        for section in sections:
            if section.get("title") == "输出结果3：多准则妥协解排序法(VIKOR)计算结果":
                section["previewLimit"] = RESULT_PREVIEW_LIMIT
                section["exportRows"] = rows
                break
    return {
        "name": METHOD_META["label"],
        "headers": headers,
        "rows": rows,
        "description": f"VIKOR 分析完成，共评估 {valid_count} 个样本，加权方式为{weight_label}。",
        "sections": sections,
    }
