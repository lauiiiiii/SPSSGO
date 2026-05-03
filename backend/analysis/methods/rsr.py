# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "rsr"
METHOD_META = {'label': '秩和比综合评价法(RSR)',
 'category': '综合评价',
 'description': '通过指标排序后的秩和比值进行综合评价',
 'order': 60,
 'slots': [{'key': 'variables', 'label': '评价指标', 'type': 'multiple', 'accept': 'numeric', 'min': 2, 'hint': '放入综合评价指标'}],
 'options': [],
 'param_builder': 'direct'}


def run(df, params):
    variables = _resolve_cols(df, params.get("variables", []))
    if len(variables) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "RSR 至少需要 2 个指标。"}
    data = df[variables].apply(pd.to_numeric, errors="coerce").dropna()
    if len(data) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效样本不足。"}

    ranks = data.rank(axis=0, method="average", ascending=True)
    rsr = ranks.sum(axis=1) / (len(variables) * len(data))
    rows = [[str(idx), _fmt(rsr.loc[idx], 4)] for idx in rsr.sort_values(ascending=False).head(10).index]
    sections = [
        _sec_table("RSR 排序 Top10", ["样本索引", "RSR 值"], rows),
        _sec_advice("RSR 值越大，说明样本在整体排序中越靠前。当前版本按所有指标均为正向指标处理。"),
        _sec_smart(f"RSR 综合评价完成，当前排序最高的样本索引为 {rows[0][0]}。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": METHOD_META["label"], "headers": ["样本索引", "RSR 值"], "rows": rows, "description": f"RSR 综合评价完成，共排序 {len(rsr)} 个样本。", "sections": sections}
