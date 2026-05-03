# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "conjoint"
METHOD_META = {'label': '联合分析',
 'category': '高级问卷分析包',
 'description': '估计用户对多个属性水平的偏好权重',
 'order': 150,
 'slots': [{'key': 'score_var',
            'label': '偏好评分变量',
            'type': 'single',
            'accept': 'numeric',
            'hint': '放入评分或偏好变量'},
           {'key': 'attribute_vars',
            'label': '属性变量',
            'type': 'multiple',
            'accept': 'categorical',
            'min': 2,
            'hint': '放入属性水平变量'}],
 'options': [],
 'param_builder': 'direct'}


def run(df, params):
    score_var = params.get("score_var", "")
    attribute_vars = _resolve_cols(df, params.get("attribute_vars", []))
    if score_var not in df.columns:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": f"评分变量 {score_var} 不存在。"}
    if len(attribute_vars) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "至少需要 2 个属性变量。"}

    temp = df[[score_var] + attribute_vars].copy()
    temp[score_var] = pd.to_numeric(temp[score_var], errors="coerce")
    temp = temp.dropna(subset=[score_var] + attribute_vars)
    if len(temp) < 8:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效样本不足，联合分析建议至少保留 8 条完整记录。"}

    design = pd.get_dummies(temp[attribute_vars].astype(str), drop_first=True, dtype=float)
    if design.empty:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "属性水平不足，无法建立联合分析模型。"}

    model = sm.OLS(temp[score_var], sm.add_constant(design)).fit()
    utility_rows = []
    importance_rows = []
    for attr in attribute_vars:
        columns = [column for column in design.columns if column.startswith(f"{attr}_")]
        levels = sorted(temp[attr].astype(str).unique().tolist())
        base_level = levels[0] if levels else ""
        effects = {base_level: 0.0}
        for column in columns:
            level = column.split("_", 1)[1]
            effects[level] = float(model.params.get(column, 0.0))
        for level in levels:
            utility_rows.append([attr, level, _fmt(effects.get(level, 0.0), 4)])
        values = list(effects.values()) or [0.0]
        importance_rows.append([attr, _fmt(max(values) - min(values), 4)])

    total_range = sum(float(row[1]) for row in importance_rows) or 1.0
    importance_rows = [[attr, value, f"{_fmt(float(value) / total_range * 100, 1)}%"] for attr, value in importance_rows]
    importance_rows.sort(key=lambda row: float(row[1]), reverse=True)

    sections = [
        _sec_table("属性水平效用值", ["属性", "水平", "相对效用"], utility_rows, description="以每个属性的首个水平为基准，其他水平的系数越高，说明越能提升偏好评分。"),
        _sec_table("属性重要性", ["属性", "效用范围", "重要性占比"], importance_rows),
        _sec_table("模型拟合概况", ["指标", "值"], [["有效样本量", str(int(model.nobs))], ["R²", _fmt(model.rsquared, 4)], ["调整后R²", _fmt(model.rsquared_adj, 4)]]),
        _sec_advice("当前联合分析基于评分型偏好数据，用虚拟变量回归估计属性水平效用；如果后续是选择型任务，更适合使用 CBC 联合分析。"),
        _sec_smart(f"联合分析完成，当前最重要的属性为 {importance_rows[0][0]}，其重要性占比为 {importance_rows[0][2]}。"),
        _sec_refs(_REFS_REGRESSION),
    ]
    return {"name": METHOD_META["label"], "headers": ["属性", "水平", "相对效用"], "rows": utility_rows, "description": f"联合分析完成，共纳入 {int(model.nobs)} 条有效记录。", "sections": sections}
