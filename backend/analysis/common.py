# -*- coding: utf-8 -*-
# spssgo
import json
import re

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import (
    chi2_contingency,
    chisquare,
    f_oneway,
    friedmanchisquare,
    kendalltau,
    kruskal,
    levene,
    mannwhitneyu,
    pearsonr,
    shapiro,
    spearmanr,
    ttest_ind,
    ttest_1samp,
    ttest_rel,
    wilcoxon,
)
from scipy.optimize import linprog
from itertools import combinations
import statsmodels.api as sm
from statsmodels.stats.contingency_tables import cochrans_q
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.metrics import cohen_kappa_score
from sklearn.manifold import MDS


def _fmt(val, decimals=3):
    if val is None:
        return "—"
    if isinstance(val, (int, np.integer)):
        return str(val)
    try:
        number = float(val)
        if not np.isfinite(number):
            return "—"
        return f"{number:.{decimals}f}"
    except (ValueError, TypeError):
        return str(val)


def _sig(p):
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return ""


def _p_expr(p):
    if p < 0.001:
        return "p<0.001"
    if p < 0.01:
        return "p<0.01"
    if p < 0.05:
        return "p<0.05"
    return f"p={_fmt(p, 3)}"


def _safe_float(value, default=np.nan):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _percentile_interval(samples, ci=0.95):
    values = pd.Series(samples, dtype="float64").replace([np.inf, -np.inf], np.nan).dropna()
    if values.empty:
        return (np.nan, np.nan)
    alpha = (1 - ci) / 2
    return (
        float(values.quantile(alpha)),
        float(values.quantile(1 - alpha)),
    )


def _bootstrap_distribution(data, stat_func, n_boot=2000, seed=42):
    if len(data) == 0:
        return []
    rng = np.random.default_rng(seed)
    n = len(data)
    distribution = []
    for _ in range(int(n_boot)):
        sample_idx = rng.integers(0, n, n)
        sample = data.iloc[sample_idx].reset_index(drop=True)
        try:
            distribution.append(float(stat_func(sample)))
        except Exception:
            continue
    return distribution


def _bootstrap_summary(data, stat_func, observed=None, n_boot=2000, seed=42, ci=0.95):
    distribution = _bootstrap_distribution(data, stat_func, n_boot=n_boot, seed=seed)
    if observed is None:
        try:
            observed = float(stat_func(data))
        except Exception:
            observed = np.nan
    lower, upper = _percentile_interval(distribution, ci=ci)
    return {
        "estimate": observed,
        "lower": lower,
        "upper": upper,
        "boot_n": len(distribution),
        "distribution": distribution,
    }


def _coef_ci(model, term, alpha=0.05):
    try:
        ci = model.conf_int(alpha=alpha)
    except Exception:
        return (np.nan, np.nan)
    if hasattr(ci, "loc"):
        try:
            bounds = ci.loc[term]
            return (_safe_float(bounds.iloc[0]), _safe_float(bounds.iloc[1]))
        except Exception:
            return (np.nan, np.nan)
    return (np.nan, np.nan)


def _normalize_benefit_frame(data, epsilon=1e-12):
    normalized = data.copy().astype(float)
    for column in normalized.columns:
        series = pd.to_numeric(normalized[column], errors="coerce")
        min_value = float(series.min())
        max_value = float(series.max())
        range_value = max_value - min_value
        if range_value == 0:
            normalized[column] = 1.0
        else:
            normalized[column] = (series - min_value) / range_value + epsilon
    return normalized


def _score_top10_rows(score_series):
    if score_series is None or len(score_series) == 0:
        return []
    return [[str(index), _fmt(value, 4)] for index, value in score_series.sort_values(ascending=False).head(10).items()]


def _resolve_cols(df, variables):
    found = []
    for value in variables:
        if value in df.columns:
            found.append(value)
    return found


def _selected_mask(series):
    normalized = series.astype(str).str.strip().str.lower()
    return (
        normalized.isin({"1", "1.0", "y", "yes", "true", "t", "是", "有", "选中", "同意"})
        | pd.to_numeric(series, errors="coerce").fillna(0).gt(0)
    )


def _sec_table(title, headers, rows, note=None, description=None):
    section = {"type": "table", "title": title, "headers": headers, "rows": rows}
    if note:
        section["note"] = note
    if description:
        section["description"] = description
    return section


def _sec_advice(content, title="分析建议"):
    return {"type": "advice", "title": title, "content": content}


def _sec_smart(content):
    return {"type": "smart_analysis", "title": "智能分析", "content": content}


def _sec_refs(items):
    return {"type": "references", "title": "参考文献", "items": items}


def _sec_charts(title, charts, description=None):
    section = {"type": "charts", "title": title, "charts": charts}
    if description:
        section["description"] = description
    return section


def _hist_chart(var_name, series):
    values = pd.to_numeric(series, errors="coerce").dropna()
    if len(values) == 0:
        return None
    unique_count = len(values.unique())
    bin_count = min(10, max(5, unique_count))
    counts, bin_edges = np.histogram(values, bins=bin_count)
    return {
        "chartType": "histogram",
        "title": f"{var_name}直方图",
        "varName": var_name,
        "data": {
            "binEdges": [round(float(edge), 4) for edge in bin_edges],
            "counts": [int(count) for count in counts],
        },
    }


def _box_chart(var_name, series):
    values = pd.to_numeric(series, errors="coerce").dropna()
    if len(values) == 0:
        return None
    q1 = float(values.quantile(0.25))
    q3 = float(values.quantile(0.75))
    iqr = q3 - q1
    lower_fence = q1 - 1.5 * iqr
    upper_fence = q3 + 1.5 * iqr
    non_outliers = values[(values >= lower_fence) & (values <= upper_fence)]
    whisker_low = float(non_outliers.min()) if len(non_outliers) > 0 else q1
    whisker_high = float(non_outliers.max()) if len(non_outliers) > 0 else q3
    outliers = [round(float(value), 4) for value in values[(values < lower_fence) | (values > upper_fence)].tolist()]
    return {
        "chartType": "boxplot",
        "title": f"{var_name}箱型图",
        "varName": var_name,
        "data": {
            "whiskerLow": round(whisker_low, 4),
            "q1": round(q1, 4),
            "median": round(float(values.median()), 4),
            "q3": round(q3, 4),
            "whiskerHigh": round(whisker_high, 4),
            "outliers": outliers,
        },
    }


def _build_missing_table(df, variables):
    subset = df[variables].apply(pd.to_numeric, errors="coerce")
    valid = subset.dropna().shape[0]
    total = len(df)
    excluded = total - valid
    headers = ["项", "样本数", "占比"]
    rows = [
        ["有效样本", str(valid), _fmt(valid / total * 100 if total else 0, 1) + "%"],
        ["排除无效样本", str(excluded), _fmt(excluded / total * 100 if total else 0, 1) + "%"],
        ["总计", str(total), "100%"],
    ]
    description = (
        "上表格展示进入算法模型时有效样本和排除在外的无效样本情况。"
        "如果某样本在任意一个分析项上出现缺失数据，该类样本无法进入模型分析。"
    )
    return _sec_table("样本缺失情况汇总", headers, rows, description=description)


def _collect_analysis_variables(params, df):
    variables = []

    def add(value):
        if isinstance(value, str):
            if value in df.columns and value not in variables:
                variables.append(value)
        elif isinstance(value, (list, tuple, set)):
            for item in value:
                add(item)
        elif isinstance(value, dict):
            for item in value.values():
                add(item)

    for key in (
        "variables",
        "items",
        "items_groups",
        "group_vars",
        "dependent",
        "predictors",
        "test_vars",
        "group_var",
        "summary_vars",
        "var1",
        "var2",
        "x",
        "y",
    ):
        add(params.get(key))
    return variables


def _build_variable_missing_table(df, variables):
    headers = [
        "名称",
        "样本量",
        "缺失样本量",
        "缺失数据行号",
        "最小值",
        "最大值",
        "平均值",
        "标准差",
        "中位数",
        "是否数字恒定",
    ]
    rows = []
    total = len(df)
    for variable in variables:
        raw = df[variable]
        numeric = pd.to_numeric(raw, errors="coerce")
        present_mask = raw.notna()
        clean_numeric = numeric[present_mask].dropna()
        clean_raw = raw[present_mask]
        missing_index = (raw[raw.isna()].index + 1).tolist()
        unique_count = clean_raw.nunique(dropna=True)
        rows.append([
            variable,
            str(total),
            str(total - int(present_mask.sum())),
            "、".join(map(str, missing_index)) if missing_index else "无",
            _fmt(clean_numeric.min()) if len(clean_numeric) else "—",
            _fmt(clean_numeric.max()) if len(clean_numeric) else "—",
            _fmt(clean_numeric.mean()) if len(clean_numeric) else "—",
            _fmt(clean_numeric.std()) if len(clean_numeric) > 1 else (
                "0.000" if len(clean_numeric) == 1 else "—"
            ),
            _fmt(clean_numeric.median()) if len(clean_numeric) else "—",
            "是" if unique_count == 1 and len(clean_raw) else "否",
        ])
    description = (
        "缺失分析表展示每个变量的缺失样本、缺失行号及基础指标，"
        "用于判断变量是否适合继续进入模型。"
    )
    return _sec_table("缺失分析", headers, rows, description=description)


def append_optional_missing_analysis(result, df, params):
    if params.get("include_missing_analysis") not in (True, "true", "1", 1, "是"):
        return result
    items = result if isinstance(result, list) else [result]
    variables = _collect_analysis_variables(params, df)
    if not variables:
        return result
    for item in items:
        sections = item.setdefault("sections", [])
        if any(section.get("title") == "缺失分析" for section in sections):
            continue
        sections.append(_build_variable_missing_table(df, variables))
    return result


_REFS_GENERAL = [
]
_REFS_RELIABILITY = _REFS_GENERAL + [
    "[3] Eisinga R, Te Grotenhuis M, Pelzer B. The reliability of a two-item scale: Pearson, Cronbach, or Spearman-Brown?[J]. International Journal of Public Health, 2013, 58(4):637-642.",
]
_REFS_CORRELATION = _REFS_GENERAL + [
    "[3] Cohen J. Statistical power analysis for the behavioral sciences (2nd ed.)[M]. Lawrence Erlbaum Associates, 1988.",
]
_REFS_REGRESSION = _REFS_GENERAL + [
    "[3] 温忠麟,叶宝娟. 中介效应分析:方法学发展、模型及应用[J]. 心理学报, 2014, 46(5):714-726.",
]


def normalized_label_dict(value_labels):
    if not value_labels:
        return {}
    return {str(key): value for key, value in value_labels.items() if value not in ("", None)}


def build_preview_result(name, params, message, suggestions=None):
    suggestions = suggestions or []
    rows = []
    for key, value in (params or {}).items():
        if isinstance(value, list):
            display = ", ".join(str(item) for item in value)
        elif isinstance(value, dict):
            display = json.dumps(value, ensure_ascii=False)
        else:
            display = str(value)
        rows.append([str(key), display])
    if not rows:
        rows.append(["参数", "当前未传入参数"])

    sections = [
        _sec_table("当前方法状态", ["项", "内容"], [["方法", name], ["状态", "已完成独立模块解耦"], ["说明", message]]),
        _sec_table("本次输入参数", ["参数", "值"], rows),
    ]
    if suggestions:
        sections.append(_sec_advice("\n".join(suggestions), "使用建议"))
    sections.append(_sec_smart(f"{name} 已具备独立入口、独立元数据和独立执行模块，后续算法迭代可直接在当前文件内完成。"))
    return {
        "name": name,
        "headers": ["项", "内容"],
        "rows": [["方法", name], ["状态", "已完成独立模块解耦"]],
        "description": message,
        "sections": sections,
    }


def build_slot_param_example(meta):
    example = {}
    for slot in meta.get("slots", []):
        slot_type = slot.get("type", "single")
        accept = slot.get("accept", "any")
        key = slot.get("key")
        if not key:
            continue
        if slot_type == "multiple":
            prefix = "数值变量" if accept == "numeric" else "分类变量" if accept == "categorical" else "变量"
            min_count = max(int(slot.get("min", 1) or 1), 1)
            example[key] = [f"{prefix}{idx + 1}" for idx in range(min_count)]
        else:
            if accept == "numeric":
                example[key] = "数值变量1"
            elif accept == "categorical":
                example[key] = "分类变量1"
            else:
                example[key] = "变量1"

    for option in meta.get("options", []):
        key = option.get("key")
        if not key:
            continue
        example[key] = option.get("default") or (option.get("choices") or [""])[0]
    return example


def build_params_reliability(slot_values):
    variables = slot_values.get("variables", [])
    params = {"items_groups": {"分析变量": variables}}
    if "type" in slot_values:
        params["type"] = slot_values["type"]
    return params


def build_params_factor(slot_values):
    variables = slot_values.get("variables", [])
    return {"items": variables, "scale_name": "量表"}


def build_params_t_test(slot_values):
    return {
        "group_var": slot_values.get("group_var", ""),
        "dependent": slot_values.get("test_vars", []),
    }


def build_params_anova(slot_values):
    return {
        "group_var": slot_values.get("group_var", ""),
        "dependent": slot_values.get("test_vars", []),
        "post_hoc": slot_values.get("post_hoc", "LSD"),
    }


def build_params_regression(slot_values):
    return {
        "dependent": slot_values.get("dependent", ""),
        "predictors": slot_values.get("predictors", []),
    }


PARAM_BUILDERS = {
    "direct": lambda slot_values: slot_values,
    "reliability": build_params_reliability,
    "factor": build_params_factor,
    "t_test": build_params_t_test,
    "anova": build_params_anova,
    "regression": build_params_regression,
}


def inject_frequency_metadata(params, metadata_map):
    enriched = dict(params)
    variables = enriched.get("variables") or []
    if isinstance(variables, str):
        variables = [variables]
    variable = enriched.get("variable", "")
    if variable and variable not in variables:
        variables = [variable] + list(variables)
    enriched["labels_by_variable"] = {
        variable_name: normalized_label_dict(metadata_map.get(variable_name, {}).get("value_labels", {}))
        for variable_name in variables
        if variable_name
    }
    if variable:
        enriched["labels"] = enriched["labels_by_variable"].get(variable) or normalized_label_dict(metadata_map.get(variable, {}).get("value_labels", {}))
    return enriched


def inject_multiple_choice_metadata(params, metadata_map):
    enriched = dict(params)
    variables = enriched.get("variables", []) or []
    enriched["variable_labels"] = {
        variable: metadata_map.get(variable, {}).get("display_name") or variable
        for variable in variables
    }
    return enriched


def inject_group_metadata(params, metadata_map):
    enriched = dict(params)
    group_var = enriched.get("group_var", "")
    if group_var:
        enriched["group_labels"] = normalized_label_dict(metadata_map.get(group_var, {}).get("value_labels", {}))
    return enriched


def inject_cross_metadata(params, metadata_map):
    enriched = dict(params)
    var1 = enriched.get("var1", "")
    var2 = enriched.get("var2", "")
    group_var = enriched.get("group_var", "") or var1
    variables = enriched.get("variables") or []
    if isinstance(variables, str):
        variables = [variables]
    if var2 and var2 not in variables:
        variables = [var2] + list(variables)

    if var1:
        enriched["var1_labels"] = normalized_label_dict(metadata_map.get(var1, {}).get("value_labels", {}))
    if var2:
        enriched["var2_labels"] = normalized_label_dict(metadata_map.get(var2, {}).get("value_labels", {}))
    if group_var:
        enriched["group_labels"] = normalized_label_dict(
            metadata_map.get(group_var, {}).get("value_labels", {})
        )
    enriched["labels_by_variable"] = {
        variable: normalized_label_dict(
            metadata_map.get(variable, {}).get("value_labels", {})
        )
        for variable in variables
        if variable
    }
    return enriched


METADATA_INJECTORS = {
    "frequency_labels": inject_frequency_metadata,
    "multiple_choice_labels": inject_multiple_choice_metadata,
    "group_labels": inject_group_metadata,
    "cross_labels": inject_cross_metadata,
}


__all__ = [
    "MDS",
    "PARAM_BUILDERS",
    "METADATA_INJECTORS",
    "_REFS_CORRELATION",
    "_REFS_GENERAL",
    "_REFS_REGRESSION",
    "_REFS_RELIABILITY",
    "_box_chart",
    "_build_missing_table",
    "_build_variable_missing_table",
    "append_optional_missing_analysis",
    "_fmt",
    "_hist_chart",
    "_normalize_benefit_frame",
    "_p_expr",
    "_percentile_interval",
    "_resolve_cols",
    "_safe_float",
    "_score_top10_rows",
    "_sec_advice",
    "_sec_charts",
    "_sec_refs",
    "_sec_smart",
    "_sec_table",
    "_selected_mask",
    "_sig",
    "_bootstrap_distribution",
    "_bootstrap_summary",
    "_coef_ci",
    "build_preview_result",
    "build_slot_param_example",
    "chi2_contingency",
    "chisquare",
    "combinations",
    "cochrans_q",
    "cohen_kappa_score",
    "f_oneway",
    "friedmanchisquare",
    "json",
    "kendalltau",
    "kruskal",
    "levene",
    "linprog",
    "mannwhitneyu",
    "np",
    "normalized_label_dict",
    "pd",
    "pearsonr",
    "re",
    "shapiro",
    "sm",
    "spearmanr",
    "stats",
    "ttest_1samp",
    "ttest_ind",
    "ttest_rel",
    "variance_inflation_factor",
    "wilcoxon",
]
