# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "ancova"
METHOD_META = {'label': '协方差分析',
 'category': '差异对比分析包',
 'description': '在控制协变量影响后比较组间均值差异',
 'order': 60,
 'slots': [{'key': 'group_var', 'label': '分组变量', 'type': 'single', 'accept': 'categorical', 'hint': '放入分组变量'},
           {'key': 'covariates', 'label': '协变量', 'type': 'multiple', 'accept': 'numeric', 'min': 1, 'hint': '放入协变量'},
           {'key': 'dependent', 'label': '因变量', 'type': 'single', 'accept': 'numeric', 'hint': '放入因变量'}],
 'options': [],
 'param_builder': 'direct'}


def run(df, params):
    try:
        import statsmodels.formula.api as smf
        from statsmodels.stats.anova import anova_lm
    except Exception as exc:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": f"缺少 ANCOVA 依赖：{str(exc)}"}
    group_var = params.get("group_var", "")
    covariates = _resolve_cols(df, params.get("covariates", []))
    dependent = params.get("dependent", "")
    needed = [group_var, dependent] + covariates
    if any(col not in df.columns for col in needed):
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "分组变量、协变量或因变量不存在。"}
    temp = df[needed].copy()
    temp[dependent] = pd.to_numeric(temp[dependent], errors="coerce")
    for cov in covariates:
        temp[cov] = pd.to_numeric(temp[cov], errors="coerce")
    temp = temp.dropna()
    temp[group_var] = temp[group_var].astype("object")
    formula = f"Q('{dependent}') ~ C(Q('{group_var}'))"
    for cov in covariates:
        formula += f" + Q('{cov}')"
    model = smf.ols(formula, data=temp).fit()
    table = anova_lm(model, typ=2)
    rows = [[str(idx), _fmt(row.get("sum_sq"), 4), _fmt(row.get("df"), 4), _fmt(row.get("F"), 4), _fmt(row.get("PR(>F)"), 4)] for idx, row in table.iterrows()]
    sections = [
        _sec_table("ANCOVA 结果", ["来源", "SS", "df", "F", "p"], rows),
        _sec_table("模型摘要", ["指标", "值"], [["R²", _fmt(model.rsquared, 4)], ["调整后R²", _fmt(model.rsquared_adj, 4)], ["样本量", str(int(model.nobs))]]),
        _sec_advice("协方差分析适合在控制协变量影响后比较组间差异。若协变量与组别交互明显，应谨慎解释。"),
        _sec_smart(f"协方差分析完成，共纳入 {int(model.nobs)} 个有效样本。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": METHOD_META["label"], "headers": ["来源", "SS", "df", "F", "p"], "rows": rows, "description": "协方差分析完成。", "sections": sections}
