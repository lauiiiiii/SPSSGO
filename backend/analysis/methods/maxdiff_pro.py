# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "maxdiff_pro"
METHOD_META = {'label': 'MaxDiff Pro',
 'category': '高级问卷分析包',
 'description': '强调个体层效用恢复与高级模拟能力的 MaxDiff 扩展方法',
 'order': 230,
 'slots': [{'key': 'variables',
            'label': 'MaxDiff任务变量',
            'type': 'multiple',
            'accept': 'categorical',
            'min': 2,
            'hint': '放入 MaxDiff 任务变量'}],
 'options': [],
 'param_builder': 'direct'}


def run(df, params):
    variables = _resolve_cols(df, params.get("variables", []))
    if len(variables) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "至少需要 2 个 MaxDiff 任务变量。"}

    numeric = df[variables].apply(pd.to_numeric, errors="coerce")
    scores = numeric.fillna(0) if numeric.notna().any().any() else df[variables].apply(lambda s: _selected_mask(s).astype(int))
    mean_scores = scores.mean(axis=0)
    score_std = float(mean_scores.std(ddof=0))
    z_scores = ((mean_scores - mean_scores.mean()) / score_std) if score_std else mean_scores * 0
    rows = [[variable, _fmt(mean_scores[variable], 4), _fmt(z_scores[variable], 4), _fmt(scores[variable].std(ddof=0), 4)] for variable in variables]
    rows.sort(key=lambda row: float(row[2]), reverse=True)

    sections = [
        _sec_table("MaxDiff Pro 偏好恢复", ["项目", "平均得分", "标准化效用", "项目波动"], rows, description="当前实现对任务得分做标准化恢复，用于快速观察偏好强度和区分度。"),
        _sec_table("个体层概况", ["指标", "值"], [["样本量", str(len(scores))], ["平均个体波动", _fmt(scores.std(axis=1, ddof=0).mean(), 4)]]),
        _sec_advice("若原始任务编码越规范，当前标准化效用越有解释力。"),
        _sec_smart(f"MaxDiff Pro 分析完成，当前标准化效用最高的项目为 {rows[0][0]}。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": METHOD_META["label"], "headers": ["项目", "平均得分", "标准化效用", "项目波动"], "rows": rows, "description": f"MaxDiff Pro 分析完成，共比较 {len(variables)} 个项目。", "sections": sections}
