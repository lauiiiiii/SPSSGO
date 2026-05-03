# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "cbc_conjoint"
METHOD_META = {'label': '联合分析CBC',
 'category': '高级问卷分析包',
 'description': '基于选择任务的联合分析，更贴近真实购买场景',
 'order': 220,
 'slots': [{'key': 'choice_var',
            'label': '选择结果',
            'type': 'single',
            'accept': 'categorical',
            'hint': '放入选择任务结果变量'},
           {'key': 'attribute_vars',
            'label': '属性变量',
            'type': 'multiple',
            'accept': 'categorical',
            'min': 2,
            'hint': '放入 CBC 属性变量'}],
 'options': [],
 'param_builder': 'direct'}


def run(df, params):
    choice_var = params.get("choice_var", "")
    attribute_vars = _resolve_cols(df, params.get("attribute_vars", []))
    if choice_var not in df.columns:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": f"选择变量 {choice_var} 不存在。"}
    if len(attribute_vars) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "至少需要 2 个属性变量。"}

    temp = df[[choice_var] + attribute_vars].copy().dropna()
    if len(temp) < 8:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效样本不足。"}

    y_raw = pd.to_numeric(temp[choice_var], errors="coerce")
    y = (y_raw > 0).astype(int) if y_raw.notna().any() else _selected_mask(temp[choice_var]).astype(int)
    design = pd.get_dummies(temp[attribute_vars].astype(str), drop_first=True, dtype=float)
    if design.empty:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "属性水平不足，无法建立 CBC 模型。"}

    X = sm.add_constant(design)
    try:
        model = sm.Logit(y, X).fit(disp=False)
        label = "logit系数"
        fit_name = "McFadden R²"
        fit_value = _fmt(model.prsquared, 4)
    except Exception:
        model = sm.OLS(y, X).fit()
        label = "线性近似系数"
        fit_name = "R²"
        fit_value = _fmt(model.rsquared, 4)
    rows = [[column, _fmt(model.params.get(column, 0.0), 4), _fmt(model.pvalues.get(column, np.nan), 4)] for column in design.columns]
    rows.sort(key=lambda row: abs(float(row[1])), reverse=True)

    sections = [
        _sec_table("CBC 属性效用", ["属性水平", label, "p"], rows, description="当前实现基于选择结果构建离散选择近似模型，用于快速观察哪些属性水平更容易被选中。"),
        _sec_table("模型概况", ["指标", "值"], [["有效样本量", str(len(temp))], [fit_name, fit_value]]),
        _sec_advice("CBC 更适合处理真实选择任务数据。若后续需要市场份额模拟，可继续在当前独立模块中扩展。"),
        _sec_smart(f"CBC 联合分析完成，当前影响选择概率最大的属性水平为 {rows[0][0]}。"),
        _sec_refs(_REFS_REGRESSION),
    ]
    return {"name": METHOD_META["label"], "headers": ["属性水平", label, "p"], "rows": rows, "description": f"CBC 联合分析完成，共纳入 {len(temp)} 条有效记录。", "sections": sections}
