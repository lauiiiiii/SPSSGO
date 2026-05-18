# -*- coding: utf-8 -*-
# 双因素方差分析主流程：这里负责模型、均值图、交叉均值表和可选事后比较。
# 三因素/多因素还复用旧 helper，别把它们和这个 SPSSAU/SPSSPRO 风格输出绑死。
import math

from backend.analysis.common import *

METHOD_KEY = "two_way_anova"
METHOD_META = {'label': '双因素方差分析',
 'category': '差异对比分析包',
 'description': '检验两个分类因素及其交互作用对因变量的影响',
 'order': 40,
 'slots': [{'key': 'factors', 'label': '分组变量X', 'type': 'multiple', 'accept': 'categorical', 'min': 2, 'max': 2, 'hint': '放入2个分组因素'},
           {'key': 'dependent', 'label': '因变量Y', 'type': 'single', 'accept': 'numeric', 'hint': '放入因变量'},
           {'key': 'covariates', 'label': '协变量', 'type': 'multiple', 'accept': 'numeric', 'min': 0, 'hint': '可选，放入需要控制的协变量'}],
 'options': [{'key': 'include_interaction', 'label': '分析交互效应', 'type': 'checkbox', 'default': True},
             {'key': 'do_post_hoc', 'label': '事后多重比较', 'type': 'checkbox', 'default': False},
             {'key': 'post_hoc_method', 'label': '方法选择', 'choices': ['LSD', 'bonf', 'sidak'], 'default': 'LSD'}],
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


def _as_list(value):
    if isinstance(value, list):
        return [item for item in value if item]
    return [value] if value else []


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


def _term_label(term, factor1, factor2):
    mapping = {
        f"C(Q('{factor1}'))": factor1,
        f"C(Q('{factor2}'))": factor2,
        f"C(Q('{factor1}')):C(Q('{factor2}'))": f"{factor1} * {factor2}",
        "Residual": "误差",
    }
    text = str(term)
    if text.startswith("Q('") and text.endswith("')"):
        return text[3:-2]
    return mapping.get(text, text)


def _formula_term(factor):
    return f"C(Q('{factor}'))"


def _mean_chart(factor1, factor2, dependent, temp):
    factor1_levels = sorted(temp[factor1].dropna().unique())
    factor2_levels = sorted(temp[factor2].dropna().unique())
    metrics = {}
    for level2 in factor2_levels:
        values = []
        for level1 in factor1_levels:
            series = temp.loc[(temp[factor1] == level1) & (temp[factor2] == level2), dependent]
            values.append(float(series.mean()) if len(series) else 0)
        metrics[str(level2)] = values
    first_metric = next(iter(metrics), "")
    return {
        "chartType": "metric_comparison",
        "title": f"{factor1}和{factor2}的均值对比图",
        "data": {
            "metric": first_metric,
            "labels": [str(item) for item in factor1_levels],
            "values": metrics.get(first_metric, []),
            "metrics": metrics,
            "multiSeries": True,
            "defaultMode": "line",
            "displayTitle": f"{factor1}和{factor2}的均值对比图",
        },
    }


def _mean_cross_table(factor1, factor2, dependent, temp):
    factor1_levels = sorted(temp[factor1].dropna().unique())
    factor2_levels = sorted(temp[factor2].dropna().unique())
    headers = [factor2, *[str(item) for item in factor1_levels]]
    rows = []
    for level2 in factor2_levels:
        row = [str(level2)]
        for level1 in factor1_levels:
            series = temp.loc[(temp[factor1] == level1) & (temp[factor2] == level2), dependent]
            if len(series):
                row.append(f"{_fmt(series.mean(), 3)}±{_fmt(series.std(), 3)}")
            else:
                row.append("null±null")
        rows.append(row)
    return _sec_table(
        f"{factor1}和{factor2}的均值对比(平均值±标准差)",
        headers,
        rows,
        description="上表展示两个分组因素交叉后各单元格的均值和标准差，用于配合均值图查看差异方向。",
    )


def _sample_summary(total_n, valid_n):
    invalid_n = max(total_n - valid_n, 0)
    total = total_n or 1
    return _sec_table(
        "样本缺失情况汇总",
        ["项", "样本数", "占比"],
        [
            ["有效样本", str(valid_n), f"{valid_n / total * 100:.3f}%"],
            ["排除无效样本", str(invalid_n), f"{invalid_n / total * 100:.3f}%"],
            ["总计", str(total_n), "100%"],
        ],
        description="上表展示进入模型时有效样本和排除样本情况；样本缺失会影响模型可解释性。",
    )


def _model_design_matrix(model, frame):
    from patsy import build_design_matrices

    frame = frame.copy()
    for col in frame.columns:
        if not pd.api.types.is_numeric_dtype(frame[col]):
            frame[col] = frame[col].astype("object")
    design_info = model.model.data.design_info
    return np.asarray(build_design_matrices([design_info], frame, return_type="dataframe")[0], dtype=float)


def _post_hoc_section(temp, factor, model, df_resid, method, output_title=None):
    levels = sorted(temp[factor].dropna().unique())
    pair_count = max(len(list(combinations(levels, 2))), 1)
    cov = np.asarray(model.cov_params(), dtype=float)
    params = np.asarray(model.params, dtype=float)
    base_design = {}
    for level in levels:
        frame = temp.copy()
        frame[factor] = level
        base_design[level] = _model_design_matrix(model, frame).mean(axis=0)
    rows = []
    for level_i, level_j in combinations(levels, 2):
        for i, j in [(level_i, level_j), (level_j, level_i)]:
            contrast = base_design[i] - base_design[j]
            diff = float(contrast @ params)
            se = math.sqrt(float(contrast @ cov @ contrast.T)) if df_resid > 0 else np.nan
            t_value = diff / se if np.isfinite(se) and se > 0 else 0
            p_raw = 2 * stats.t.sf(abs(t_value), df_resid) if df_resid > 0 else np.nan
            if method == "bonf":
                p_value = min(float(p_raw) * pair_count, 1.0)
            elif method == "sidak":
                p_value = 1 - (1 - float(p_raw)) ** pair_count
            elif method == "tukey":
                q_value = abs(t_value) * math.sqrt(2)
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
        output_title or f"{factor}事后多重比较结果",
        [f"{factor}(I)", f"{factor}(J)", "平均值差值(I-J)", "标准误差", "P", "95%置信区间下限", "95%置信区间上限"],
        rows,
        description=f"上表使用{method}方法基于模型调整均值进行事后多重比较，对{factor}各水平之间的具体差异进行分析。",
    )


def _smart_text(rows, factor1, factor2, dependent, include_interaction, covariates):
    parts = [f"从上表可知，以{factor1}和{factor2}为分组因素、{dependent}为因变量进行双因素方差分析。"]
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
    if not include_interaction:
        parts.append("本次未纳入交互项，主效应解释不包含两因素共同作用。")
    return "\n".join(parts)


def run(df, params):
    try:
        import statsmodels.formula.api as smf
        from statsmodels.stats.anova import anova_lm
    except Exception as exc:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": f"缺少方差分析依赖：{str(exc)}"}

    raw_factors = _as_list(params.get("factors", []))
    factors = _resolve_cols(df, raw_factors)
    if raw_factors:
        if len(factors) != 2:
            return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "分组变量X需要放入2个定类变量。"}
        factor1, factor2 = factors
    else:
        # 兼容历史任务，旧版本把两个因素拆成 factor1/factor2。
        factor1 = params.get("factor1", "")
        factor2 = params.get("factor2", "")
    dependent = params.get("dependent", "")
    covariates = _resolve_cols(df, _as_list(params.get("covariates", [])))
    include_interaction = params.get("include_interaction", True) not in (False, "false", "0", 0, "否")
    do_post_hoc = params.get("do_post_hoc", False) in (True, "true", "1", 1, "是")
    post_hoc_method = str(params.get("post_hoc_method", "LSD") or "LSD")

    needed = [factor1, factor2, dependent] + covariates
    if any(not col or col not in df.columns for col in needed):
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "因素变量、因变量或协变量不存在。"}

    temp = df[needed].copy()
    total_n = len(temp)
    temp[dependent] = pd.to_numeric(temp[dependent], errors="coerce")
    for cov in covariates:
        temp[cov] = pd.to_numeric(temp[cov], errors="coerce")
    temp = temp.dropna()
    for factor in [factor1, factor2]:
        temp[factor] = temp[factor].astype("object")
    if len(temp) < 8:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效样本不足。"}

    terms = [_formula_term(factor1), _formula_term(factor2)]
    if include_interaction:
        terms.append(f"{_formula_term(factor1)}:{_formula_term(factor2)}")
    terms.extend([f"Q('{cov}')" for cov in covariates])
    formula = f"Q('{dependent}') ~ " + " + ".join(terms)
    model = smf.ols(formula, data=temp).fit()
    table = anova_lm(model, typ=2)

    headers = ["项", "平方和", "自由度", "均方", "F", "P", "R²", "调整R²"]
    rows = []
    for idx, row in table.iterrows():
        ss = row.get("sum_sq")
        df_val = row.get("df")
        ms = ss / df_val if pd.notna(ss) and pd.notna(df_val) and df_val else np.nan
        rows.append([
            _term_label(idx, factor1, factor2),
            _fmt(ss, 3),
            _fmt(df_val, 0),
            _fmt(ms, 3),
            _fmt(row.get("F"), 3),
            _fmt_p(row.get("PR(>F)")),
            "",
            "",
        ])
    if rows:
        rows[0][-2] = _fmt(model.rsquared, 3)
        rows[0][-1] = _fmt(model.rsquared_adj, 3)

    sections = [
        _sec_advice(
            "1. 双因素方差分析用于判断两个分组因素是否对因变量产生显著影响；\n"
            "2. 先看主效应和交互效应的P值，若P<0.05说明影响显著；\n"
            "3. 若交互效应显著，应优先结合均值对比图解释不同组合下的差异；\n"
            "4. 如开启事后多重比较，可进一步定位具体水平之间的差异。",
            title="分析步骤",
        ),
        _sec_table(
            "输出结果1：双因素方差分析结果",
            headers,
            rows,
            note="* p<0.1 ** p<0.05 *** p<0.01 **** p<0.001",
            description="上表展示双因素方差分析结果；主效应或交互效应显著时，可继续结合均值图和事后比较结果解释差异来源。",
        ),
        _sec_smart(_smart_text(rows, factor1, factor2, dependent, include_interaction, covariates)),
        _sec_charts(
            "输出结果2：均值对比图",
            [_mean_chart(factor1, factor2, dependent, temp)],
            "上图展示双因素方差分析的均值结果，通过比较不同分组变量的均值以及交叉情况，可挖掘其差异关系。",
        ),
        _mean_cross_table(factor1, factor2, dependent, temp),
        _sample_summary(total_n, int(model.nobs)),
    ]

    if do_post_hoc:
        df_resid = float(table.loc["Residual", "df"]) if "Residual" in table.index else np.nan
        sections.append(_post_hoc_section(temp, factor1, model, df_resid, post_hoc_method, "输出结果3：事后多重比较结果"))
        sections.append(_post_hoc_section(temp, factor2, model, df_resid, post_hoc_method))

    sections.append(_sec_refs(_REFS_GENERAL))
    return {
        "name": METHOD_META["label"],
        "headers": headers,
        "rows": rows,
        "description": "双因素方差分析完成。",
        "sections": sections,
    }
