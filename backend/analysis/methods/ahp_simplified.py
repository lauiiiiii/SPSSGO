# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "ahp_simplified"
METHOD_META = {'label': '层次分析法（AHP简化版）',
 'category': '综合评价',
 'description': '基于指标平均重要度近似构造判断矩阵并计算权重',
 'order': 20,
 'slots': [{'key': 'variables', 'label': '准则指标', 'type': 'multiple', 'accept': 'numeric', 'min': 2, 'hint': '放入用于构造 AHP 权重的准则变量'}],
 'options': [],
 'param_builder': 'direct'}

_RI_TABLE = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.9, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}


def _ahp_from_means(data):
    means = data.mean().abs().replace(0, 1e-6)
    matrix = pd.DataFrame(index=means.index, columns=means.index, dtype=float)
    for i in means.index:
        for j in means.index:
            matrix.loc[i, j] = float(means[i] / means[j])
    eigvals, eigvecs = np.linalg.eig(matrix.values)
    max_idx = int(np.argmax(eigvals.real))
    lambda_max = float(eigvals.real[max_idx])
    weights = np.abs(eigvecs[:, max_idx].real)
    weights = weights / weights.sum()
    weight_series = pd.Series(weights, index=means.index)
    n = len(means)
    ci = (lambda_max - n) / (n - 1) if n > 2 else 0.0
    ri = _RI_TABLE.get(n, 1.49)
    cr = ci / ri if ri not in (0, 0.0) else 0.0
    return matrix, weight_series, lambda_max, ci, cr


def run(df, params):
    variables = _resolve_cols(df, params.get("variables", []))
    if len(variables) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "AHP 简化版至少需要 2 个准则变量。"}
    data = df[variables].apply(pd.to_numeric, errors="coerce").dropna()
    if len(data) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效样本不足。"}

    matrix, weights, lambda_max, ci, cr = _ahp_from_means(data)
    normalized = _normalize_benefit_frame(data)
    score = normalized.mul(weights, axis=1).sum(axis=1)
    rows = [[var, _fmt(weights[var], 4)] for var in weights.sort_values(ascending=False).index]
    matrix_rows = [[idx] + [_fmt(matrix.loc[idx, col], 4) for col in matrix.columns] for idx in matrix.index]
    sections = [
        _sec_table("AHP 权重结果", ["准则", "权重"], rows),
        _sec_table("一致性检验", ["指标", "值"], [["λmax", _fmt(lambda_max, 4)], ["CI", _fmt(ci, 4)], ["CR", _fmt(cr, 4)], ["是否通过", "是" if cr < 0.1 else "否"]]),
        _sec_table("判断矩阵", ["准则"] + list(matrix.columns), matrix_rows),
        _sec_table("综合得分 Top10", ["样本索引", "综合得分"], _score_top10_rows(score)),
        _sec_advice("AHP 简化版当前根据指标均值近似构造判断矩阵，适合快速得到权重参考。"),
        _sec_smart(f"AHP 简化版完成，权重最高的准则为 {weights.sort_values(ascending=False).index[0]}。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": METHOD_META["label"], "headers": ["准则", "权重"], "rows": rows, "description": f"AHP 简化版完成，共计算 {len(variables)} 个准则权重。", "sections": sections}
