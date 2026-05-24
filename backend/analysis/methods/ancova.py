# -*- coding: utf-8 -*-
# 协方差分析：用 OLS/Type III ANCOVA 输出主体间效应、调整均值和可选事后比较。
# 多个分组变量只建主效应模型；全交互多因素协方差不要塞进这个入口。
import math

from backend.analysis.common import *

METHOD_KEY = "ancova"
METHOD_META = {
    "label": "协方差分析",
    "category": "差异对比分析包",
    "description": "在控制协变量影响后比较组间均值差异",
    "order": 60,
    "slots": [
        {"key": "dependent", "label": "因变量", "type": "single", "accept": "numeric", "hint": "放入因变量"},
        {"key": "group_var", "label": "分组变量", "type": "multiple", "accept": "categorical", "min": 1, "hint": "放入1个或多个分组变量"},
        {"key": "covariates", "label": "协变量", "type": "multiple", "accept": "numeric", "min": 1, "hint": "放入协变量"},
    ],
    "options": [
        {
            "key": "include_interaction",
            "label": "平行性检验",
            "type": "checkbox",
            "default": False,
            "hint": "模型中建立分组变量与协变量之间的交互项，用于检查回归斜率齐性。",
        },
        {
            "key": "include_effect_size",
            "label": "效应量",
            "type": "checkbox",
            "default": False,
            "hint": "选中后主体间效应表会输出偏η²。",
        },
        {
            "key": "do_post_hoc",
            "label": "事后多重比较",
            "type": "checkbox",
            "default": False,
        },
        {
            "key": "post_hoc_method",
            "label": "方法选择",
            "choices": ["LSD", "Bonferroni校正", "Sidak法", "Tukey法"],
            "default": "LSD",
            "hint": "默认不进行事后多重比较，可选 LSD 等方法。",
        },
    ],
    "param_builder": "direct",
}


def _as_list(value):
    if isinstance(value, list):
        return [item for item in value if item]
    return [value] if value else []


def _truthy(value, default=False):
    if value is None:
        return default
    return value in (True, "true", "1", 1, "是", "yes", "on")


def _fmt_p(p):
    if pd.isna(p):
        return "—"
    number = float(p)
    if number < 0.001:
        sig = "****"
    elif number < 0.01:
        sig = "***"
    elif number < 0.05:
        sig = "**"
    elif number < 0.1:
        sig = "*"
    else:
        sig = ""
    return f"{_fmt(number, 3)}{sig}"


def _normalize_post_hoc_method(method):
    text = str(method or "LSD").lower()
    if "bonf" in text or "校正" in text:
        return "bonferroni"
    if "sidak" in text:
        return "sidak"
    if "tukey" in text:
        return "tukey"
    return "lsd"


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
        cov_term = f"Q('{cov}')"
        if text == cov_term:
            return cov
        for group_term, group_var in group_terms.items():
            if text == f"{group_term}:Q('{cov}')" or text == f"Q('{cov}'):{group_term}":
                return f"{group_var}*{cov}"
    if text.startswith("Q('") and text.endswith("')"):
        return text[3:-2]
    return text


def _model_design_matrix(model, frame):
    from patsy import build_design_matrices

    design_info = model.model.data.design_info
    return np.asarray(build_design_matrices([design_info], frame, return_type="dataframe")[0], dtype=float)


def _adjusted_design(temp, group_vars, target_group, level, covariates):
    frame = temp.copy()
    frame[target_group] = level
    for group_var in group_vars:
        frame[group_var] = frame[group_var].astype("object")
    for cov in covariates:
        frame[cov] = temp[cov].mean()
    return frame


def _adjusted_means_section(temp, model, group_vars, group_var, dependent, covariates, ci=0.95):
    levels = sorted(temp[group_var].dropna().unique())
    cov = np.asarray(model.cov_params(), dtype=float)
    params = np.asarray(model.params, dtype=float)
    df_resid = float(model.df_resid)
    crit = stats.t.ppf(1 - (1 - ci) / 2, df_resid) if df_resid > 0 else np.nan
    rows = []
    chart_labels = []
    chart_values = []
    design_by_level = {}
    for level in levels:
        design = _model_design_matrix(model, _adjusted_design(temp, group_vars, group_var, level, covariates)).mean(axis=0)
        design_by_level[level] = design
        mean = float(design @ params)
        se = math.sqrt(float(design @ cov @ design.T)) if df_resid > 0 else np.nan
        ci_low = mean - crit * se if np.isfinite(crit) and np.isfinite(se) else np.nan
        ci_high = mean + crit * se if np.isfinite(crit) and np.isfinite(se) else np.nan
        rows.append([str(level), _fmt(mean, 3), _fmt(se, 3), _fmt(ci_low, 3), _fmt(ci_high, 3)])
        chart_labels.append(str(level))
        chart_values.append(mean)
    section = _sec_table(
        f"输出结果2：协方差分析调整均值（{group_var}）",
        [group_var, "平均值", "标准误差", f"{int(ci * 100)}%置信区间下限", f"{int(ci * 100)}%置信区间上限"],
        rows,
        description="上表展示控制协变量后的分组变量调整均值，可用于比较各组在因变量上的净差异。",
    )
    chart = _sec_charts(
        f"{group_var}调整均值对比图",
        [{
            "chartType": "metric_comparison",
            "title": f"{group_var}调整均值对比",
            "data": {
                "metric": dependent,
                "labels": chart_labels,
                "values": chart_values,
                "defaultMode": "line",
                "displayTitle": f"{group_var}调整均值对比",
            },
        }],
        "上图展示控制协变量后各组调整均值的差异方向。",
    )
    return section, chart, design_by_level


def _post_hoc_section(model, design_by_level, method, group_var, output_index):
    levels = list(design_by_level.keys())
    pair_count = max(len(list(combinations(levels, 2))), 1)
    cov = np.asarray(model.cov_params(), dtype=float)
    params = np.asarray(model.params, dtype=float)
    df_resid = float(model.df_resid)
    normalized = _normalize_post_hoc_method(method)
    rows = []
    for level_i, level_j in combinations(levels, 2):
        for i, j in [(level_i, level_j), (level_j, level_i)]:
            contrast = design_by_level[i] - design_by_level[j]
            diff = float(contrast @ params)
            se = math.sqrt(float(contrast @ cov @ contrast.T)) if df_resid > 0 else np.nan
            t_value = diff / se if np.isfinite(se) and se > 0 else np.nan
            p_raw = 2 * stats.t.sf(abs(t_value), df_resid) if df_resid > 0 and np.isfinite(t_value) else np.nan
            if normalized == "bonferroni":
                p_value = min(float(p_raw) * pair_count, 1.0)
            elif normalized == "sidak":
                p_value = 1 - (1 - float(p_raw)) ** pair_count
            elif normalized == "tukey":
                q_value = abs(t_value) * math.sqrt(2) if np.isfinite(t_value) else np.nan
                try:
                    p_value = float(stats.studentized_range.sf(q_value, len(levels), df_resid))
                except Exception:
                    p_value = float(p_raw)
            else:
                p_value = float(p_raw)
            ci_low = diff - stats.t.ppf(0.975, df_resid) * se if df_resid > 0 and np.isfinite(se) else np.nan
            ci_high = diff + stats.t.ppf(0.975, df_resid) * se if df_resid > 0 and np.isfinite(se) else np.nan
            rows.append([str(i), str(j), _fmt(diff, 3), _fmt(se, 3), _fmt_p(p_value), _fmt(ci_low, 3), _fmt(ci_high, 3)])
    return _sec_table(
        f"输出结果{output_index}：{group_var}事后多重比较结果",
        [f"{group_var}(I)", f"{group_var}(J)", "平均值差值(I-J)", "标准误差", "P", "95%置信区间下限", "95%置信区间上限"],
        rows,
        description=f"上表使用{method}方法基于调整均值进行事后多重比较，用于定位{group_var}各组别之间的差异。",
    )


def _smart_text(rows, group_vars, dependent, covariates, include_interaction):
    parts = [
        f"从上表可知，以{'、'.join(group_vars)}为分组变量、{dependent}为因变量进行协方差分析，"
        f"模型控制了协变量：{'、'.join(covariates)}。"
    ]
    for row in rows:
        name, _, _, _, f_value, p_value, *_ = row
        if name in ("截距", "误差"):
            continue
        p_num = _safe_float(str(p_value).replace("*", ""), np.nan)
        if pd.notna(p_num) and p_num < 0.05:
            parts.append(f"{name}呈现显著性（F={f_value}，P={p_value}），说明其对{dependent}存在显著影响。")
        else:
            parts.append(f"{name}未呈现显著性（F={f_value}，P={p_value}），说明其对{dependent}的影响不显著。")
    if include_interaction:
        parts.append("本次纳入了各分组变量与协变量交互项，可用于判断回归斜率齐性；若交互项显著，主效应解释要谨慎。")
    else:
        parts.append("本次未纳入分组变量与协变量交互项，默认回归斜率齐性假设成立。")
    return "\n".join(parts)


def run(df, params):
    try:
        import statsmodels.formula.api as smf
        from statsmodels.stats.anova import anova_lm
    except Exception as exc:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": f"缺少 ANCOVA 依赖：{str(exc)}"}

    raw_group_vars = params.get("group_var", params.get("group_vars", params.get("factors", [])))
    group_vars = _resolve_cols(df, _as_list(raw_group_vars))
    covariates = _resolve_cols(df, _as_list(params.get("covariates", [])))
    dependent = params.get("dependent", "")
    include_interaction = _truthy(params.get("include_interaction"), False)
    include_effect_size = _truthy(params.get("include_effect_size"), False)
    do_post_hoc = _truthy(params.get("do_post_hoc"), False)
    post_hoc_method = str(params.get("post_hoc_method", "LSD") or "LSD")

    needed = group_vars + [dependent] + covariates
    if any(not col or col not in df.columns for col in needed):
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "分组变量、协变量或因变量不存在。"}
    if not group_vars:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "协方差分析至少需要 1 个分组变量。"}
    if not covariates:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "协方差分析至少需要 1 个协变量。"}

    temp = df[needed].copy()
    temp[dependent] = pd.to_numeric(temp[dependent], errors="coerce")
    for cov in covariates:
        temp[cov] = pd.to_numeric(temp[cov], errors="coerce")
    temp = temp.dropna()
    for group_var in group_vars:
        temp[group_var] = temp[group_var].astype("object")
    if len(temp) < max(8, len(covariates) + 4):
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效样本不足。"}
    invalid_groups = [group_var for group_var in group_vars if temp[group_var].nunique() < 2]
    if invalid_groups:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": f"分组变量至少需要 2 个有效组：{', '.join(invalid_groups)}。"}

    group_terms = [f"C(Q('{group_var}'))" for group_var in group_vars]
    cov_terms = [f"Q('{cov}')" for cov in covariates]
    terms = [*group_terms, *cov_terms]
    if include_interaction:
        terms.extend([f"{group_term}:Q('{cov}')" for group_term in group_terms for cov in covariates])
    formula = f"Q('{dependent}') ~ " + " + ".join(terms)
    model = smf.ols(formula, data=temp).fit()
    table = anova_lm(model, typ=3)
    residual_ss = float(table.loc["Residual", "sum_sq"]) if "Residual" in table.index else np.nan

    headers = ["项", "平方和", "自由度", "均方", "F", "P", "R²", "调整R²"]
    if include_effect_size:
        headers.append("偏η²")
    rows = []
    for idx, row in table.iterrows():
        ss = row.get("sum_sq")
        df_val = row.get("df")
        ms = ss / df_val if pd.notna(ss) and pd.notna(df_val) and df_val else np.nan
        item = [
            _term_label(idx, group_vars, covariates),
            _fmt(ss, 3),
            _fmt(df_val, 0),
            _fmt(ms, 3),
            _fmt(row.get("F"), 3),
            _fmt_p(row.get("PR(>F)")),
            "",
            "",
        ]
        if include_effect_size:
            partial_eta = (
                ss / (ss + residual_ss)
                if str(idx) != "Residual" and pd.notna(ss) and pd.notna(residual_ss) and (ss + residual_ss) > 0
                else np.nan
            )
            item.append(_fmt(partial_eta, 3) if str(idx) != "Residual" else "")
        rows.append(item)
    if rows:
        rows[0][6] = _fmt(model.rsquared, 3)
        rows[0][7] = _fmt(model.rsquared_adj, 3)

    sections = [
        _sec_advice(
            "1. 通过主体间效应检验判断分组变量和协变量是否与因变量存在显著关联；\n"
            "2. 若开启平行性检验，需要重点查看分组变量与协变量交互项是否显著；\n"
            "3. 控制协变量影响后，再查看分组变量对因变量的影响；\n"
            "4. 如开启事后多重比较，可进一步定位具体组别之间的差异。",
            title="分析步骤",
        ),
        _sec_table(
            "输出结果1：主体间效应检验",
            headers,
            rows,
            note="* p<0.1 ** p<0.05 *** p<0.01 **** p<0.001",
            description="上表展示主体间效应检验结果，用于判断分组变量、协变量及可选交互项是否对因变量存在显著影响。",
        ),
        _sec_smart(_smart_text(rows, group_vars, dependent, covariates, include_interaction)),
    ]
    design_by_group = {}
    for group_var in group_vars:
        adjusted_section, chart_section, design_by_level = _adjusted_means_section(temp, model, group_vars, group_var, dependent, covariates)
        sections.extend([adjusted_section, chart_section])
        design_by_group[group_var] = design_by_level
    if do_post_hoc:
        output_index = 2 + len(group_vars)
        for group_var in group_vars:
            sections.append(_post_hoc_section(model, design_by_group[group_var], post_hoc_method, group_var, output_index))
            output_index += 1
    sections.append(_sec_refs(_REFS_GENERAL))
    return {
        "name": METHOD_META["label"],
        "headers": headers,
        "rows": rows,
        "description": "协方差分析完成。",
        "sections": sections,
    }
