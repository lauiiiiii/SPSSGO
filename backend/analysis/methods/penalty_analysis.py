# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "penalty_analysis"
METHOD_META = {'label': '惩罚分析',
 'category': '高级问卷分析包',
 'description': '识别属性表现偏低时对总体满意度的拖累程度',
 'order': 200,
 'slots': [{'key': 'satisfaction_var',
            'label': '总体满意度',
            'type': 'single',
            'accept': 'numeric',
            'hint': '放入总体满意度变量'},
           {'key': 'attribute_vars',
            'label': '属性表现变量',
            'type': 'multiple',
            'accept': 'numeric',
            'min': 1,
            'hint': '放入属性评分变量'}],
 'options': [],
 'param_builder': 'direct'}


def run(df, params):
    satisfaction_var = params.get("satisfaction_var", "")
    attribute_vars = _resolve_cols(df, params.get("attribute_vars", []))
    if satisfaction_var not in df.columns:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": f"总体满意度变量 {satisfaction_var} 不存在。"}
    if not attribute_vars:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "至少需要 1 个属性表现变量。"}

    temp = df[[satisfaction_var] + attribute_vars].apply(pd.to_numeric, errors="coerce").dropna()
    if len(temp) < 8:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效样本不足。"}

    rows = []
    for variable in attribute_vars:
        threshold = float(temp[variable].median())
        low = temp[variable] <= threshold
        high = temp[variable] > threshold
        low_mean = float(temp.loc[low, satisfaction_var].mean()) if low.any() else np.nan
        high_mean = float(temp.loc[high, satisfaction_var].mean()) if high.any() else np.nan
        rows.append([variable, _fmt(threshold, 2), _fmt(low_mean, 3), _fmt(high_mean, 3), _fmt(high_mean - low_mean, 3), _fmt(temp[variable].corr(temp[satisfaction_var]), 3)])
    rows.sort(key=lambda row: float(row[4]), reverse=True)

    sections = [
        _sec_table("惩罚值结果", ["属性", "低表现阈值", "低表现满意度", "高表现满意度", "惩罚值", "相关系数"], rows, description="惩罚值越高，说明该属性落到低表现区间时对总体满意度的拖累越明显。"),
        _sec_advice("当前实现按属性中位数划分低表现与高表现组。"),
        _sec_smart(f"惩罚分析完成，当前最需要优先改进的属性是 {rows[0][0]}，其惩罚值为 {rows[0][4]}。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": METHOD_META["label"], "headers": ["属性", "低表现阈值", "低表现满意度", "高表现满意度", "惩罚值", "相关系数"], "rows": rows, "description": f"惩罚分析完成，共比较 {len(attribute_vars)} 个属性表现变量。", "sections": sections}
