# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "two_way_anova"
METHOD_META = {'label': '双因素方差分析',
 'category': '差异对比分析包',
 'description': '检验两个分类因素及其交互作用对因变量的影响',
 'order': 40,
 'slots': [{'key': 'factor1', 'label': '因素1', 'type': 'single', 'accept': 'categorical', 'hint': '放入第一个分组因素'},
           {'key': 'factor2', 'label': '因素2', 'type': 'single', 'accept': 'categorical', 'hint': '放入第二个分组因素'},
           {'key': 'dependent', 'label': '因变量', 'type': 'single', 'accept': 'numeric', 'hint': '放入因变量'}],
 'options': [],
 'param_builder': 'direct'}


def _factorial_anova(df, factors, dependent, name):
    try:
        import statsmodels.formula.api as smf
        from statsmodels.stats.anova import anova_lm
    except Exception as exc:
        return {"name": name, "headers": [], "rows": [], "description": f"缺少方差分析依赖：{str(exc)}"}
    factors = [f for f in factors if f]
    needed = factors + [dependent]
    if any(col not in df.columns for col in needed):
        return {"name": name, "headers": [], "rows": [], "description": "因素变量或因变量不存在。"}
    temp = df[needed].copy()
    temp[dependent] = pd.to_numeric(temp[dependent], errors="coerce")
    temp = temp.dropna()
    for factor in factors:
        temp[factor] = temp[factor].astype("object")
    if len(temp) < max(8, len(factors) * 4):
        return {"name": name, "headers": [], "rows": [], "description": "有效样本不足。"}
    formula = f"Q('{dependent}') ~ " + " * ".join([f"C(Q('{f}'))" for f in factors])
    model = smf.ols(formula, data=temp).fit()
    table = anova_lm(model, typ=2)
    rows = []
    for idx, row in table.iterrows():
        rows.append([str(idx), _fmt(row.get("sum_sq"), 4), _fmt(row.get("df"), 4), _fmt(row.get("F"), 4), _fmt(row.get("PR(>F)"), 4)])
    sections = [
        _sec_table(f"{name}结果", ["来源", "SS", "df", "F", "p"], rows),
        _sec_table("模型摘要", ["指标", "值"], [["R²", _fmt(model.rsquared, 4)], ["调整后R²", _fmt(model.rsquared_adj, 4)], ["样本量", str(int(model.nobs))]]),
        _sec_advice("多因素方差分析要重点关注主效应和交互作用是否显著。交互项显著时，主效应解释需要更谨慎。"),
        _sec_smart(f"{name}完成，共纳入 {int(model.nobs)} 个有效样本。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": name, "headers": ["来源", "SS", "df", "F", "p"], "rows": rows, "description": f"{name}完成。", "sections": sections}


def run(df, params):
    return _factorial_anova(df, [params.get("factor1", ""), params.get("factor2", "")], params.get("dependent", ""), METHOD_META["label"])
