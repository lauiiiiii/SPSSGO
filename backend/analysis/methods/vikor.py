# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "vikor"
METHOD_META = {'label': '多准则妥协排序法（VIKOR）',
 'category': '综合评价',
 'description': '根据群体效用与个体遗憾构建折中排序',
 'order': 130,
 'slots': [{'key': 'variables', 'label': '评价指标', 'type': 'multiple', 'accept': 'numeric', 'min': 2, 'hint': '放入综合评价指标'}],
 'options': [],
 'param_builder': 'direct'}


def run(df, params):
    variables = _resolve_cols(df, params.get("variables", []))
    if len(variables) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "VIKOR 至少需要 2 个指标。"}
    data = df[variables].apply(pd.to_numeric, errors="coerce").dropna()
    if len(data) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效样本不足。"}

    f_star = data.max(axis=0)
    f_minus = data.min(axis=0)
    denom = (f_star - f_minus).replace(0, np.nan)
    weighted_gap = ((f_star - data) / denom).fillna(0.0) * (1 / len(variables))
    s = weighted_gap.sum(axis=1)
    r = weighted_gap.max(axis=1)
    s_min, s_max = s.min(), s.max()
    r_min, r_max = r.min(), r.max()
    v = 0.5
    q = v * (s - s_min) / (s_max - s_min + 1e-12) + (1 - v) * (r - r_min) / (r_max - r_min + 1e-12)
    rows = [[str(idx), _fmt(s.loc[idx], 4), _fmt(r.loc[idx], 4), _fmt(q.loc[idx], 4)] for idx in q.sort_values(ascending=True).head(10).index]
    sections = [
        _sec_table("VIKOR 排序 Top10", ["样本索引", "S 群体效用", "R 个体遗憾", "Q 折中值"], rows),
        _sec_advice("VIKOR 中 Q 值越小越优，适合用于多指标折中排序场景。"),
        _sec_smart(f"VIKOR 分析完成，当前 Q 值最优的样本索引为 {rows[0][0]}。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": METHOD_META["label"], "headers": ["样本索引", "S 群体效用", "R 个体遗憾", "Q 折中值"], "rows": rows, "description": f"VIKOR 分析完成，共排序 {len(q)} 个样本。", "sections": sections}
