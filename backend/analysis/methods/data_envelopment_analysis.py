# -*- coding: utf-8 -*-
# DEA 这里负责 SPSSAU/SPSSPRO 粒度的线性规划结果编排。
# 统计口径是输入导向 DEA；前端只消费统一 sections 和通用图表协议。
from backend.analysis.common import *

METHOD_KEY = "data_envelopment_analysis"
METHOD_META = {
    "label": "数据包络分析",
    "category": "综合评价",
    "description": "使用 BCC/CCR 模型比较决策单元的相对投入产出效率",
    "order": 40,
    "slots": [
        {
            "key": "input_vars",
            "label": "投入指标",
            "type": "multiple",
            "accept": "numeric",
            "min": 1,
            "hint": "放入投入指标",
        },
        {
            "key": "output_vars",
            "label": "产出指标",
            "type": "multiple",
            "accept": "numeric",
            "min": 1,
            "hint": "放入产出指标",
        },
        {
            "key": "index_var",
            "label": "索引项",
            "type": "single",
            "accept": "any",
            "min": 0,
            "max": 1,
            "required": False,
            "hint": "可选，放入决策单元名称或编号",
        },
    ],
    "options": [
        {
            "key": "dea_type",
            "label": "类型",
            "choices": [
                {"value": "BCC", "label": "BCC（默认）"},
                {"value": "CCR", "label": "CCR"},
            ],
            "default": "BCC",
            "hint": "BCC 为可变规模报酬模型，可拆分技术效益和规模效益；CCR 为固定规模报酬模型。",
        },
        {
            "key": "non_negative_translation",
            "label": "非负平移",
            "type": "checkbox",
            "default": True,
            "hint": "如果有数据小于等于0，此时平移单位为：最小值的绝对值+0.01，保证数据全部为正数可正常计算。",
        },
        {
            "key": "save_efficiency",
            "label": "保存效益",
            "type": "checkbox",
            "default": False,
            "hint": "点击后会新生成标题来保存效益值，选中后每次分析均会得到新标题。",
        },
    ],
    "param_builder": "direct",
}

DEA_REFS = _REFS_GENERAL + [
    "[3] Charnes A, Cooper W W, Rhodes E. Measuring the efficiency of decision making units[J]. European Journal of Operational Research, 1978, 2(6):429-444.",
    "[4] Banker R D, Charnes A, Cooper W W. Some models for estimating technical and scale inefficiencies in data envelopment analysis[J]. Management Science, 1984, 30(9):1078-1092.",
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


def _clean_model_type(params):
    value = str(params.get("dea_type") or params.get("type") or "BCC").strip().upper()
    return "CCR" if value == "CCR" else "BCC"


def _label_for_row(df, row_pos, index_var):
    if index_var:
        value = df.iloc[row_pos][index_var]
        if pd.notna(value) and str(value).strip():
            return str(value).strip()
    return str(row_pos + 1)


def _translate_positive(data, variables, enabled):
    """按 SPSSAU 提示口径处理非正数；不开启时直接卡住，别让 DEA 在脏数据上硬跑。"""
    translations = []
    non_positive = []
    adjusted = data.copy()
    for variable in variables:
        min_value = float(adjusted[variable].min())
        if min_value <= 0:
            if not enabled:
                non_positive.append(variable)
                continue
            shift = abs(min_value) + 0.01
            adjusted[variable] = adjusted[variable] + shift
            translations.append([variable, _fmt(min_value, 4), _fmt(shift, 4)])
    if non_positive:
        return None, translations, f"DEA 要求投入和产出指标均为正数，请勾选非负平移或处理变量：{', '.join(non_positive)}。"
    return adjusted, translations, ""


def _solve_input_oriented(X, Y, dmu_index, returns_to_scale):
    """
    求解输入导向 DEA 包络模型。

    @param X: n*m 投入矩阵
    @param Y: n*s 产出矩阵
    @param dmu_index: 当前决策单元行号
    @param returns_to_scale: crs 对应 CCR，vrs 对应 BCC
    @return: theta、lambda、投入松弛和产出松弛；失败时 success=False
    """
    n, input_count = X.shape
    output_count = Y.shape[1]
    c = np.zeros(n + 1)
    c[0] = 1.0
    a_ub = []
    b_ub = []

    for input_idx in range(input_count):
        row = np.zeros(n + 1)
        row[0] = -X[dmu_index, input_idx]
        row[1:] = X[:, input_idx]
        a_ub.append(row)
        b_ub.append(0.0)

    for output_idx in range(output_count):
        row = np.zeros(n + 1)
        row[1:] = -Y[:, output_idx]
        a_ub.append(row)
        b_ub.append(-Y[dmu_index, output_idx])

    a_eq = None
    b_eq = None
    if returns_to_scale == "vrs":
        a_eq = np.zeros((1, n + 1))
        a_eq[0, 1:] = 1.0
        b_eq = np.array([1.0])

    result = linprog(
        c=c,
        A_ub=np.array(a_ub),
        b_ub=np.array(b_ub),
        A_eq=a_eq,
        b_eq=b_eq,
        bounds=[(0, None)] * (n + 1),
        method="highs",
    )
    if not result.success:
        return {
            "success": False,
            "theta": np.nan,
            "lambdas": np.full(n, np.nan),
            "input_slack": np.full(input_count, np.nan),
            "output_slack": np.full(output_count, np.nan),
            "lambda_sum": np.nan,
        }

    theta = min(max(float(result.x[0]), 0.0), 1.0)
    lambdas = np.array(result.x[1:], dtype=float)
    input_slack = theta * X[dmu_index] - X.T.dot(lambdas)
    output_slack = Y.T.dot(lambdas) - Y[dmu_index]
    input_slack = np.where(np.abs(input_slack) < 1e-7, 0.0, input_slack)
    output_slack = np.where(np.abs(output_slack) < 1e-7, 0.0, output_slack)
    input_slack = np.maximum(input_slack, 0.0)
    output_slack = np.maximum(output_slack, 0.0)
    return {
        "success": True,
        "theta": theta,
        "lambdas": lambdas,
        "input_slack": input_slack,
        "output_slack": output_slack,
        "lambda_sum": float(np.sum(lambdas)),
    }


def _safe_ratio(numerator, denominator):
    if not np.isfinite(numerator) or not np.isfinite(denominator) or denominator <= 0:
        return np.nan
    return min(max(float(numerator) / float(denominator), 0.0), 1.0)


def _validity(efficiency, input_slack, output_slack, tol=1e-5):
    if not np.isfinite(efficiency):
        return "计算失败"
    slack_total = float(np.nansum(input_slack) + np.nansum(output_slack))
    if efficiency >= 1 - tol and slack_total <= tol:
        return "DEA强有效"
    if efficiency >= 1 - tol:
        return "DEA弱有效"
    return "非DEA有效"


def _returns_to_scale(lambda_sum, tol=1e-5):
    if not np.isfinite(lambda_sum):
        return "—"
    if lambda_sum > 1 + tol:
        return "规模报酬递减"
    if lambda_sum < 1 - tol:
        return "规模报酬递增"
    return "规模报酬不变"


def _num(value, digits=6):
    if value is None or not np.isfinite(value):
        return None
    return round(float(value), digits)


def _build_records(X, Y, labels, row_positions, model_type):
    records = []
    for idx, label in enumerate(labels):
        ccr = _solve_input_oriented(X, Y, idx, "crs")
        bcc = _solve_input_oriented(X, Y, idx, "vrs") if model_type == "BCC" else ccr
        overall_eff = ccr["theta"]
        technical_eff = bcc["theta"] if model_type == "BCC" else np.nan
        scale_eff = _safe_ratio(overall_eff, technical_eff) if model_type == "BCC" else np.nan
        slack_source = bcc if model_type == "BCC" else ccr
        records.append({
            "label": label,
            "row_position": int(row_positions[idx]),
            "technical_eff": technical_eff,
            "scale_eff": scale_eff,
            "overall_eff": overall_eff,
            "input_slack": slack_source["input_slack"],
            "output_slack": slack_source["output_slack"],
            "lambda_sum": ccr["lambda_sum"],
            "returns_to_scale": _returns_to_scale(ccr["lambda_sum"]),
            "validity": _validity(overall_eff, slack_source["input_slack"], slack_source["output_slack"]),
            "success": bool(ccr["success"] and slack_source["success"]),
        })
    return records


def _efficiency_rows(records, model_type):
    if model_type == "BCC":
        headers = ["决策单元", "技术效益", "规模效益", "综合效益", "松弛变量S-", "松弛变量S+", "有效性"]
        rows = [
            [
                item["label"],
                _fmt(item["technical_eff"], 3),
                _fmt(item["scale_eff"], 3),
                _fmt(item["overall_eff"], 3),
                _fmt(float(np.nansum(item["input_slack"])), 3),
                _fmt(float(np.nansum(item["output_slack"])), 3),
                item["validity"],
            ]
            for item in records
        ]
        return headers, rows

    headers = ["决策单元", "综合效益", "松弛变量S-", "松弛变量S+", "有效性"]
    rows = [
        [
            item["label"],
            _fmt(item["overall_eff"], 3),
            _fmt(float(np.nansum(item["input_slack"])), 3),
            _fmt(float(np.nansum(item["output_slack"])), 3),
            item["validity"],
        ]
        for item in records
    ]
    return headers, rows


def _scale_table(records, model_type):
    if model_type == "BCC":
        return ["决策单元", "CCR综合效益", "BCC技术效益", "规模效益", "λ合计", "规模报酬"], [
            [
                item["label"],
                _fmt(item["overall_eff"], 3),
                _fmt(item["technical_eff"], 3),
                _fmt(item["scale_eff"], 3),
                _fmt(item["lambda_sum"], 3),
                item["returns_to_scale"],
            ]
            for item in records
        ]
    return ["决策单元", "综合效益", "λ合计", "规模报酬"], [
        [
            item["label"],
            _fmt(item["overall_eff"], 3),
            _fmt(item["lambda_sum"], 3),
            item["returns_to_scale"],
        ]
        for item in records
    ]


def _slack_rows(records, input_vars, output_vars):
    headers = ["决策单元"]
    headers.extend([f"S-({variable})" for variable in input_vars])
    headers.extend([f"S+({variable})" for variable in output_vars])
    rows = []
    for item in records:
        row = [item["label"]]
        row.extend(_fmt(value, 3) for value in item["input_slack"])
        row.extend(_fmt(value, 3) for value in item["output_slack"])
        rows.append(row)
    return headers, rows


def _efficiency_chart(records, model_type):
    labels = [item["label"] for item in records]
    overall_values = [_num(item["overall_eff"]) for item in records]
    if model_type == "BCC":
        metrics = {
            "技术效益": [_num(item["technical_eff"]) for item in records],
            "规模效益": [_num(item["scale_eff"]) for item in records],
            "综合效益": overall_values,
        }
    else:
        metrics = {"综合效益": overall_values}
    return {
        "chartType": "metric_comparison",
        "title": "效益有效性分析",
        "data": {
            "metric": "效益",
            "labels": labels,
            "values": overall_values,
            "multiSeries": True,
            "metrics": metrics,
            "xVariable": "决策单元",
            "defaultMode": "line",
            "displayModes": [
                {"value": "line", "label": "折线图"},
                {"value": "bar", "label": "柱形图"},
                {"value": "horizontalBar", "label": "条形图"},
            ],
        },
    }


def _score_columns(records, row_count, model_type):
    values = [None] * row_count
    for item in records:
        values[item["row_position"]] = _num(item["overall_eff"])
    return [{
        "base_name": "DEA_综合效益" if model_type == "BCC" else "DEA_CCR效率",
        "values": values,
    }]


def run(df, params):
    """
    执行数据包络分析。

    @param df: 当前数据集
    @param params: input_vars、output_vars、index_var、dea_type、non_negative_translation、save_efficiency
    @return: 对齐 SPSSAU/SPSSPRO 粒度的 DEA 结果 sections
    """
    params = params or {}
    input_vars = _resolve_cols(df, _as_list(params.get("input_vars", [])))
    output_vars = _resolve_cols(df, _as_list(params.get("output_vars", [])))
    index_vars = _resolve_cols(df, _as_list(params.get("index_var", [])))
    index_var = index_vars[0] if index_vars else ""
    model_type = _clean_model_type(params)
    translate_enabled = _as_bool(params.get("non_negative_translation"), default=True)

    if not input_vars or not output_vars:
        return _error("DEA 至少需要 1 个投入指标和 1 个产出指标。")

    numeric = df[input_vars + output_vars].apply(pd.to_numeric, errors="coerce")
    complete_mask = numeric.notna().all(axis=1)
    valid_count = int(complete_mask.sum())
    if valid_count < 3:
        return _error("有效样本不足，DEA 至少需要 3 个完整决策单元。")

    row_positions = np.where(complete_mask.to_numpy())[0]
    labels = [_label_for_row(df, int(row_pos), index_var) for row_pos in row_positions]
    clean = numeric.loc[complete_mask, input_vars + output_vars].reset_index(drop=True)
    clean, translations, translate_error = _translate_positive(clean, input_vars + output_vars, translate_enabled)
    if translate_error:
        return _error(translate_error)

    X = clean[input_vars].to_numpy(dtype=float)
    Y = clean[output_vars].to_numpy(dtype=float)
    records = _build_records(X, Y, labels, row_positions, model_type)
    headers, rows = _efficiency_rows(records, model_type)
    scale_headers, scale_rows = _scale_table(records, model_type)
    slack_headers, slack_rows = _slack_rows(records, input_vars, output_vars)
    strong_count = sum(1 for item in records if item["validity"] == "DEA强有效")
    weak_count = sum(1 for item in records if item["validity"] == "DEA弱有效")
    invalid_count = sum(1 for item in records if item["validity"] == "非DEA有效")
    best = max(
        records,
        key=lambda item: item["overall_eff"] if np.isfinite(item["overall_eff"]) else -np.inf,
    )

    sections = [
        _sec_table(
            "算法配置",
            ["项", "值"],
            [
                ["模型类型", model_type],
                ["投入指标", "、".join(input_vars)],
                ["产出指标", "、".join(output_vars)],
                ["索引项", index_var or "使用原始行号"],
                ["非负平移", "开启" if translate_enabled else "关闭"],
            ],
            description="数据包络分析将每条有效样本视为一个决策单元，比较其投入与产出的相对效率。",
        ),
        _sec_table(
            "样本处理",
            ["项", "样本量"],
            [
                ["原始样本量", str(len(df))],
                ["有效样本量", str(valid_count)],
                ["排除样本量", str(len(df) - valid_count)],
            ],
            description="若某样本在任意投入或产出指标上缺失，该样本不进入 DEA 模型。",
        ),
    ]
    if translations:
        sections.append(_sec_table(
            "非负平移处理",
            ["变量", "原最小值", "平移单位"],
            translations,
            description="平移只用于 DEA 计算，原始数据不会被覆盖；平移单位按各变量最小值的绝对值+0.01计算。",
        ))

    sections.extend([
        _sec_table(
            "输出结果1：效益分析表",
            headers,
            rows,
            description=(
                "BCC 模型下，技术效益表示纯技术效率，规模效益=CCR综合效益/BCC技术效益，综合效益为 CCR 效率。"
                if model_type == "BCC"
                else "CCR 模型假设固定规模报酬，综合效益越接近 1 表示相对投入产出越有效。"
            ),
        ),
        _sec_charts(
            "输出结果2：效益有效性分析",
            [_efficiency_chart(records, model_type)],
            "图中 x 轴为决策单元，y 轴为效益值；BCC 模型会同时展示技术效益、规模效益和综合效益。",
        ),
        _sec_table(
            "输出结果3：规模报酬分析",
            scale_headers,
            scale_rows,
            description="λ合计来自 CCR 包络模型；大于1通常对应规模报酬递减，小于1通常对应规模报酬递增，接近1表示规模报酬不变。",
        ),
        _sec_table(
            "输出结果4：松弛变量分析",
            slack_headers,
            slack_rows,
            description="S- 为投入冗余，S+ 为产出不足；综合效益为1且 S-/S+ 均为0时，可判为 DEA 强有效。",
        ),
        _sec_advice(
            "先看综合效益判断整体 DEA 有效性，再结合技术效益和规模效益区分管理技术问题还是规模配置问题；"
            "最后查看松弛变量，定位需要减少的投入或需要提升的产出。"
        ),
        _sec_smart(
            f"DEA 分析完成，有效样本量 N={valid_count}；DEA强有效 {strong_count} 个，DEA弱有效 {weak_count} 个，"
            f"非DEA有效 {invalid_count} 个。综合效益最高的决策单元为 {best['label']}，综合效益={_fmt(best['overall_eff'], 3)}。"
        ),
        _sec_refs(DEA_REFS),
    ])

    result = {
        "name": METHOD_META["label"],
        "headers": headers,
        "rows": rows,
        "description": f"DEA 分析完成，有效样本量 N={valid_count}，模型类型为 {model_type}。",
        "sections": sections,
    }
    if _as_bool(params.get("save_efficiency"), default=False):
        result["score_columns"] = _score_columns(records, len(df), model_type)
    return result
