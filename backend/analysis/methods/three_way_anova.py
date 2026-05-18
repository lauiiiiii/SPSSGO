# -*- coding: utf-8 -*-
# 三因素方差分析主流程：对齐 SPSSAU/SPSSPRO 的输入、交互项、均值图表和可选事后比较。
# 这里只处理三因素固定模型；多因素通用入口仍走 n_way_anova，别把两边逻辑混在一起。
from itertools import combinations
import re

from backend.analysis.common import *
from backend.analysis.methods.two_way_anova import (
    _as_list,
    _fmt_p,
    _formula_term,
    _mean_chart,
    _mean_cross_table,
    _post_hoc_section,
    _sample_summary,
)

METHOD_KEY = "three_way_anova"
METHOD_META = {'label': '三因素方差分析',
 'category': '差异对比分析包',
 'description': '检验三个分类因素及其交互作用对因变量的影响',
 'order': 45,
 'slots': [{'key': 'factors', 'label': '分组变量X', 'type': 'multiple', 'accept': 'categorical', 'min': 3, 'max': 3, 'hint': '放入3个分组因素'},
           {'key': 'dependent', 'label': '因变量Y', 'type': 'single', 'accept': 'numeric', 'hint': '放入因变量'},
           {'key': 'covariates', 'label': '协变量', 'type': 'multiple', 'accept': 'numeric', 'min': 0, 'hint': '可选，放入需要控制的协变量'}],
 'options': [{'key': 'include_interaction', 'label': '分析交互效应', 'type': 'checkbox', 'default': True},
             {'key': 'second_order_interaction', 'label': '二阶交互效应', 'type': 'checkbox', 'default': True},
             {'key': 'third_order_interaction', 'label': '三阶交互效应', 'type': 'checkbox', 'default': False},
             {'key': 'include_effect_size', 'label': '效应量', 'type': 'checkbox', 'default': False},
             {'key': 'do_post_hoc', 'label': '事后多重比较', 'type': 'checkbox', 'default': False},
             {'key': 'post_hoc_method', 'label': '方法选择', 'choices': ['LSD', 'Tukey法', 'Bonferroni校正', 'Sidak法'], 'default': 'LSD'}],
 'param_builder': 'direct'}


def _truthy(value, default=False):
    if value is None:
        return default
    return value in (True, "true", "1", 1, "是", "yes", "on")


def _resolve_factors(df, params):
    raw_factors = _as_list(params.get("factors", []))
    factors = _resolve_cols(df, raw_factors)
    if raw_factors:
        return factors
    return [params.get("factor1", ""), params.get("factor2", ""), params.get("factor3", "")]


def _normalize_post_hoc_method(method):
    text = str(method or "LSD")
    if "bonf" in text.lower() or "校正" in text:
        return "bonf"
    if "sidak" in text.lower():
        return "sidak"
    if "tukey" in text.lower():
        return "tukey"
    return "LSD"


def _term_label(term, factors):
    text = str(term)
    if text == "Residual":
        return "误差"
    for factor in factors:
        text = text.replace(f"C(Q('{factor}'))", factor)
    for cov in re.findall(r"Q\('([^']+)'\)", text):
        text = text.replace(f"Q('{cov}')", cov)
    return text.replace(":", " * ")


def _anova_rows(table, model, factors, include_effect_size=False):
    headers = ["差异源", "平方和", "df", "均方", "F", "p"]
    if include_effect_size:
        headers.extend(["η²", "partial η²"])
    rows = []
    ss_total = float(table["sum_sq"].sum()) if "sum_sq" in table else np.nan
    ss_error = float(table.loc["Residual", "sum_sq"]) if "Residual" in table.index else np.nan
    for idx, row in table.iterrows():
        ss = row.get("sum_sq")
        df_val = row.get("df")
        ms = ss / df_val if pd.notna(ss) and pd.notna(df_val) and df_val else np.nan
        out = [
            _term_label(idx, factors),
            _fmt(ss, 3),
            _fmt(df_val, 0),
            _fmt(ms, 3),
            _fmt(row.get("F"), 3),
            _fmt_p(row.get("PR(>F)")),
        ]
        if include_effect_size:
            if str(idx) == "Residual":
                out.extend(["", ""])
            else:
                eta_sq = float(ss) / ss_total if pd.notna(ss) and ss_total > 0 else np.nan
                partial_eta_sq = float(ss) / (float(ss) + ss_error) if pd.notna(ss) and pd.notna(ss_error) and (float(ss) + ss_error) > 0 else np.nan
                out.extend([_fmt(eta_sq, 3), _fmt(partial_eta_sq, 3)])
        rows.append(out)
    return headers, rows


def _analysis_advice(second_order, third_order, covariates):
    lines = [
        "三因素方差分析用于研究3个定类数据对于1个定量数据Y的差异关系，通常用于实验研究中。如果有可能干扰模型项，则放入协变量中。",
        "第一：分别分析3个X是否呈现出显著性；如果呈现出显著性，说明不同组别会对Y产生显著性差异，具体可以通过方差分析（单因素方差）进一步研究；",
    ]
    if second_order:
        lines.append("第二：如果二阶效应显著，则可继续通过表格和图形研究二阶效应情况；")
    else:
        lines.append("第二：本次未纳入二阶效应，结果主要解释3个因素的主效应；")
    if third_order:
        lines.append("第三：如果三阶效应显著，则可继续通过表格和图形研究三阶效应情况；")
    else:
        lines.append("第三：本次未纳入三阶效应，暂不解释三个因素共同作用；")
    if covariates:
        lines.append("第四：协变量为干扰项，通常不需要进行分析。")
    return "\n".join(lines)


def _three_way_mean_table(factors, dependent, temp):
    levels = [sorted(temp[factor].dropna().unique()) for factor in factors]
    rows = []
    for level1 in levels[0]:
        for level2 in levels[1]:
            for level3 in levels[2]:
                series = temp.loc[
                    (temp[factors[0]] == level1)
                    & (temp[factors[1]] == level2)
                    & (temp[factors[2]] == level3),
                    dependent,
                ]
                if len(series):
                    rows.append([str(level1), str(level2), str(level3), _fmt(series.mean(), 3), _fmt(series.std(), 3), str(len(series))])
                else:
                    rows.append([str(level1), str(level2), str(level3), "null", "null", "0"])
    return _sec_table(
        "三因素均值对比",
        [*factors, "均值", "标准差", "n"],
        rows,
        description="上表展示三个分组因素交叉后各单元格的均值、标准差和样本量，用于定位三因素组合下的差异方向。",
    )


def _smart_text(rows, factors, dependent, covariates, include_interaction, second_order, third_order):
    parts = [f"从上表可知，以{'、'.join(factors)}为分组因素、{dependent}为因变量进行三因素方差分析。"]
    if covariates:
        parts.append(f"模型同时控制了协变量：{'、'.join(covariates)}。")
    for row in rows:
        name, _, _, _, f_value, p_value, *_ = row
        if name == "误差":
            continue
        p_num = _safe_float(str(p_value).replace("*", ""), np.nan)
        if pd.notna(p_num) and p_num < 0.05:
            parts.append(f"{name}呈现显著性（F={f_value}，p={p_value}），说明其对{dependent}存在显著影响。")
        else:
            parts.append(f"{name}未呈现显著性（F={f_value}，p={p_value}），说明其对{dependent}的影响不显著。")
    if include_interaction and third_order:
        parts.append("已纳入三阶交互项，若三阶交互显著，应优先结合三因素组合均值表解释差异。")
    elif include_interaction and second_order:
        parts.append("已纳入二阶交互项，可结合两两均值图和均值表解释交互方向。")
    else:
        parts.append("本次未纳入交互项，结果主要解释三个因素的主效应。")
    return "\n".join(parts)


def run(df, params):
    try:
        import statsmodels.formula.api as smf
        from statsmodels.stats.anova import anova_lm
    except Exception as exc:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": f"缺少方差分析依赖：{str(exc)}"}

    factors = _resolve_factors(df, params)
    if len([factor for factor in factors if factor in df.columns]) != 3:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "分组变量X需要放入3个定类变量。"}
    dependent = params.get("dependent", "")
    covariates = _resolve_cols(df, _as_list(params.get("covariates", [])))
    include_interaction = _truthy(params.get("include_interaction"), True)
    second_order = include_interaction and _truthy(params.get("second_order_interaction"), True)
    third_order = include_interaction and _truthy(params.get("third_order_interaction"), False)
    include_effect_size = _truthy(params.get("include_effect_size"), False)
    do_post_hoc = _truthy(params.get("do_post_hoc"), False)
    post_hoc_method = _normalize_post_hoc_method(params.get("post_hoc_method", "LSD"))

    needed = factors + [dependent] + covariates
    if any(not col or col not in df.columns for col in needed):
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "因素变量、因变量或协变量不存在。"}

    temp = df[needed].copy()
    total_n = len(temp)
    temp[dependent] = pd.to_numeric(temp[dependent], errors="coerce")
    for cov in covariates:
        temp[cov] = pd.to_numeric(temp[cov], errors="coerce")
    temp = temp.dropna()
    for factor in factors:
        temp[factor] = temp[factor].astype("object")
    if len(temp) < 12:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效样本不足。"}

    factor_terms = [_formula_term(factor) for factor in factors]
    terms = list(factor_terms)
    if second_order or third_order:
        terms.extend([":".join(pair) for pair in combinations(factor_terms, 2)])
    if third_order:
        terms.append(":".join(factor_terms))
    terms.extend([f"Q('{cov}')" for cov in covariates])
    formula = f"Q('{dependent}') ~ " + " + ".join(terms)
    model = smf.ols(formula, data=temp).fit()
    table = anova_lm(model, typ=2)
    headers, rows = _anova_rows(table, model, factors, include_effect_size)

    sections = [
        _sec_table(
            "输出结果1：三因素方差分析结果",
            headers,
            rows,
            note=f"备注：R² = {_fmt(model.rsquared, 3)}\n* p<0.1 ** p<0.05 *** p<0.01 **** p<0.001",
            description="上表展示三因素方差分析结果，主效应或交互效应显著时，可继续结合均值图、均值表和事后比较结果解释差异来源。",
        ),
        _sec_advice(_analysis_advice(second_order, third_order, covariates), title="分析建议"),
        _sec_smart(_smart_text(rows, factors, dependent, covariates, include_interaction, second_order, third_order)),
    ]

    if second_order or third_order:
        charts = [_mean_chart(pair[0], pair[1], dependent, temp) for pair in combinations(factors, 2)]
        sections.append(_sec_charts(
            "输出结果2：均值对比图",
            charts,
            "上图展示三因素方差分析中的两两均值对比，可用于观察二阶交互方向。",
        ))
        for pair in combinations(factors, 2):
            sections.append(_mean_cross_table(pair[0], pair[1], dependent, temp))
    else:
        sections.append(_three_way_mean_table(factors, dependent, temp))

    if third_order:
        sections.append(_three_way_mean_table(factors, dependent, temp))

    sections.append(_sample_summary(total_n, int(model.nobs)))

    if do_post_hoc:
        df_resid = float(table.loc["Residual", "df"]) if "Residual" in table.index else np.nan
        sections.append(_post_hoc_section(temp, factors[0], model, df_resid, post_hoc_method, "输出结果3：事后多重比较结果"))
        for factor in factors[1:]:
            sections.append(_post_hoc_section(temp, factor, model, df_resid, post_hoc_method))

    sections.append(_sec_refs(_REFS_GENERAL))
    return {
        "name": METHOD_META["label"],
        "headers": headers,
        "rows": rows,
        "description": "三因素方差分析完成。",
        "sections": sections,
    }
