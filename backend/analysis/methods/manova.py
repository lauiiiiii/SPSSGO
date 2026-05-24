# -*- coding: utf-8 -*-
# 多变量方差分析：输出多变量检验和各因变量主体间效应检验。
# 多个分组变量只建主效应模型；协变量走 MANCOVA 口径，不在这里做全交互。
from backend.analysis.common import *

METHOD_KEY = "manova"
METHOD_META = {
    "label": "多变量方差分析",
    "category": "差异对比分析包",
    "description": "同时检验多个因变量在组间的总体差异",
    "order": 65,
    "slots": [
        {"key": "dependent_vars", "label": "因变量", "type": "multiple", "accept": "numeric", "min": 2, "hint": "放入两个及以上因变量"},
        {"key": "group_var", "label": "分组变量", "type": "multiple", "accept": "categorical", "min": 1, "hint": "放入1个或多个分组变量"},
        {"key": "covariates", "label": "协变量", "type": "multiple", "accept": "numeric", "min": 0, "hint": "可选，放入协变量"},
    ],
    "options": [],
    "param_builder": "direct",
}


def _as_list(value):
    if isinstance(value, list):
        return [item for item in value if item]
    return [value] if value else []


def _fmt_p(p):
    if pd.isna(p):
        return "—"
    number = float(p)
    if number < 0.001:
        sig = "***"
    elif number < 0.01:
        sig = "**"
    elif number < 0.1:
        sig = "*"
    else:
        sig = ""
    return f"{_fmt(number, 3)}{sig}"


def _term_label(term, group_vars, covariates):
    text = str(term)
    if text == "Intercept":
        return "截距"
    if text == "Residual":
        return "误差"
    group_terms = {f"C(Q('{group_var}'))": group_var for group_var in group_vars}
    if text in group_terms:
        return group_terms[text]
    for cov in covariates:
        if text == f"Q('{cov}')":
            return cov
    if text.startswith("Q('") and text.endswith("')"):
        return text[3:-2]
    return text


def _test_name(name):
    mapping = {
        "Wilks' lambda": "威尔克Lambda",
        "Pillai's trace": "比莱轨迹",
        "Hotelling-Lawley trace": "霍特林轨迹",
        "Roy's greatest root": "罗伊最大根",
    }
    return mapping.get(str(name), str(name))


def _multivariate_rows(mv, group_vars, covariates):
    rows = []
    for effect_key, result in mv.results.items():
        label = _term_label(effect_key, group_vars, covariates)
        stat_table = result.get("stat")
        if stat_table is None:
            continue
        for stat_name, row in stat_table.iterrows():
            rows.append([
                label,
                _test_name(stat_name),
                _fmt(row.get("Value"), 3),
                _fmt(row.get("F Value"), 3),
                _fmt_p(row.get("Pr > F")),
            ])
    return rows


def _subject_effect_rows(temp, dependent_vars, group_vars, covariates, terms):
    import statsmodels.formula.api as smf
    from statsmodels.stats.anova import anova_lm

    rows = []
    for dependent in dependent_vars:
        formula = f"Q('{dependent}') ~ " + " + ".join(terms)
        model = smf.ols(formula, data=temp).fit()
        table = anova_lm(model, typ=3)
        for idx, row in table.iterrows():
            label = _term_label(idx, group_vars, covariates)
            ss = row.get("sum_sq")
            df_val = row.get("df")
            ms = ss / df_val if pd.notna(ss) and pd.notna(df_val) and df_val else np.nan
            rows.append([
                label,
                dependent,
                _fmt(ss, 3),
                _fmt(df_val, 0),
                _fmt(ms, 3),
                _fmt(row.get("F"), 3),
                _fmt_p(row.get("PR(>F)")),
            ])
    return rows


def _smart_text(multivariate_rows, group_vars, dependent_vars, covariates):
    parts = [
        f"多变量方差分析用于判断{'、'.join(group_vars)}是否对多个因变量整体产生影响，"
        f"本次因变量为：{'、'.join(dependent_vars)}。"
    ]
    if covariates:
        parts.append(f"模型同时控制协变量：{'、'.join(covariates)}。")
    for group_var in group_vars:
        wilks = next((row for row in multivariate_rows if row[0] == group_var and row[1] == "威尔克Lambda"), None)
        if not wilks:
            continue
        p_num = _safe_float(str(wilks[4]).replace("*", ""), np.nan)
        if pd.notna(p_num) and p_num < 0.05:
            parts.append(f"基于分组变量{group_var}，Wilks' Lambda 的P值为{wilks[4]}，整体因变量差异呈现显著性。")
        else:
            parts.append(f"基于分组变量{group_var}，Wilks' Lambda 的P值为{wilks[4]}，整体因变量差异不呈现显著性。")
    return "\n".join(parts)


def run(df, params):
    try:
        from statsmodels.multivariate.manova import MANOVA
    except Exception as exc:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": f"缺少 MANOVA 依赖：{str(exc)}"}

    dependent_vars = _resolve_cols(df, _as_list(params.get("dependent_vars", [])))
    raw_group_vars = params.get("group_var", params.get("group_vars", params.get("factors", [])))
    group_vars = _resolve_cols(df, _as_list(raw_group_vars))
    covariates = _resolve_cols(df, _as_list(params.get("covariates", [])))

    if len(dependent_vars) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "因变量至少需要 2 个。"}
    if not group_vars:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "分组变量至少需要 1 个。"}

    needed = dependent_vars + group_vars + covariates
    if any(not col or col not in df.columns for col in needed):
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "分组变量、因变量或协变量不存在。"}

    temp = df[needed].copy()
    for dep in dependent_vars:
        temp[dep] = pd.to_numeric(temp[dep], errors="coerce")
    for cov in covariates:
        temp[cov] = pd.to_numeric(temp[cov], errors="coerce")
    temp = temp.dropna()
    for group_var in group_vars:
        temp[group_var] = temp[group_var].astype("object")
    if len(temp) < max(8, len(dependent_vars) * 3):
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效样本不足。"}
    invalid_groups = [group_var for group_var in group_vars if temp[group_var].nunique() < 2]
    if invalid_groups:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": f"分组变量至少需要 2 个有效组：{', '.join(invalid_groups)}。"}

    lhs = " + ".join([f"Q('{dep}')" for dep in dependent_vars])
    group_terms = [f"C(Q('{group_var}'))" for group_var in group_vars]
    cov_terms = [f"Q('{cov}')" for cov in covariates]
    terms = [*group_terms, *cov_terms]
    formula = f"{lhs} ~ " + " + ".join(terms)
    try:
        model = MANOVA.from_formula(formula, data=temp)
        mv = model.mv_test()
    except Exception as exc:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": f"MANOVA 执行失败：{str(exc)}"}

    multivariate_headers = ["项", "检验方法", "统计值", "F", "P"]
    multivariate_rows = _multivariate_rows(mv, group_vars, covariates)
    subject_headers = ["项", "因变量", "平方和", "自由度", "均方", "F", "P"]
    subject_rows = _subject_effect_rows(temp, dependent_vars, group_vars, covariates, terms)

    sections = [
        _sec_advice(
            "1. 通过多变量检验判断分组因素是否会对多个因变量整体产生影响；\n"
            "2. 若整体检验显著，再通过主体间效应检验查看具体是哪一个因变量存在显著差异；\n"
            "3. 若加入协变量，则主体间效应是在控制协变量后的结果。",
            title="分析步骤",
        ),
        _sec_table(
            "输出结果1：多变量检验",
            multivariate_headers,
            multivariate_rows,
            description=(
                "上表展示多变量检验结果，用于研究不同分组在多个因变量整体上是否存在显著差异。\n"
                "Wilks' Lambda、Pillai's Trace、Hotelling-Lawley Trace、Roy's Largest Root 均可作为整体差异判断依据。"
            ),
        ),
        _sec_smart(_smart_text(multivariate_rows, group_vars, dependent_vars, covariates)),
        _sec_table(
            "输出结果2：主体间效应检验",
            subject_headers,
            subject_rows,
            note="* p<0.1 ** p<0.01 *** p<0.001",
            description="上表展示主体间效应检验结果，可查看具体是哪一个因变量存在显著的组间差异。",
        ),
        _sec_refs(_REFS_GENERAL),
    ]
    return {
        "name": METHOD_META["label"],
        "headers": multivariate_headers,
        "rows": multivariate_rows,
        "description": "多变量方差分析完成。",
        "sections": sections,
    }
