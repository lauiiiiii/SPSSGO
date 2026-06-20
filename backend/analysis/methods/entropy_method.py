# -*- coding: utf-8 -*-
# 熵值法综合评价入口：只放指标方向统一、熵权计算、综合得分和保存得分列。
# 这里取 SPSSPRO 的正负向指标和报告结构，叠加 SPSSAU 的非负平移选项。
from backend.analysis.common import *

METHOD_KEY = "entropy_method"
METHOD_META = {
    "label": "熵值法",
    "category": "综合评价",
    "description": "依据指标离散程度自动分配客观权重并计算综合得分",
    "order": 90,
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
            "prefixLabel": "索引项",
            "type": "single",
            "accept": "categorical",
            "min": 0,
            "max": 1,
            "required": False,
            "hint": "可选，放入样本名称或编号",
        },
    ],
    "options": [
        {
            "key": "non_negative_translation",
            "label": "非负平移",
            "type": "checkbox",
            "default": False,
            "hint": "如果熵权计算矩阵中有数据小于等于0，平移单位为最小值的绝对值+0.01，保证数据全部为正数后计算。",
        },
        {
            "key": "save_composite_score",
            "label": "保存综合得分",
            "type": "checkbox",
            "default": False,
            "hint": "选中后生成新数据版本，保存本次熵值法综合得分。",
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


def _first_resolved(df, value):
    resolved = _resolve_cols(df, _as_list(value))
    return resolved[0] if resolved else ""


def _unique_preserve(items):
    result = []
    for item in items:
        if item not in result:
            result.append(item)
    return result


def _resolve_inputs(df, params):
    positive_vars = _resolve_cols(df, _as_list(params.get("positive_vars", [])))
    negative_vars = _resolve_cols(df, _as_list(params.get("negative_vars", [])))
    if not positive_vars and not negative_vars:
        positive_vars = _resolve_cols(df, _as_list(params.get("variables", params.get("items", []))))

    duplicate_vars = sorted(set(positive_vars) & set(negative_vars))
    if duplicate_vars:
        return None, None, f"同一指标不能同时作为正向和负向指标：{', '.join(duplicate_vars)}。"

    variables = _unique_preserve(positive_vars + negative_vars)
    return positive_vars, negative_vars, variables


def _directional_normalize(data, positive_vars, negative_vars):
    """正负向指标统一为越大越好；常量列给 1，别让熵权分母后面全挂。"""
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


def _translate_positive(data, variables, enabled):
    """按 SPSSAU 提示做正数平移；平移只进熵权矩阵，不覆盖原始数据。"""
    adjusted = data.copy()
    translations = []
    if not enabled:
        return adjusted, translations

    for variable in variables:
        min_value = float(adjusted[variable].min())
        if min_value <= 0:
            shift = abs(min_value) + 0.01
            adjusted[variable] = adjusted[variable] + shift
            translations.append([variable, _fmt(min_value, 4), _fmt(shift, 4)])
    return adjusted, translations


def _entropy_weights(matrix, variables):
    safe = matrix[variables].clip(lower=0)
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


def _label_for_row(df, row_index, index_var):
    if index_var:
        value = df.loc[row_index, index_var]
        if pd.notna(value) and str(value).strip():
            return str(value).strip()
    return str(row_index)


def _weight_rows(variables, weights, entropy, divergence):
    rows = []
    for variable in variables:
        rows.append([
            variable,
            _fmt(entropy[variable], 3),
            _fmt(divergence[variable], 3),
            _fmt(weights[variable] * 100, 3),
        ])
    return rows


def _score_rows(df, score, rank_series, index_var):
    rows = []
    for row_index, value in score.sort_values(ascending=False).items():
        rows.append([
            _label_for_row(df, row_index, index_var),
            _fmt(value, 6),
            str(int(rank_series.loc[row_index])),
        ])
    return rows


def _weight_chart(rows):
    ordered = sorted(rows, key=lambda row: float(row[3]), reverse=True)
    return {
        "chartType": "metric_comparison",
        "title": "指标重要度直方图",
        "data": {
            "metric": "权重(%)",
            "labels": [row[0] for row in ordered],
            "values": [float(row[3]) for row in ordered],
            "defaultMode": "bar",
            "displayModes": [
                {"value": "bar", "label": "柱形图"},
                {"value": "line", "label": "折线图"},
                {"value": "horizontalBar", "label": "条形图"},
            ],
        },
    }


def _score_columns(df, score):
    row_positions = {row_index: position for position, row_index in enumerate(df.index)}
    values = [None] * len(df)
    for row_index, value in score.items():
        position = row_positions.get(row_index)
        if position is None:
            continue
        values[position] = None if pd.isna(value) else round(float(value), 6)
    return [{"base_name": "CompScore_熵值法", "values": values}]


def _analysis_steps(non_negative_translation):
    translation_text = "开启非负平移，计算矩阵中小于等于0的列按最小值绝对值+0.01平移。" if non_negative_translation else "未开启非负平移，0 值按极小值参与熵值计算。"
    return (
        "1. 剔除任一评价指标缺失的样本，得到有效样本。\n"
        "2. 将正向指标和负向指标统一为越大越好的方向，并消除量纲影响。\n"
        f"3. {translation_text}\n"
        "4. 计算各指标的信息熵值 e、信息效用值 d=1-e，并归一化得到权重。\n"
        "5. 按指标权重汇总综合得分，并按综合得分由高到低排序。"
    )


def run(df, params):
    """
    执行熵值法综合评价。

    @param df: 当前数据集，样本为行、指标为列
    @param params: positive_vars、negative_vars、index_var、non_negative_translation、save_composite_score
    @return: 对齐 SPSSPRO 报告结构，并兼容 SPSSAU 非负平移和保存综合得分选项
    """
    params = params or {}
    positive_vars, negative_vars, variables = _resolve_inputs(df, params)
    if positive_vars is None:
        return _error(variables)

    if len(variables) < 2:
        return _error("熵值法至少需要 2 个正向或负向指标。")

    index_var = _first_resolved(df, params.get("index_var"))
    numeric = df[variables].apply(pd.to_numeric, errors="coerce")
    complete_mask = numeric.notna().all(axis=1)
    valid_count = int(complete_mask.sum())
    if valid_count < 2:
        return _error("有效样本不足，熵值法至少需要 2 条完整样本。")

    data = numeric.loc[complete_mask, variables]
    normalized = _directional_normalize(data, positive_vars, negative_vars)
    translation_enabled = _as_bool(params.get("non_negative_translation"), default=False)
    entropy_matrix, translations = _translate_positive(normalized, variables, translation_enabled)
    weights, entropy, divergence = _entropy_weights(entropy_matrix, variables)
    score = entropy_matrix.mul(weights, axis=1).sum(axis=1)
    rank_series = score.rank(method="min", ascending=False).astype(int)
    weight_rows = _weight_rows(variables, weights, entropy, divergence)
    score_rows = _score_rows(df, score, rank_series, index_var)
    headers = ["项", "信息熵值e", "信息效用值d", "权重(%)"]
    top_weight = max(weight_rows, key=lambda row: float(row[3]))
    best = score_rows[0]

    sections = [
        _sec_table(
            "算法配置",
            ["项", "值"],
            [
                ["正向指标", "、".join(positive_vars) or "未设置"],
                ["负向指标", "、".join(negative_vars) or "未设置"],
                ["索引项", index_var or "使用样本索引"],
                ["非负平移", "开启" if translation_enabled else "关闭"],
                ["保存综合得分", "开启" if _as_bool(params.get("save_composite_score"), default=False) else "关闭"],
            ],
            description="SPSSGO 采用 SPSSPRO 的正负向指标入口，同时保留 SPSSAU 的非负平移和保存综合得分选项。",
        ),
        _sec_table(
            "样本处理",
            ["项", "样本量"],
            [
                ["原始样本量", str(len(df))],
                ["有效样本量", str(valid_count)],
                ["排除样本量", str(len(df) - valid_count)],
            ],
            description="若某样本在任意评价指标上缺失，该样本不进入熵值法计算。",
        ),
        _sec_advice(_analysis_steps(translation_enabled), title="分析步骤"),
    ]
    if translations:
        sections.append(_sec_table(
            "非负平移处理",
            ["变量", "矩阵最小值", "平移单位"],
            translations,
            description="平移只用于熵权计算矩阵，原始数据不会被覆盖；平移单位按各列最小值的绝对值+0.01计算。",
        ))

    sections.extend([
        _sec_table(
            "输出结果1：权重计算结果",
            headers,
            weight_rows,
            description="信息熵值越低、信息效用值越高，指标在当前样本中的区分度通常越强，权重也越高。",
        ),
        _sec_charts(
            "输出结果2：指标重要度直方图",
            [_weight_chart(weight_rows)],
            "图中按权重百分比展示各指标重要度，默认按权重由高到低排序。",
        ),
        _sec_table(
            "输出结果3：综合得分表",
            ["行索引", "综合评价", "排名"],
            score_rows[:15],
            description="综合评价为各指标标准化值按熵值法权重加权求和，数值越大代表综合评价越高；表格仅预览前 15 条结果。",
        ),
        _sec_table(
            "输出结果4：综合得分概况",
            ["指标", "值"],
            [
                ["有效样本量", str(valid_count)],
                ["平均得分", _fmt(score.mean(), 6)],
                ["最大得分", _fmt(score.max(), 6)],
                ["最小得分", _fmt(score.min(), 6)],
            ],
        ),
        _sec_advice(
            "熵值法适合用样本离散程度进行客观赋权。负向指标必须放入负向指标槽；"
            "如果需要把综合得分写回数据集，请勾选保存综合得分。"
        ),
        _sec_smart(
            f"熵值法分析完成，有效样本量 N={valid_count}；权重最高的指标为 {top_weight[0]}（{top_weight[3]}%）。"
            f"综合得分最高的评价对象为 {best[0]}，综合评价={best[1]}，排名第 {best[2]}。"
        ),
        _sec_refs(_REFS_GENERAL),
    ])

    result = {
        "name": METHOD_META["label"],
        "headers": headers,
        "rows": weight_rows,
        "description": f"熵值法完成，共计算 {len(variables)} 个指标的客观权重，有效样本量 N={valid_count}。",
        "sections": sections,
    }
    if _as_bool(params.get("save_composite_score"), default=False):
        result["score_columns"] = _score_columns(df, score)
    return result

