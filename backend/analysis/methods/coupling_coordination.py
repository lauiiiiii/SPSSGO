# -*- coding: utf-8 -*-
# 耦合协调度单入口：吸收 SPSSPRO 的正负向指标入口和 SPSSAU 的标签、区间化、权重与完整报告颗粒度。
# 样本为行、指标或子系统为列；旧 group1/group2/group3 参数继续兼容，别直接删。
from backend.analysis.common import *

METHOD_KEY = "coupling_coordination"

WEIGHT_METHOD_CHOICES = [
    {"value": "equal", "label": "不设置权重"},
    {"value": "entropy", "label": "熵权法"},
    {"value": "custom", "label": "自定义权重"},
]
WEIGHT_METHOD_MAP = {item["value"]: item for item in WEIGHT_METHOD_CHOICES}
WEIGHT_METHOD_ALIAS = {
    "不设置权重": "equal",
    "等权": "equal",
    "equal": "equal",
    "none": "equal",
    "耦合协调度": "equal",
    "熵权法": "entropy",
    "entropy": "entropy",
    "entropy_weight": "entropy",
    "熵权": "entropy",
    "自定义权重": "custom",
    "custom": "custom",
}

GRADE_LABELS = [
    "极度失调",
    "严重失调",
    "中度失调",
    "轻度失调",
    "濒临失调",
    "勉强协调",
    "初级协调",
    "中级协调",
    "良好协调",
    "优质协调",
]

METHOD_META = {
    "label": "耦合协调度",
    "category": "综合评价",
    "description": "衡量多个系统或指标之间的耦合关系与协调发展水平，支持正负向指标、协调指数、权重和数据区间化",
    "order": 70,
    "aliases": ["耦合协调", "耦合协调度模型", "耦合协调度分析", "协调度"],
    "slots": [
        {
            "key": "positive_vars",
            "label": "变量",
            "prefixLabel": "正向指标",
            "type": "multiple",
            "accept": "numeric",
            "min": 0,
            "required": False,
            "hint": "拖入越大越好的指标",
        },
        {
            "key": "negative_vars",
            "label": "变量",
            "prefixLabel": "负向指标",
            "type": "multiple",
            "accept": "numeric",
            "min": 0,
            "required": False,
            "hint": "拖入越小越好的指标",
        },
        {
            "key": "coordination_index_var",
            "label": "变量",
            "prefixLabel": "协调指数",
            "type": "single",
            "accept": "numeric",
            "min": 0,
            "max": 1,
            "required": False,
            "hint": "可选，只能放入 0~1 的已计算协调指数T；原始题项请放入正向/负向指标",
        },
        {
            "key": "label_vars",
            "label": "变量",
            "prefixLabel": "标签",
            "type": "multiple",
            "accept": "categorical",
            "min": 0,
            "max": 2,
            "required": False,
            "hint": "可选，最多 2 个标签变量，用于标识样本",
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
            "label": "指标权重",
            "choices": WEIGHT_METHOD_CHOICES,
            "default": "equal",
            "hint": "默认各指标权重相等；熵权法按离散程度赋权；自定义权重需放入指标权重列或通过 API 传 custom_weights/weights。",
        },
        {
            "key": "data_intervalization",
            "label": "数据区间化",
            "type": "checkbox",
            "default": True,
            "hint": "将同趋势化后的数据压缩到 0.01~0.99，避免 0 值导致耦合度退化或不稳定。",
        },
        {
            "key": "save_process",
            "label": "保存计算值",
            "type": "checkbox",
            "default": False,
            "hint": "选中后生成新数据版本，保存耦合度C、协调指数T、耦合协调度D和协调等级。",
        },
    ],
    "param_builder": "direct",
}

_REFS_COUPLING = _REFS_GENERAL + [
    "[3] 廖重斌. 环境与经济协调发展的定量评判及其分类体系——以珠江三角洲城市群为例[J]. 热带地理, 1999, 19(2):171-177.",
    "[4] 刘耀彬,李仁东,宋学锋. 中国城市化与生态环境耦合度分析[J]. 自然资源学报, 2005, 20(1):105-112.",
    "[5] 陈伟忠,周春应. 中国区域科技金融与技术创新耦合协调度分析[J]. 生产力研究, 2021(6):113-118.",
    "[6] Haken H. Synergetics: An Introduction[M]. 3rd ed. Berlin: Springer, 1983.",
    "[7] Nardo M, Saisana M, Saltelli A, Tarantola S, Hoffman A, Giovannini E. Handbook on Constructing Composite Indicators: Methodology and User Guide[M]. Paris: OECD Publishing, 2008.",
    "[8] Shannon C E. A mathematical theory of communication[J]. Bell System Technical Journal, 1948, 27(3):379-423; 27(4):623-656.",
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


def _as_bool(value, default=False):
    if value in (None, ""):
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on", "是", "勾选", "选中"}


def _clean_choice(value, alias_map, default):
    if value in (None, ""):
        return default
    text = str(value).strip()
    if text in alias_map:
        return alias_map[text]
    return alias_map.get(text.lower(), default)


def _first_resolved(df, value):
    resolved = _resolve_cols(df, _as_list(value))
    return resolved[0] if resolved else ""


def _unique_preserve(items):
    result = []
    for item in items:
        if item not in result:
            result.append(item)
    return result


def _coordination_index_var(df, params):
    for key in ("coordination_index_var", "coordination_var", "coordination_t_var", "t_var"):
        variable = _first_resolved(df, params.get(key))
        if variable:
            return variable
    return ""


def _resolve_label_vars(df, params):
    label_vars = _resolve_cols(df, _as_list(params.get("label_vars", [])))
    index_var = _first_resolved(df, params.get("index_var"))
    if index_var:
        label_vars = [index_var] + label_vars
    return _unique_preserve(label_vars)[:2]


def _new_input_groups(df, params):
    positive_vars = _resolve_cols(df, _as_list(params.get("positive_vars", [])))
    negative_vars = _resolve_cols(df, _as_list(params.get("negative_vars", [])))
    if not positive_vars and not negative_vars:
        positive_vars = _resolve_cols(df, _as_list(params.get("variables", params.get("items", []))))
    if not positive_vars and not negative_vars:
        return None

    duplicate_vars = sorted(set(positive_vars) & set(negative_vars))
    if duplicate_vars:
        return {"error": f"同一指标不能同时作为正向和负向指标：{', '.join(duplicate_vars)}。"}
    variables = _unique_preserve(positive_vars + negative_vars)
    return {
        "mode": "directional",
        "positive_vars": positive_vars,
        "negative_vars": negative_vars,
        "groups": [[variable] for variable in variables],
        "group_labels": variables,
        "all_vars": variables,
    }


def _legacy_input_groups(df, params):
    groups = []
    labels = []
    for index, key in enumerate(["group1_vars", "group2_vars", "group3_vars"], start=1):
        variables = _resolve_cols(df, _as_list(params.get(key, [])))
        if not variables:
            continue
        groups.append(variables)
        labels.append(f"子系统{index}")
    if len(groups) < 2:
        return {"error": "耦合协调度至少需要 2 个正向或负向指标；旧版子系统参数至少需要 2 个子系统。"}
    all_vars = _unique_preserve([variable for group in groups for variable in group])
    return {
        "mode": "legacy_groups",
        "positive_vars": all_vars,
        "negative_vars": [],
        "groups": groups,
        "group_labels": labels,
        "all_vars": all_vars,
    }


def _resolve_inputs(df, params):
    resolved = _new_input_groups(df, params)
    if resolved is not None:
        return resolved
    return _legacy_input_groups(df, params)


def _intervalize(series):
    return 0.01 + 0.98 * series


def _directional_normalize(data, positive_vars, negative_vars, intervalize=True):
    """正负向同趋势化后再区间化；常量列给 1，避免样本全相等时后续全挂。"""
    normalized = pd.DataFrame(index=data.index)
    for variable in positive_vars + negative_vars:
        series = pd.to_numeric(data[variable], errors="coerce").astype(float)
        min_value = float(series.min())
        max_value = float(series.max())
        spread = max_value - min_value
        if spread == 0:
            values = pd.Series(1.0, index=data.index)
        elif variable in negative_vars:
            values = (max_value - series) / spread
        else:
            values = (series - min_value) / spread
        normalized[variable] = _intervalize(values) if intervalize else values
    return normalized.fillna(0.0)


def _normalize_single(series, intervalize=True):
    values = pd.to_numeric(series, errors="coerce").astype(float)
    min_value = float(values.min())
    max_value = float(values.max())
    spread = max_value - min_value
    if spread == 0:
        normalized = pd.Series(1.0, index=values.index)
    else:
        normalized = (values - min_value) / spread
    return _intervalize(normalized) if intervalize else values


def _coordination_index_score(series):
    values = pd.to_numeric(series, errors="coerce").astype(float)
    if ((values < 0) | (values > 1)).any():
        return None, "协调指数T变量必须是 0~1 之间的已计算指数；如果是原始量表题项，请放入正向/负向指标，不要放入协调指数。"
    return values, ""


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


def _weight_table(weight_method, variables, weights, entropy, divergence):
    if weight_method != "entropy":
        return ["项", "权重(%)"], [
            [variable, _fmt(weights[variable] * 100, 3)]
            for variable in variables
        ]

    return ["项", "信息熵值e", "信息效用值d", "权重(%)"], [
        [
            variable,
            _fmt(entropy[variable], 4) if entropy is not None else "—",
            _fmt(divergence[variable], 4) if divergence is not None else "—",
            _fmt(weights[variable] * 100, 3),
        ]
        for variable in variables
    ]


def _subsystem_scores(data, normalized, groups, group_labels):
    columns = {}
    for label, group in zip(group_labels, groups):
        columns[label] = normalized[group].mean(axis=1)
    return pd.DataFrame(columns, index=data.index)


def _coupling_degree(subsystem_df):
    k = len(subsystem_df.columns)
    matrix = subsystem_df.clip(lower=0).astype(float)
    product = matrix.prod(axis=1)
    mean_u = matrix.mean(axis=1)
    denominator = mean_u.pow(k)
    ratio = product.div(denominator.replace(0, np.nan)).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    ratio = ratio.clip(lower=0.0, upper=1.0)
    return ratio.pow(1 / k)


def _label_text_for_row(df, row_index, label_vars):
    parts = []
    for variable in label_vars:
        value = df.loc[row_index, variable]
        if pd.notna(value) and str(value).strip():
            parts.append(str(value).strip())
    return " / ".join(parts)


def _build_item_labels(df, row_indexes, label_vars):
    labels = [_label_text_for_row(df, row_index, label_vars) for row_index in row_indexes]
    non_empty_labels = [label for label in labels if label]
    if len(non_empty_labels) == len(labels) and len(set(non_empty_labels)) == len(non_empty_labels):
        return labels
    return [f"第{position + 1}项" for position in range(len(row_indexes))]


def _grade_for_value(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = 0
    grade = int(np.floor(min(max(number, 0), 0.999999) * 10)) + 1
    return min(max(grade, 1), 10), GRADE_LABELS[min(max(grade, 1), 10) - 1]


def _calculation_rows(df, row_indexes, label_vars, coupling, t_score, coordination):
    rows = []
    grade_by_index = {}
    item_labels = _build_item_labels(df, row_indexes, label_vars)
    for position, row_index in enumerate(row_indexes):
        grade, label = _grade_for_value(coordination.loc[row_index])
        grade_by_index[row_index] = grade
        rows.append([
            item_labels[position],
            _fmt(coupling.loc[row_index], 6),
            _fmt(t_score.loc[row_index], 6),
            _fmt(coordination.loc[row_index], 6),
            str(grade),
            label,
        ])
    return rows, grade_by_index


def _grade_rule_rows():
    rows = []
    for index, label in enumerate(GRADE_LABELS, start=1):
        lower = (index - 1) / 10
        upper = index / 10
        if index == 1:
            rule = f"0 ≤ D < {_fmt(upper, 1)}"
        elif index == 10:
            rule = f"{_fmt(lower, 1)} ≤ D ≤ 1.0"
        else:
            rule = f"{_fmt(lower, 1)} ≤ D < {_fmt(upper, 1)}"
        rows.append([str(index), rule, label])
    return rows


def _grade_summary_rows(calc_rows):
    total = len(calc_rows)
    counts = {label: 0 for label in GRADE_LABELS}
    for row in calc_rows:
        counts[row[5]] = counts.get(row[5], 0) + 1
    return [
        [str(index), label, str(counts[label]), _fmt(counts[label] / total * 100 if total else 0, 2) + "%"]
        for index, label in enumerate(GRADE_LABELS, start=1)
        if counts[label] > 0
    ]


def _score_chart(calc_rows):
    return {
        "chartType": "metric_comparison",
        "title": "耦合协调度图",
        "data": {
            "metric": "耦合协调度D值",
            "labels": [row[0] for row in calc_rows],
            "values": [float(row[3]) for row in calc_rows],
            "multiSeries": True,
            "metrics": {
                "耦合度C值": [float(row[1]) for row in calc_rows],
                "协调指数T值": [float(row[2]) for row in calc_rows],
                "耦合协调度D值": [float(row[3]) for row in calc_rows],
            },
            "defaultMode": "line",
            "displayModes": [
                {"value": "line", "label": "折线图"},
                {"value": "bar", "label": "柱形图"},
            ],
            "axisLabels": {"x": "评价对象", "y": "数值"},
        },
    }


def _score_columns(df, row_indexes, coupling, t_score, coordination, grade_by_index):
    row_count = len(df)
    row_positions = {row_index: position for position, row_index in enumerate(df.index)}
    columns = [
        ("耦合协调_耦合度C", coupling),
        ("耦合协调_协调指数T", t_score),
        ("耦合协调_协调度D", coordination),
        ("耦合协调_协调等级", pd.Series(grade_by_index)),
    ]
    result = []
    for base_name, series in columns:
        values = [None] * row_count
        for row_index in row_indexes:
            position = row_positions.get(row_index)
            if position is None:
                continue
            value = series.get(row_index)
            values[position] = None if pd.isna(value) else round(float(value), 6)
        result.append({"base_name": base_name, "values": values})
    return result


def _analysis_steps(weight_label, intervalize, has_t_var):
    t_text = "使用用户放入的 0~1 协调指数T变量" if has_t_var else f"按{weight_label}计算协调指数T"
    interval_text = "并将同趋势化结果压缩到 0.01~0.99 区间" if intervalize else "不进行区间化压缩"
    return (
        f"1. 区分正向指标和负向指标，完成同趋势化处理，{interval_text}。\n"
        f"2. {t_text}，T 值反映评价对象的综合发展水平。\n"
        "3. 计算耦合度 C 值，C 值越大，说明系统或指标之间的相互作用越强。\n"
        "4. 计算耦合协调度 D=sqrt(C×T)，D 值同时反映耦合关系和整体发展水平。\n"
        "5. 按 D 值所属区间划分 1~10 个协调等级，并据此判断耦合协调程度。"
    )


def _weight_description(weight_method, weight_label, weights, entropy, divergence, has_t_var):
    top_var = str(weights.sort_values(ascending=False).index[0])
    top_weight = _fmt(weights[top_var] * 100, 3)
    t_note = "由于本次已放入协调指数T变量，权重表主要用于记录指标重要性，不再参与 T 值生成。" if has_t_var else "该权重用于计算协调指数 T。"
    if weight_method == "equal":
        return f"本次采用{weight_label}，各指标或子系统权重相同。{t_note}"
    if weight_method == "entropy":
        entropy_text = _fmt(entropy[top_var], 4) if entropy is not None else "—"
        divergence_text = _fmt(divergence[top_var], 4) if divergence is not None else "—"
        return (
            f"本次采用熵权法确定权重。结果显示，{top_var} 的权重最高（{top_weight}%），"
            f"信息熵值为 {entropy_text}，信息效用值为 {divergence_text}，说明其在当前样本中的区分作用相对更强。{t_note}"
        )
    return (
        f"本次采用自定义权重，权重由研究设计、专家判断或外部模型给定。"
        f"其中 {top_var} 的权重最高（{top_weight}%）。{t_note}"
    )


def _calculation_description(best, worst, valid_count):
    return (
        f"上表以有效样本为单位，按样本顺序列示耦合度 C、协调指数 T、耦合协调度 D 及协调等级。"
        f"结果显示，在 {valid_count} 个有效样本中，{best[0]} 的 D 值最高（D={best[3]}），属于{best[5]}；"
        f"{worst[0]} 的 D 值最低（D={worst[3]}），属于{worst[5]}。"
        "这说明不同评价对象之间的协调发展水平存在差异，D 值越高，系统间相互作用强度与综合发展水平越协调。"
    )


def _grade_rule_description():
    return (
        "等级划分采用 0.1 为步长，将耦合协调度 D 划分为 10 个区间。"
        "等级越高表示耦合协调程度越好，论文报告中应同时呈现 D 值和等级，避免只用等级替代连续数值信息。"
    )


def _grade_summary_description(summary_rows, valid_count):
    if not summary_rows:
        return "未形成有效等级分布。"
    top_row = max(summary_rows, key=lambda row: int(row[2]))
    return (
        f"等级汇总结果显示，本次有效样本量为 N={valid_count}，样本分布最多的协调程度为{top_row[1]}，"
        f"共有 {top_row[2]} 个样本，占比 {top_row[3]}。"
        "该结果表明样本整体协调水平主要集中在上述等级，具体对象差异仍需结合 D 值排序和原始指标表现进一步解释。"
    )


def _score_chart_description():
    return (
        "图中同时展示耦合度 C、协调指数 T 和耦合协调度 D。"
        "其中 C 反映系统间相互作用强度，T 反映综合发展水平，D 为最终协调水平。"
    )


def _academic_interpretation(best, worst, variables, valid_count, weight_label, has_t_var):
    t_source = "外部协调指数T变量" if has_t_var else f"{weight_label}生成的协调指数T"
    return (
        f"结果表明，本次耦合协调度分析共纳入 {valid_count} 个有效样本和 {len(variables)} 个指标或子系统，"
        f"协调指数来源为{t_source}。从 D 值看，{best[0]} 的耦合协调度最高（D={best[3]}），属于{best[5]}，"
        f"说明其在当前评价体系下系统互动关系和综合发展水平相对最好；{worst[0]} 的耦合协调度最低（D={worst[3]}），属于{worst[5]}，"
        "表明其系统协调状态相对较弱。论文写作中，可将 C 值解释为系统间相互作用强度，将 T 值解释为综合发展水平，"
        "将 D 值作为最终耦合协调水平指标；需要注意，本方法反映的是当前样本和指标体系下的相对协调状态，不能直接推断因果关系。"
    )


def _advice(best, worst, valid_count):
    sample_note = "样本量较少时，等级划分更适合做探索性参考；" if valid_count < 30 else ""
    return (
        f"{sample_note}建议重点关注 D 值处于低等级的对象，结合原始指标进一步识别制约协调发展的薄弱环节。"
        f"当前最高对象为 {best[0]}，最低对象为 {worst[0]}；若研究存在明确政策或业务阈值，"
        "可在报告中同时呈现阈值判断和本方法的相对等级结果。"
    )


def run(df, params):
    """
    执行耦合协调度分析。

    @param df: 当前数据集，样本为行、指标或子系统为列
    @param params: positive_vars、negative_vars、coordination_index_var、label_vars、weight_method、weight_var
    @return: 包含配置、样本处理、权重、C/T/D 计算、等级划分、图表和论文式解释的 sections
    """
    params = params or {}
    resolved = _resolve_inputs(df, params)
    if resolved.get("error"):
        return _error(resolved["error"])

    positive_vars = resolved["positive_vars"]
    negative_vars = resolved["negative_vars"]
    groups = resolved["groups"]
    group_labels = resolved["group_labels"]
    all_vars = resolved["all_vars"]
    intervalize = _as_bool(params.get("data_intervalization"), default=True)
    coordination_var = _coordination_index_var(df, params)
    label_vars = _resolve_label_vars(df, params)
    weight_var = _first_resolved(df, params.get("weight_var"))
    weight_method = _clean_choice(params.get("weight_method"), WEIGHT_METHOD_ALIAS, "equal")
    weight_label = WEIGHT_METHOD_MAP[weight_method]["label"]

    if coordination_var and coordination_var in all_vars:
        return _error("协调指数变量不能同时作为评价指标。")
    if weight_method == "custom" and weight_var in all_vars:
        return _error("指标权重列不能同时作为评价指标。")
    if len(group_labels) < 2:
        return _error("耦合协调度至少需要 2 个指标或子系统。")

    required_numeric_vars = all_vars + ([coordination_var] if coordination_var else [])
    numeric = df[required_numeric_vars].apply(pd.to_numeric, errors="coerce")
    complete_mask = numeric.notna().all(axis=1)
    valid_count = int(complete_mask.sum())
    if valid_count < 2:
        return _error("有效样本不足，耦合协调度至少需要 2 条完整样本。")

    data = numeric.loc[complete_mask, all_vars]
    normalized = _directional_normalize(data, positive_vars, negative_vars, intervalize=intervalize)
    subsystem_df = _subsystem_scores(data, normalized, groups, group_labels)
    weights, entropy, divergence, weight_error = _resolve_weights(
        df, subsystem_df, params, group_labels, weight_method, weight_var
    )
    if weight_error:
        return _error(weight_error)

    coupling = _coupling_degree(subsystem_df)
    if coordination_var:
        t_score, t_error = _coordination_index_score(numeric.loc[complete_mask, coordination_var])
        if t_error:
            return _error(t_error)
    else:
        t_score = subsystem_df.mul(weights, axis=1).sum(axis=1)
    coordination = np.sqrt((coupling * t_score).clip(lower=0))

    calc_rows, grade_by_index = _calculation_rows(
        df,
        list(data.index),
        label_vars,
        coupling,
        t_score,
        coordination,
    )
    headers = ["项", "耦合度C值", "协调指数T值", "耦合协调度D值", "协调等级", "耦合协调程度"]
    best = max(calc_rows, key=lambda row: float(row[3]))
    worst = min(calc_rows, key=lambda row: float(row[3]))
    weight_headers, weight_rows = _weight_table(weight_method, group_labels, weights, entropy, divergence)
    grade_summary_rows = _grade_summary_rows(calc_rows)

    config_rows = [
        ["正向指标", "、".join(positive_vars) or "未设置"],
        ["负向指标", "、".join(negative_vars) or "未设置"],
        ["协调指数T", coordination_var or "按指标权重计算"],
        ["标签项", "、".join(label_vars) or "第1项、第2项..."],
        ["数据区间化", "是" if intervalize else "否"],
        ["指标权重", weight_label],
    ]
    if weight_method == "custom":
        config_rows.append(["指标权重列", weight_var or "通过 API 传入"])
    config_rows.append(["输出指标", "耦合协调度D值"])

    sections = [
        _sec_table(
            "算法配置",
            ["项", "值"],
            config_rows,
            description="SPSSGO 采用正向/负向指标入口；未放入协调指数T时，将按指标权重计算 T 值。",
        ),
    ]
    if _as_bool(params.get("include_missing_analysis"), default=False):
        sections.append(_sec_table(
            "样本处理",
            ["项", "样本量"],
            [
                ["原始样本量", str(len(df))],
                ["有效样本量", str(valid_count)],
                ["排除样本量", str(len(df) - valid_count)],
            ],
            description="若某样本在任意评价指标或协调指数T上缺失，该样本不进入耦合协调度计算。",
        ))
    sections.extend([
        _sec_advice(_analysis_steps(weight_label, intervalize, bool(coordination_var)), title="分析步骤"),
        _sec_table(
            "指标权重计算",
            weight_headers,
            weight_rows,
            description=_weight_description(weight_method, weight_label, weights, entropy, divergence, bool(coordination_var)),
        ),
        _sec_table(
            "输出结果1：耦合协调度计算结果",
            headers,
            calc_rows,
            description=_calculation_description(best, worst, valid_count),
        ),
        _sec_charts(
            "输出结果2：耦合协调度图",
            [_score_chart(calc_rows)],
            _score_chart_description(),
        ),
        _sec_table(
            "输出结果3：耦合协调度等级划分",
            ["协调等级", "耦合协调度D值区间", "耦合协调程度"],
            _grade_rule_rows(),
            description=_grade_rule_description(),
        ),
        _sec_table(
            "输出结果4：耦合协调度等级汇总",
            ["协调等级", "耦合协调程度", "频数", "占比"],
            grade_summary_rows,
            description=_grade_summary_description(grade_summary_rows, valid_count),
        ),
        _sec_advice(
            _academic_interpretation(best, worst, group_labels, valid_count, weight_label, bool(coordination_var)),
            title="结果解释",
        ),
        _sec_advice(_advice(best, worst, valid_count)),
        _sec_smart(
            f"耦合协调度分析完成，有效样本量 N={valid_count}；当前最高对象为 {best[0]}，D={best[3]}，协调程度为{best[5]}。"
        ),
        _sec_refs(_REFS_COUPLING),
    ])
    result = {
        "name": METHOD_META["label"],
        "headers": headers,
        "rows": calc_rows,
        "description": f"耦合协调度分析完成，共评估 {valid_count} 个样本，指标权重为{weight_label}。",
        "sections": sections,
    }
    if _as_bool(params.get("save_process"), default=False):
        result["score_columns"] = _score_columns(df, list(data.index), coupling, t_score, coordination, grade_by_index)
    return result
