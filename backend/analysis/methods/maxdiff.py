# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "maxdiff"
METHOD_META = {'label': 'MaxDiff模型',
 'category': '高级问卷分析包',
 'description': '基于最好/最差选择结果恢复偏好强度与优先级排序',
 'order': 170,
 'slots': [{'key': 'variables',
            'label': 'MaxDiff任务变量',
            'type': 'multiple',
            'accept': 'categorical',
            'min': 2,
            'hint': '放入 MaxDiff 任务相关变量'}],
 'options': [],
 'param_builder': 'direct'}


def _score_series(series):
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().any():
        best = int((numeric > 0).sum())
        worst = int((numeric < 0).sum())
        base = max(best + worst, 1)
        return best, worst, (best - worst) / base * 100
    selected = _selected_mask(series)
    best = int(selected.sum())
    worst = int((~selected).sum())
    return best, worst, (best - worst) / max(len(series), 1) * 100


def run(df, params):
    variables = _resolve_cols(df, params.get("variables", []))
    if len(variables) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "至少需要 2 个 MaxDiff 任务变量。"}

    rows = []
    for variable in variables:
        best, worst, score = _score_series(df[variable])
        rows.append([variable, str(best), str(worst), _fmt(score, 2)])
    rows.sort(key=lambda row: float(row[3]), reverse=True)

    sections = [
        _sec_table("MaxDiff净偏好得分", ["项目", "最好次数", "最差次数", "净偏好分"], rows, description="当前实现优先读取正负编码数据：正值视为最好、负值视为最差；若不是数值编码，则退化为选中/未选中的净得分近似。"),
        _sec_advice("若原始数据已经是标准 best=1 / worst=-1 / 其余=0 结构，当前结果会更稳定。"),
        _sec_smart(f"MaxDiff 分析完成，当前偏好最高的项目为 {rows[0][0]}，净偏好分为 {rows[0][3]}。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": METHOD_META["label"], "headers": ["项目", "最好次数", "最差次数", "净偏好分"], "rows": rows, "description": f"MaxDiff 分析完成，共比较 {len(variables)} 个项目。", "sections": sections}
