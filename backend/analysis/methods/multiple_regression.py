# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "multiple_regression"
METHOD_META = {'label': '多元线性回归',
 'category': '回归&因果分析包',
 'description': '分析多个自变量对一个因变量的预测作用',
 'slots': [{'key': 'dependent',
            'label': '因变量(Y)',
            'type': 'single',
            'accept': 'numeric',
            'hint': '放入因变量'},
           {'key': 'predictors',
            'label': '自变量(X)',
            'type': 'multiple',
            'accept': 'numeric',
            'min': 1,
            'hint': '放入一个或多个自变量'}],
 'options': [],
 'param_builder': 'regression'}

def multiple_regression(df, params):
    """
    多元线性回归分析，含模型摘要表、VIF 列

    @param df: 数据 DataFrame
    @param params: 包含 predictors, dependent 的参数字典
    @return: 含 sections 的结果字典
    """
    predictors = _resolve_cols(df, params.get("predictors", []))
    dep = params.get("dependent", "")
    if dep not in df.columns or not predictors:
        return {"name": "多元线性回归", "headers": [], "rows": [], "description": "缺少自变量或因变量。"}

    temp = df[predictors + [dep]].apply(pd.to_numeric, errors="coerce").dropna()
    X = temp[predictors]
    y = temp[dep]
    constant_predictors = [v for v in predictors if X[v].nunique(dropna=True) <= 1]
    if constant_predictors:
        return {
            "name": "多元线性回归",
            "headers": [],
            "rows": [],
            "description": f"以下自变量在有效样本中没有变异，无法进行稳定回归估计：{'、'.join(constant_predictors)}。",
        }

    X_c = sm.add_constant(X, has_constant="add")
    model = sm.OLS(y, X_c).fit()

    y_std = (y - y.mean()) / y.std()
    X_std = (X - X.mean()) / X.std()
    X_std_c = sm.add_constant(X_std, has_constant="add")
    model_std = sm.OLS(y_std, X_std_c).fit()

    r_sq = model.rsquared
    adj_r = model.rsquared_adj
    f_stat = model.fvalue
    f_prob = model.f_pvalue
    se_model = np.sqrt(model.mse_resid)

    # VIF
    vif_vals = {}
    if len(predictors) >= 2:
        X_vif = sm.add_constant(X, has_constant="add")
        for v in predictors:
            vif_vals[v] = variance_inflation_factor(X_vif.values, X_vif.columns.get_loc(v))

    sections = []

    # 表 1：模型摘要
    s1_headers = ["R", "R²", "调整R²", "标准误", "F", "p"]
    s1_rows = [[_fmt(np.sqrt(r_sq), 3), _fmt(r_sq, 3), _fmt(adj_r, 3), _fmt(se_model, 3), _fmt(f_stat, 2), _fmt(f_prob)]]
    sections.append(_sec_table("模型摘要", s1_headers, s1_rows,
                               description="R²表示模型解释因变量变异的比例，调整R²考虑了自变量数量的影响。"))

    # 表 2：回归系数（含 VIF）
    headers = ["变量", "B", "SE", "Beta", "t", "p", "Tolerance", "VIF", "95% CI"]
    rows = [["常量", _fmt(model.params["const"]), _fmt(model.bse["const"]), "—",
             _fmt(model.tvalues["const"]), _fmt(model.pvalues["const"]), "—", "—",
             f"[{_fmt(model.conf_int().loc['const', 0], 3)}, {_fmt(model.conf_int().loc['const', 1], 3)}]"]]
    var_descs = []
    for v in predictors:
        beta = model_std.params[v]
        vif_raw = vif_vals.get(v, np.nan) if vif_vals else np.nan
        vif_v = _fmt(vif_raw, 2) if vif_vals else "—"
        tolerance = _fmt(1 / vif_raw, 3) if vif_vals and vif_raw and pd.notna(vif_raw) else "—"
        ci_low, ci_high = model.conf_int().loc[v]
        rows.append([v, _fmt(model.params[v]), _fmt(model.bse[v]), _fmt(beta),
                      _fmt(model.tvalues[v]), _fmt(model.pvalues[v]), tolerance, vif_v,
                      f"[{_fmt(ci_low, 3)}, {_fmt(ci_high, 3)}]"])
        direction = "负向" if model.params[v] < 0 else "正向"
        p = model.pvalues[v]
        if p < 0.05:
            var_descs.append(f"{v}能够显著{direction}预测{dep}（B={_fmt(model.params[v], 3)}，β={_fmt(beta, 3)}，{_p_expr(p)}）")
        else:
            var_descs.append(f"{v}对{dep}的预测作用未达到显著水平（B={_fmt(model.params[v], 3)}，β={_fmt(beta, 3)}，{_p_expr(p)}）")

    note = f"注：R²={_fmt(r_sq)}，调整R²={_fmt(adj_r)}，F={_fmt(f_stat)}，p={_fmt(f_prob)}。"
    sections.append(_sec_table("回归系数", headers, rows, note=note,
                               description="B为非标准化系数，Beta为标准化系数，VIF>10提示严重多重共线性。"))

    # 分析建议
    advice = (
        "多元线性回归用于分析多个自变量对一个因变量的预测作用；\n"
        "第一：R²越接近1，模型拟合越好；调整R²考虑了变量数量，更为客观；\n"
        "第二：F检验p<0.05说明回归方程整体有效；\n"
        "第三：各自变量的p值判断其是否显著，Beta值可比较各变量的相对重要性；\n"
        "第四：VIF>10表示存在严重多重共线性，需要处理。"
    )
    sections.append(_sec_advice(advice))

    # 智能分析
    smart = (
        f"以{dep}为因变量，以{'、'.join(predictors)}为自变量，采用强制进入法进行多元线性回归分析。"
        f"回归方程整体检验结果{'显著' if f_prob < 0.05 else '不显著'}"
        f"（F={_fmt(f_stat, 2)}，{_p_expr(f_prob)}），"
        f"模型可解释{dep}总变异的{_fmt(adj_r * 100, 1)}%（调整R²={_fmt(adj_r, 3)}）。"
        f"具体而言，{'；'.join(var_descs)}。"
    )
    # 共线性提示
    high_vif = [v for v in predictors if vif_vals.get(v, 0) > 10]
    if high_vif:
        smart += f"\n注意：{'、'.join(high_vif)}的VIF>10，存在严重多重共线性，建议处理。"
    sections.append(_sec_smart(smart))
    sections.append(_sec_refs(_REFS_REGRESSION))

    desc = smart + " " + note
    return {"name": "多元线性回归分析", "headers": headers, "rows": rows, "description": desc, "sections": sections}

run = multiple_regression
