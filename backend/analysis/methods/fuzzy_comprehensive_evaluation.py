# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "fuzzy_comprehensive_evaluation"
METHOD_META = {'label': '模糊综合评价',
 'category': '综合评价',
 'description': '通过模糊隶属度和加权合成得到综合评价结果',
 'order': 45,
 'slots': [{'key': 'variables', 'label': '评价指标', 'type': 'multiple', 'accept': 'numeric', 'min': 2, 'hint': '放入评价指标'}],
 'options': [],
 'param_builder': 'direct'}


def run(df, params):
    variables = _resolve_cols(df, params.get("variables", []))
    if len(variables) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "模糊综合评价至少需要 2 个指标。"}
    data = df[variables].apply(pd.to_numeric, errors="coerce").dropna()
    if len(data) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效样本不足。"}

    normalized = _normalize_benefit_frame(data)
    grades = pd.DataFrame(index=data.index)
    grades["差"] = np.clip(1 - normalized.mean(axis=1) * 2, 0, 1)
    grades["中"] = 1 - (normalized.mean(axis=1) - 0.5).abs() * 2
    grades["优"] = np.clip(normalized.mean(axis=1) * 2 - 1, 0, 1)
    grades = grades.clip(0, 1)
    score = grades.mul(pd.Series({"差": 1, "中": 3, "优": 5}), axis=1).sum(axis=1) / grades.sum(axis=1).replace(0, np.nan)
    rows = [[str(idx), _fmt(grades.loc[idx, "差"], 4), _fmt(grades.loc[idx, "中"], 4), _fmt(grades.loc[idx, "优"], 4), _fmt(score.loc[idx], 4)] for idx in score.sort_values(ascending=False).head(10).index]
    sections = [
        _sec_table("模糊综合评价 Top10", ["样本索引", "差隶属度", "中隶属度", "优隶属度", "综合得分"], rows),
        _sec_advice("当前版本按等权重和三等级隶属度近似计算综合评价结果。"),
        _sec_smart(f"模糊综合评价完成，当前综合得分最高的样本索引为 {rows[0][0]}。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": METHOD_META["label"], "headers": ["样本索引", "差隶属度", "中隶属度", "优隶属度", "综合得分"], "rows": rows, "description": f"模糊综合评价完成，共评估 {len(score)} 个样本。", "sections": sections}
