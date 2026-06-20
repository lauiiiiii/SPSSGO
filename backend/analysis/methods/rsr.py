# -*- coding: utf-8 -*-
# RSR/WRSR 单入口，合并 SPSSAU 的简洁输入和 SPSSPRO 的权重、分档输出颗粒度。
# 样本为行、指标为列；普通 RSR 和加权 WRSR 只通过权重方式区分，别拆成两套方法。
from backend.analysis.common import *

METHOD_KEY = "rsr"

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
    "RSR": "equal",
    "rsr": "equal",
    "熵权法": "entropy",
    "entropy_weight": "entropy",
    "entropy": "entropy",
    "熵权": "entropy",
    "自定义权重": "custom",
    "custom": "custom",
    "WRSR": "custom",
    "wrsr": "custom",
}

RANK_METHOD_CHOICES = [
    {"value": "integer", "label": "整次法"},
    {"value": "fractional", "label": "非整次法"},
]
RANK_METHOD_MAP = {item["value"]: item for item in RANK_METHOD_CHOICES}
RANK_METHOD_ALIAS = {
    "整次法": "integer",
    "整秩法": "integer",
    "整数秩": "integer",
    "integer": "integer",
    "rank": "integer",
    "非整次法": "fractional",
    "非整秩方法": "fractional",
    "非整秩法": "fractional",
    "极差换算": "fractional",
    "fractional": "fractional",
    "linear": "fractional",
}

DIVISION_CHOICES = [{"value": str(value), "label": f"{value}档"} for value in range(3, 8)]

GRADE_LABELS = {
    3: ["低水平", "中等水平", "高水平"],
    4: ["较差水平", "一般水平", "先进水平", "领先水平"],
    5: ["很低水平", "较低水平", "一般水平", "较高水平", "很高水平"],
    6: ["很低水平", "较低水平", "中下水平", "中上水平", "较高水平", "很高水平"],
    7: ["很低水平", "较低水平", "中下水平", "中等水平", "中上水平", "较高水平", "很高水平"],
}

METHOD_META = {
    "label": "秩和比综合评价法(RSR/WRSR)",
    "category": "综合评价",
    "description": "通过指标秩次计算 RSR/WRSR 综合得分，支持正负向指标、权重和 Probit 分档",
    "order": 60,
    "aliases": ["RSR", "WRSR", "WRSR秩和比", "秩和比", "秩和比综合评价法"],
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
            "key": "index_var",
            "label": "变量",
            "prefixLabel": "标签",
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
            "key": "rank_method",
            "label": "编秩方法",
            "choices": RANK_METHOD_CHOICES,
            "default": "integer",
            "hint": "整次法按样本排序秩次计算，并列值取平均秩；非整次法按极差线性换算为非整秩。",
        },
        {
            "key": "division_count",
            "label": "分档数量",
            "choices": DIVISION_CHOICES,
            "default": "3",
            "hint": "支持 3-7 档；分档阈值基于 Probit 回归结果生成。",
        },
        {
            "key": "weight_method",
            "label": "变量权重",
            "choices": WEIGHT_METHOD_CHOICES,
            "default": "equal",
            "hint": "不设置权重为普通 RSR；熵权法和自定义权重为加权 WRSR。",
        },
    ],
    "param_builder": "direct",
}

_REFS_RSR = _REFS_GENERAL + [
    "[3] 田凤调. 秩和比法及其应用[M]. 北京：中国统计出版社，1993.",
    "[4] 孙振球. 医学综合评价方法及其应用[M]. 北京：化学工业出版社，2006.",
    "[5] 方积乾. 卫生统计学[M]. 7版. 北京：人民卫生出版社，2012.",
    "[6] Nardo M, Saisana M, Saltelli A, Tarantola S, Hoffman A, Giovannini E. Handbook on Constructing Composite Indicators: Methodology and User Guide[M]. Paris: OECD Publishing, 2008.",
    "[7] Shannon C E. A mathematical theory of communication[J]. Bell System Technical Journal, 1948, 27(3):379-423; 27(4):623-656.",
    "[8] Finney D J. Probit Analysis[M]. 3rd ed. Cambridge: Cambridge University Press, 1971.",
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
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on", "是", "勾选"}


def _clean_choice(value, alias_map, default):
    if value in (None, ""):
        return default
    text = str(value).strip()
    if text in alias_map:
        return alias_map[text]
    return alias_map.get(text.lower(), default)


def _clean_division_count(value):
    try:
        count = int(value)
    except (TypeError, ValueError):
        count = 3
    return min(max(count, 3), 7)


def _first_resolved(df, value):
    resolved = _resolve_cols(df, _as_list(value))
    return resolved[0] if resolved else ""


def _unique_preserve(items):
    result = []
    for item in items:
        if item not in result:
            result.append(item)
    return result


def _label_for_row(df, row_index, index_var):
    if index_var:
        value = df.loc[row_index, index_var]
        if pd.notna(value) and str(value).strip():
            return str(value).strip()
    return str(row_index)


def _score_name(weight_method):
    return "RSR值" if weight_method == "equal" else "WRSR值"


def _score_label_text(score_label):
    return str(score_label).replace("WRSR值", "WRSR 值").replace("RSR值", "RSR 值")


def _distribution_metric_name(score_label):
    return "WRSR分布值" if str(score_label).startswith("WRSR") else "RSR分布值"


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


def _directional_normalize(data, positive_vars, negative_vars):
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


def _directional_ranks(data, positive_vars, negative_vars, rank_method):
    ranks = pd.DataFrame(index=data.index)
    if rank_method == "integer":
        for variable in positive_vars:
            ranks[variable] = data[variable].rank(method="average", ascending=True)
        for variable in negative_vars:
            ranks[variable] = data[variable].rank(method="average", ascending=False)
        return ranks.astype(float)

    n = len(data)
    neutral_rank = (n + 1) / 2
    for variable in positive_vars + negative_vars:
        series = pd.to_numeric(data[variable], errors="coerce").astype(float)
        min_value = float(series.min())
        max_value = float(series.max())
        spread = max_value - min_value
        if spread == 0:
            ranks[variable] = neutral_rank
        elif variable in negative_vars:
            ranks[variable] = 1 + (n - 1) * (max_value - series) / spread
        else:
            ranks[variable] = 1 + (n - 1) * (series - min_value) / spread
    return ranks.astype(float)


def _calculate_score(ranks, weights):
    n = len(ranks)
    return ranks.mul(weights, axis=1).sum(axis=1) / n


def _weight_table(weight_method, variables, weights, entropy, divergence):
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


def _distribution_records(score):
    n = len(score)
    counts = score.groupby(score.round(12)).size().sort_index()
    records = []
    cumulative = 0
    for value, frequency in counts.items():
        start = cumulative + 1
        cumulative += int(frequency)
        average_rank = (start + cumulative) / 2
        probability = average_rank / n
        if cumulative == n:
            # 最大累计概率不能取 1，不然 Probit 会变成无穷大。
            probability = 1 - 1 / (4 * n)
        probability = min(max(probability, 1e-6), 1 - 1e-6)
        records.append({
            "score": float(value),
            "frequency": int(frequency),
            "cumulative": int(cumulative),
            "average_rank": float(average_rank),
            "percent": probability * 100,
            "probit": float(stats.norm.ppf(probability) + 5),
        })
    return records


def _distribution_rows(records, score_label):
    return [
        [
            _fmt(record["score"], 6),
            str(record["frequency"]),
            str(record["cumulative"]),
            _fmt(record["average_rank"], 3),
            _fmt(record["percent"], 3),
            _fmt(record["probit"], 6),
        ]
        for record in records
    ]


def _fit_probit_regression(records):
    if len(records) < 2:
        return None
    x = np.array([record["probit"] for record in records], dtype=float)
    y = np.array([record["score"] for record in records], dtype=float)
    if len(np.unique(x)) < 2 or len(np.unique(y)) < 2:
        return None
    try:
        model = sm.OLS(y, sm.add_constant(x)).fit()
    except Exception:
        return None
    params = model.params
    bse = model.bse
    tvalues = model.tvalues
    pvalues = model.pvalues
    beta = np.corrcoef(x, y)[0, 1] if len(x) > 1 else np.nan
    return {
        "intercept": float(params[0]),
        "slope": float(params[1]),
        "intercept_se": float(bse[0]),
        "slope_se": float(bse[1]),
        "intercept_t": float(tvalues[0]),
        "slope_t": float(tvalues[1]),
        "intercept_p": float(pvalues[0]),
        "slope_p": float(pvalues[1]),
        "beta": float(beta),
        "r2": float(model.rsquared),
        "adj_r2": float(model.rsquared_adj),
        "f": _safe_float(model.fvalue),
        "f_p": _safe_float(model.f_pvalue),
        "df_model": int(model.df_model),
        "df_resid": int(model.df_resid),
    }


def _p_decimal(p):
    return _fmt(p, 3)


def _f_summary(regression):
    if not regression or np.isnan(regression["f"]):
        return "—"
    return f"F ({regression['df_model']},{regression['df_resid']})={_fmt(regression['f'], 3)},p={_p_decimal(regression['f_p'])}"


def _regression_headers():
    return ["项", "B", "标准误", "Beta", "t", "p", "R²", "调整R²", "F"]


def _regression_header_rows():
    return [
        [
            {"text": "项", "rowspan": 2},
            {"text": "非标准化系数", "colspan": 2},
            {"text": "标准化系数", "colspan": 1},
            {"text": "t", "rowspan": 2},
            {"text": "p", "rowspan": 2},
            {"text": "R²", "rowspan": 2},
            {"text": "调整R²", "rowspan": 2},
            {"text": "F", "rowspan": 2},
        ],
        ["B", "标准误", "Beta"],
    ]


def _regression_rows(regression):
    if not regression:
        return [["Probit回归", "有效分布点不足，未拟合", "—", "—", "—", "—", "—", "—", "—"]]
    return [
        [
            "常数",
            _fmt(regression["intercept"], 3),
            _fmt(regression["intercept_se"], 3),
            "—",
            _fmt(regression["intercept_t"], 3),
            _p_decimal(regression["intercept_p"]),
            {"text": _fmt(regression["r2"], 3), "rowspan": 2},
            {"text": _fmt(regression["adj_r2"], 3), "rowspan": 2},
            {"text": _f_summary(regression), "rowspan": 2},
        ],
        [
            "Probit值",
            _fmt(regression["slope"], 3),
            _fmt(regression["slope_se"], 3),
            _fmt(regression["beta"], 3),
            _fmt(regression["slope_t"], 3),
            _p_decimal(regression["slope_p"]),
        ],
    ]


def _regression_section(regression, score_label):
    distribution_metric = _distribution_metric_name(score_label)
    section = _sec_table(
        "输出结果6：回归模型表格",
        _regression_headers(),
        _regression_rows(regression),
        note=f"备注：因变量 = {distribution_metric}",
        description=_regression_description(regression, score_label),
    )
    section["headerRows"] = _regression_header_rows()
    if regression:
        section["bodyRowspanColumns"] = 1
    return section


def _grade_thresholds(score, division_count, regression):
    probabilities = [idx / division_count for idx in range(1, division_count)]
    thresholds = []
    for probability in probabilities:
        probit = float(stats.norm.ppf(probability) + 5)
        if regression:
            threshold = regression["intercept"] + regression["slope"] * probit
        else:
            threshold = float(score.quantile(probability))
        thresholds.append({
            "probability": probability,
            "probit": probit,
            "score": float(threshold),
        })
    return thresholds


def _grade_for_score(value, thresholds, labels):
    for index, threshold in enumerate(thresholds):
        if value <= threshold["score"]:
            return labels[index]
    return labels[-1]


def _grade_rule_rows(thresholds, labels, score_label):
    rows = []
    lower = "-∞"
    for index, threshold in enumerate(thresholds):
        upper = _fmt(threshold["score"], 4)
        rows.append([
            labels[index],
            lower,
            upper,
            _fmt(threshold["probit"], 4),
            f"{score_label} ≤ {upper}" if index == 0 else f"{lower} < {score_label} ≤ {upper}",
        ])
        lower = upper
    rows.append([
        labels[-1],
        lower,
        "+∞",
        "—",
        f"{score_label} > {lower}",
    ])
    return rows


def _rank_rows(df, score, index_var, score_label, grade_by_index):
    rank_series = score.rank(method="min", ascending=False).astype(int)
    ordered = score.sort_values(ascending=False)
    rows = []
    for row_index, value in ordered.items():
        rows.append([
            _label_for_row(df, row_index, index_var),
            _fmt(value, 6),
            str(int(rank_series.loc[row_index])),
            grade_by_index[row_index],
        ])
    return rows, rank_series


def _rank_label(score_label):
    return "WRSR排名" if str(score_label).startswith("WRSR") else "RSR排名"


def _calculation_table(df, variables, ranks, score, rank_series, index_var, score_label):
    rank_label = _rank_label(score_label)
    headers = ["项", *variables, score_label, rank_label]
    header_rows = [
        ["项", *variables, score_label, rank_label],
        ["", *(["[秩]"] * len(variables)), "", ""],
    ]

    rows = []
    for row_index in score.index:
        row = [_label_for_row(df, row_index, index_var)]
        for variable in variables:
            row.append(_fmt(ranks.loc[row_index, variable], 3))
        row.extend([
            _fmt(score.loc[row_index], 3),
            str(int(rank_series.loc[row_index])),
        ])
        rows.append(row)
    return headers, header_rows, rows


def _calculation_section(headers, header_rows, rows, score_label, rank_label):
    section = _sec_table(
        f"{score_label}计算表格",
        headers,
        rows,
        description=_calculation_description(score_label, rank_label),
    )
    section["headerRows"] = header_rows
    return section


def _grade_summary_rows(rank_rows):
    total = len(rank_rows)
    counts = {}
    for row in rank_rows:
        counts[row[3]] = counts.get(row[3], 0) + 1
    return [[label, str(count), _fmt(count / total * 100 if total else 0, 2) + "%"] for label, count in counts.items()]


def _weight_description(weight_method, weight_label, weights, entropy, divergence):
    top_var = str(weights.sort_values(ascending=False).index[0])
    top_weight = _fmt(weights[top_var] * 100, 3)
    if weight_method == "equal":
        return (
            f"本次采用{weight_label}，各评价指标在综合评价中具有相同重要性。"
            "该设定适用于研究者希望避免主观或客观赋权影响、仅依据指标秩次进行综合评价的场景。"
        )
    if weight_method == "entropy":
        entropy_text = _fmt(entropy[top_var], 4) if entropy is not None else "—"
        divergence_text = _fmt(divergence[top_var], 4) if divergence is not None else "—"
        return (
            f"本次采用熵权法确定指标权重。熵权法依据指标离散程度赋权，信息熵值越低、信息效用值越高，指标区分度通常越强。"
            f"结果显示，{top_var} 的权重最高（{top_weight}%），其信息熵值为 {entropy_text}，信息效用值为 {divergence_text}，"
            "说明该指标在当前样本中对综合评价结果的区分作用相对更大。"
        )
    return (
        f"本次采用自定义权重计算 WRSR，权重由研究设计、专家判断或外部模型给定。"
        f"其中 {top_var} 的权重最高（{top_weight}%），解释结果时应同时说明权重来源及其理论依据。"
    )


def _calculation_description(score_label, rank_label):
    score_text = _score_label_text(score_label)
    rank_note = (
        "整次法按样本排序得到 1 到 N 的秩次，并列值取平均秩"
        if rank_label == "整次法"
        else "非整次法按指标极差线性换算为 1 到 N 的非整秩"
    )
    return (
        f"{score_text}计算表格列示各评价对象在每个指标上的转换秩次、最终 {score_text}及排名。"
        f"本次采用{rank_label}，{rank_note}；正向指标按数值越大秩次越高处理，负向指标按数值越小秩次越高处理。"
        f"{score_text}越大，表示评价对象在当前指标体系下的相对综合表现越好。"
    )


def _ranking_description(score_label, best, worst, valid_count):
    score_text = _score_label_text(score_label)
    return (
        f"排序结果表明，在 {valid_count} 个有效样本中，{best[0]} 的 {score_text}最高（{best[1]}），"
        f"综合评价排序第 {best[2]}，分档为{best[3]}；{worst[0]} 的 {score_text}最低（{worst[1]}），"
        f"综合评价排序第 {worst[2]}，分档为{worst[3]}。该结果反映样本内部的相对优劣，"
        "论文解释时应结合指标含义、样本来源和研究问题进行讨论。"
    )


def _distribution_description(score_label, records, valid_count):
    score_text = _score_label_text(score_label)
    return (
        f"分布表将相同 {score_text}的样本合并，计算频数、累计频数、平均秩次、累计频率和 Probit 值，"
        f"用于后续线性回归和分档阈值估计。本次 {valid_count} 个有效样本形成 {len(records)} 个分布点；"
        "最大累计频率采用 1-1/(4N) 修正，以避免 Probit 转换出现无穷值。"
    )


def _fit_description(regression, score_label):
    if not regression:
        return "有效分布点不足，未生成拟合效果图。此时分档结果主要依据样本分位数，解释时应降低拟合结论的权重。"
    score_text = _score_label_text(score_label)
    return (
        f"拟合效果图以排序序号为横轴、{score_text}为纵轴，展示实际值与 Probit 回归预测值的变化趋势。"
        "两条曲线走势越接近，说明回归模型对 RSR/WRSR 分布趋势的刻画越充分；若局部偏离较大，"
        "则说明部分样本的综合评价水平与线性拟合趋势存在差异，后续解释应结合原始指标表现进一步核查。"
    )


def _regression_description(regression, score_label):
    if not regression:
        return "有效分布点不足，未进行 Probit 线性回归；分档阈值退化为样本分位数阈值。"
    slope_judgement = "达到常用显著性水平" if regression["slope_p"] < 0.05 else "未达到常用显著性水平"
    f_judgement = "模型整体通过显著性检验" if regression["f_p"] < 0.05 else "模型整体未通过常用显著性检验"
    distribution_metric = _distribution_metric_name(score_label)
    return (
        "Probit 线性回归用于检验 RSR/WRSR 分布值与累计概率正态转换值之间的线性关系，并为分档阈值提供依据。"
        f"本次回归方程为 {distribution_metric} = {_fmt(regression['intercept'], 4)} + {_fmt(regression['slope'], 4)} × Probit值；"
        f"模型 R²={_fmt(regression['r2'], 3)}，调整 R²={_fmt(regression['adj_r2'], 3)}，F 检验 {_p_expr(regression['f_p'])}，{f_judgement}；"
        f"Probit 项 {_p_expr(regression['slope_p'])}，{slope_judgement}。"
    )


def _grade_rule_description(score_label, division_count, regression):
    basis = "Probit 回归预测值" if regression else "样本分位数"
    score_text = _score_label_text(score_label)
    return (
        f"分档规则依据{basis}生成，将评价对象划分为 {division_count} 个等级。"
        f"判定时以 {score_text}所处区间确定对应分档，数值越高通常对应越优等级。"
        "论文报告中应同时呈现分档规则和排序结果，避免仅凭等级忽略同一等级内部的得分差异。"
    )


def _grade_summary_description(rank_rows, grade_labels):
    total = len(rank_rows)
    counts = {label: 0 for label in grade_labels}
    for row in rank_rows:
        counts[row[3]] = counts.get(row[3], 0) + 1
    high_label = grade_labels[-1]
    low_label = grade_labels[0]
    return (
        f"分档汇总显示，{high_label}共有 {counts.get(high_label, 0)} 个样本，占比 "
        f"{_fmt(counts.get(high_label, 0) / total * 100 if total else 0, 2)}%；"
        f"{low_label}共有 {counts.get(low_label, 0)} 个样本，占比 "
        f"{_fmt(counts.get(low_label, 0) / total * 100 if total else 0, 2)}%。"
        "该结果可用于概括样本整体水平分布，但不替代对关键样本和关键指标的进一步解释。"
    )


def _academic_interpretation(score_label, best, worst, variables, valid_count, division_count, weight_label):
    score_text = _score_label_text(score_label)
    return (
        f"结果表明，本次 RSR/WRSR 综合评价共纳入 {valid_count} 个有效样本和 {len(variables)} 个评价指标，"
        f"变量权重采用{weight_label}，并划分为 {division_count} 个等级。"
        f"从综合排序看，{best[0]} 的 {score_text}最高（{best[1]}），属于{best[3]}，表明其在当前指标体系下综合表现最优；"
        f"{worst[0]} 的 {score_text}最低（{worst[1]}），属于{worst[3]}，表明其相对综合表现较弱。"
        "在论文写作中，可将 RSR/WRSR 作为综合评价的相对得分，并结合排序、分档和指标权重报告评价对象的优劣水平；"
        "需要注意，该方法反映的是当前样本和指标体系下的相对评价结果，不能直接解释为绝对绩效或因果效应。"
    )


def _score_chart(rows, score_label):
    top_rows = rows[:30]
    return {
        "chartType": "metric_comparison",
        "title": f"{score_label}排序",
        "data": {
            "metric": score_label,
            "labels": [row[0] for row in top_rows],
            "values": [float(row[1]) for row in top_rows],
            "defaultMode": "bar",
            "displayModes": [
                {"value": "bar", "label": "柱形图"},
                {"value": "line", "label": "折线图"},
                {"value": "horizontalBar", "label": "条形图"},
            ],
        },
    }


def _grade_chart(rank_rows):
    total = len(rank_rows)
    counts = {}
    for row in rank_rows:
        counts[row[3]] = counts.get(row[3], 0) + 1
    labels = list(counts.keys())
    values = [counts[label] for label in labels]
    return {
        "chartType": "category_distribution",
        "title": "分档分布",
        "data": {
            "variable": "分档",
            "labels": labels,
            "counts": values,
            "percents": [round(value / total * 100, 4) if total else 0 for value in values],
            "total": total,
            "defaultMode": "bar",
        },
    }


def _fit_chart(score, records, regression, score_label):
    if not regression:
        return None
    probit_by_score = {round(record["score"], 12): record["probit"] for record in records}
    ordered = score.sort_values(ascending=True)
    labels = [str(index + 1) for index in range(len(ordered))]
    actual = [round(float(value), 6) for value in ordered.tolist()]
    predicted = []
    for value in ordered.tolist():
        probit = probit_by_score.get(round(float(value), 12))
        predicted.append(round(regression["intercept"] + regression["slope"] * probit, 6))
    return {
        "chartType": "metric_comparison",
        "title": "拟合效果图",
        "data": {
            "metric": score_label,
            "labels": labels,
            "values": actual,
            "multiSeries": True,
            "metrics": {"实际值": actual, "预测值": predicted},
            "defaultMode": "line",
            "displayModes": [
                {"value": "line", "label": "折线图"},
                {"value": "bar", "label": "柱形图"},
            ],
            "axisLabels": {"x": "排序序号", "y": score_label},
        },
    }


def _analysis_steps(weight_label, rank_label, division_count):
    rank_note = "样本排序秩次" if rank_label == "整次法" else "极差线性换算秩次"
    return (
        "1. 区分正向指标和负向指标，正向指标越大越优，负向指标越小越优。\n"
        f"2. 按{rank_label}把各指标转换为{rank_note}，并按{weight_label}生成权重。\n"
        "3. 普通 RSR 使用等权秩和比；熵权法或自定义权重会计算 WRSR。\n"
        f"4. 汇总 RSR/WRSR 分布，计算累计频率、Probit 值，并按 {division_count} 档生成分档阈值。\n"
        "5. 按 RSR/WRSR 值由大到小排序，值越大表示综合评价越高。"
    )


def _advice(score_label, best, worst, division_count, valid_count):
    sample_note = "；样本量偏少，分档结果更适合做内部排序参考" if valid_count < 30 else ""
    return (
        f"本次使用 {score_label} 作为综合评价指标，共划分 {division_count} 档{sample_note}。"
        f"当前综合评价最高的是 {best[0]}，最低的是 {worst[0]}。"
        "如果研究需要复现普通 RSR，请保持变量权重为不设置权重；如果需要体现指标重要性差异，再使用熵权法或自定义权重。"
    )


def run(df, params):
    """
    执行 RSR/WRSR 综合评价。

    @param df: 当前数据集，样本为行、评价指标为列
    @param params: positive_vars、negative_vars、index_var、rank_method、division_count、weight_method、weight_var
    @return: 包含权重、秩次、RSR/WRSR、Probit 回归和分档结果的 sections
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
    weight_method = _clean_choice(params.get("weight_method"), WEIGHT_METHOD_ALIAS, "equal")
    rank_method = _clean_choice(params.get("rank_method"), RANK_METHOD_ALIAS, "integer")
    division_count = _clean_division_count(params.get("division_count", 3))
    weight_label = WEIGHT_METHOD_MAP[weight_method]["label"]
    rank_label = RANK_METHOD_MAP[rank_method]["label"]
    score_label = _score_name(weight_method)

    if weight_method == "custom" and weight_var in variables:
        return _error("指标权重列不能同时作为评价指标。")
    if len(variables) < 2:
        return _error("RSR/WRSR 至少需要 2 个正向或负向指标。")

    numeric = df[variables].apply(pd.to_numeric, errors="coerce")
    complete_mask = numeric.notna().all(axis=1)
    valid_count = int(complete_mask.sum())
    if valid_count < 2:
        return _error("有效样本不足，RSR/WRSR 至少需要 2 条完整样本。")

    data = numeric.loc[complete_mask, variables]
    normalized = _directional_normalize(data, positive_vars, negative_vars)
    weights, entropy, divergence, weight_error = _resolve_weights(
        df, normalized, params, variables, weight_method, weight_var
    )
    if weight_error:
        return _error(weight_error)

    ranks = _directional_ranks(data, positive_vars, negative_vars, rank_method)
    score = _calculate_score(ranks[variables], weights)
    distribution = _distribution_records(score)
    regression = _fit_probit_regression(distribution)
    thresholds = _grade_thresholds(score, division_count, regression)
    grade_labels = GRADE_LABELS[division_count]
    grade_by_index = {
        row_index: _grade_for_score(float(value), thresholds, grade_labels)
        for row_index, value in score.items()
    }

    rows, rank_series = _rank_rows(df, score, index_var, score_label, grade_by_index)
    calc_headers, calc_header_rows, calc_rows = _calculation_table(
        df, variables, ranks, score, rank_series, index_var, score_label
    )
    weight_headers, weight_rows = _weight_table(weight_method, variables, weights, entropy, divergence)
    headers = ["评价对象", score_label, "排序结果", "分档"]
    best = rows[0]
    worst = rows[-1]
    fit_chart = _fit_chart(score, distribution, regression, score_label)
    summary_charts = [_score_chart(rows, score_label), _grade_chart(rows)]

    config_rows = [
        ["正向指标", "、".join(positive_vars) or "未设置"],
        ["负向指标", "、".join(negative_vars) or "未设置"],
        ["索引项", index_var or "使用样本索引"],
        ["编秩方法", rank_label],
        ["分档数量", f"{division_count}档"],
        ["变量权重", weight_label],
    ]
    if weight_method == "custom":
        config_rows.append(["指标权重列", weight_var or "通过 API 传入"])
    config_rows.append(["输出指标", score_label])

    sections = [
        _sec_table(
            "算法配置",
            ["项", "值"],
            config_rows,
            description="SPSSGO 将普通 RSR 和加权 WRSR 合并为一个入口：不设置权重为 RSR，设置权重后为 WRSR。",
        ),
        _sec_table(
            "样本处理",
            ["项", "样本量"],
            [
                ["原始样本量", str(len(df))],
                ["有效样本量", str(valid_count)],
                ["排除样本量", str(len(df) - valid_count)],
            ],
            description="若某样本在任意评价指标上缺失，该样本不进入 RSR/WRSR 计算。",
        ),
        _sec_advice(_analysis_steps(weight_label, rank_label, division_count), title="分析步骤"),
        _sec_table(
            "输出结果1：指标权重计算",
            weight_headers,
            weight_rows,
            description=_weight_description(weight_method, weight_label, weights, entropy, divergence),
        ),
        _calculation_section(calc_headers, calc_header_rows, calc_rows, score_label, rank_label),
        _sec_table(
            "输出结果3：RSR/WRSR排序结果",
            headers,
            rows,
            description=_ranking_description(score_label, best, worst, valid_count),
        ),
        _sec_table(
            "输出结果4：RSR/WRSR分布表",
            [score_label, "频数", "累计频数", "平均秩次", "累计频率(%)", "Probit值"],
            _distribution_rows(distribution, score_label),
            description=_distribution_description(score_label, distribution, valid_count),
        ),
        _sec_charts(
            "输出结果5：拟合效果图",
            [fit_chart] if fit_chart else [],
            _fit_description(regression, score_label),
        ),
        _regression_section(regression, score_label),
        _sec_table(
            "输出结果7：分档规则",
            ["分档", "下界", "上界", "边界Probit", "判定规则"],
            _grade_rule_rows(thresholds, grade_labels, score_label),
            description=_grade_rule_description(score_label, division_count, regression),
        ),
        _sec_table(
            "输出结果8：分档汇总",
            ["分档", "频数", "占比"],
            _grade_summary_rows(rows),
            description=_grade_summary_description(rows, grade_labels),
        ),
        _sec_charts(
            "输出结果9：综合评价图",
            summary_charts,
            "图中展示综合评价排序和分档分布。",
        ),
        _sec_advice(
            _academic_interpretation(score_label, best, worst, variables, valid_count, division_count, weight_label),
            title="结果解释",
        ),
        _sec_advice(_advice(score_label, best, worst, division_count, valid_count)),
        _sec_smart(
            f"RSR/WRSR 综合评价完成，有效样本量 N={valid_count}；当前最高评价对象为 {best[0]}，"
            f"{score_label}={best[1]}，排序第 {best[2]}，分档为{best[3]}。"
        ),
        _sec_refs(_REFS_RSR),
    ]
    return {
        "name": METHOD_META["label"],
        "headers": headers,
        "rows": rows,
        "description": f"RSR/WRSR 综合评价完成，共评估 {valid_count} 个样本，变量权重为{weight_label}。",
        "sections": sections,
    }
