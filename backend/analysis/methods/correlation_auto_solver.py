# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "correlation_auto_solver"
METHOD_META = {
 'label': '相关性分析自动求解器',
 'category': '数据检验',
 'description': '自动识别变量特征并推荐合适的相关或一致性分析方法',
 'order': 80,
 'slots': [
     {'key': 'variables', 'label': '分析变量', 'type': 'multiple', 'accept': 'any', 'min': 2, 'hint': '放入需要自动判断方法的两个或多个变量'}
 ],
 'options': [],
 'param_builder': 'direct'
}


def _series_profile(df, col):
    raw = df[col]
    non_null = raw.dropna()
    numeric = pd.to_numeric(raw, errors="coerce")
    numeric_non_null = numeric.dropna()
    numeric_ratio = len(numeric_non_null) / len(non_null) if len(non_null) else 0
    unique_count = int(non_null.nunique())
    normalized = non_null.astype(str).str.strip().str.lower()
    binary_tokens = {"0", "1", "0.0", "1.0", "true", "false", "yes", "no", "y", "n", "是", "否"}
    is_binary = unique_count == 2 and (set(normalized.unique()) <= binary_tokens or numeric_non_null.nunique() == 2)
    is_numeric = numeric_ratio >= 0.9
    normality_p = np.nan
    if is_numeric and len(numeric_non_null) >= 3 and numeric_non_null.nunique() >= 3 and len(numeric_non_null) <= 5000:
        try:
            _, normality_p = shapiro(numeric_non_null)
        except Exception:
            normality_p = np.nan
    if is_binary:
        var_type = "二分类"
    elif is_numeric and unique_count <= 7:
        var_type = "等级/离散数值"
    elif is_numeric:
        var_type = "连续数值"
    else:
        var_type = "分类"
    return {
        "name": col,
        "type": var_type,
        "is_binary": is_binary,
        "is_numeric": is_numeric,
        "n": int(len(non_null)),
        "unique_count": unique_count,
        "normality_p": normality_p,
        "normality_ok": bool(pd.notna(normality_p) and normality_p > 0.05),
    }


def _pairwise_numeric_result(df, variables, method_name):
    headers = ["变量"] + variables
    rows = []
    descs = []
    corr_func = pearsonr if method_name == "Pearson" else spearmanr
    stat_symbol = "r" if method_name == "Pearson" else "ρ"
    for v1 in variables:
        row = [v1]
        for v2 in variables:
            s1 = pd.to_numeric(df[v1], errors="coerce")
            s2 = pd.to_numeric(df[v2], errors="coerce")
            mask = s1.notna() & s2.notna()
            if v1 == v2:
                row.append("1")
                continue
            if mask.sum() < 3 or s1[mask].nunique() < 2 or s2[mask].nunique() < 2:
                row.append("—")
                continue
            stat, p = corr_func(s1[mask], s2[mask])
            row.append(_fmt(stat, 3) + _sig(p))
        rows.append(row)

    for v1, v2 in combinations(variables, 2):
        s1 = pd.to_numeric(df[v1], errors="coerce")
        s2 = pd.to_numeric(df[v2], errors="coerce")
        mask = s1.notna() & s2.notna()
        if mask.sum() < 3 or s1[mask].nunique() < 2 or s2[mask].nunique() < 2:
            continue
        stat, p = corr_func(s1[mask], s2[mask])
        direction = "正" if stat > 0 else "负"
        descs.append(f"{v1}与{v2}呈{direction}相关（{stat_symbol}={_fmt(stat, 3)}，{_p_expr(p)}）")
    return rows, descs


def _recommendations(profiles):
    all_numeric = all(item["is_numeric"] for item in profiles)
    all_binary = all(item["is_binary"] for item in profiles)
    all_continuous = all(item["type"] == "连续数值" for item in profiles)
    all_normal = all(item["normality_ok"] for item in profiles if item["is_numeric"])
    count = len(profiles)
    recs = []

    if count >= 3 and all_binary:
        recs.append(("Cochran's Q检验", "当前变量均为二分类且数量不少于 3 个，适合检验相关样本比例差异。"))
        return recs
    if count == 2 and all(item["type"] == "分类" or item["is_binary"] for item in profiles):
        recs.append(("Kappa一致性检验", "当前为两个分类/判定变量，适合评估一致性。"))
        return recs
    if count >= 3 and all_numeric:
        recs.append(("组内相关系数", "当前为多个数值型评价变量，若你的关注点是评价者一致性，可优先查看 ICC。"))
        recs.append(("Kendall一致性检验", "当前为多个评价变量，若你的关注点是排序一致性，可同时查看 Kendall’s W。"))
    if count >= 2 and all_numeric:
        if all_continuous and all_normal:
            recs.insert(0, ("相关性分析", "变量整体更接近连续数值且正态性基本可接受，优先推荐 Pearson 相关分析。"))
        else:
            recs.insert(0, ("Spearman 等级相关", "变量存在等级特征、离散特征或正态性不足，更适合使用 Spearman 等级相关。"))
    return recs


def run(df, params):
    variables = _resolve_cols(df, params.get("variables", []))
    if len(variables) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "至少需要放入 2 个变量。" }

    profiles = [_series_profile(df, col) for col in variables]
    profile_rows = []
    for item in profiles:
        normality_text = "—"
        if item["is_numeric"]:
            normality_text = _fmt(item["normality_p"], 4) if pd.notna(item["normality_p"]) else "样本/类型不适用"
        profile_rows.append([
            item["name"],
            item["type"],
            str(item["n"]),
            str(item["unique_count"]),
            normality_text,
        ])

    recommendations = _recommendations(profiles)
    rec_rows = [[str(idx + 1), name, reason] for idx, (name, reason) in enumerate(recommendations)]

    primary = recommendations[0][0] if recommendations else "相关性分析"
    result_rows = []
    result_headers = []
    smart_parts = []
    all_numeric = all(item["is_numeric"] for item in profiles)
    all_binary = all(item["is_binary"] for item in profiles)

    if primary in {"相关性分析", "Spearman 等级相关"} and all_numeric:
        method_name = "Pearson" if primary == "相关性分析" else "Spearman"
        result_headers = ["变量"] + variables
        result_rows, descs = _pairwise_numeric_result(df, variables, method_name)
        smart_parts.extend(descs[:6])
    elif primary == "Cochran's Q检验" and all_binary and len(variables) >= 3:
        binary_df = df[variables].copy().apply(lambda s: _selected_mask(s).astype(int))
        valid = binary_df.dropna()
        q_result = cochrans_q(valid.to_numpy())
        result_headers = ["统计量", "值"]
        result_rows = [
            ["Q", _fmt(q_result.statistic, 4)],
            ["df", str(len(variables) - 1)],
            ["p", _fmt(q_result.pvalue, 4)],
        ]
        smart_parts.append(f"自动识别为相关二分类变量集合，Cochran's Q={_fmt(q_result.statistic, 3)}，{_p_expr(q_result.pvalue)}。")
    elif primary == "Kappa一致性检验" and len(variables) == 2:
        temp = df[variables].dropna().astype(str)
        kappa = cohen_kappa_score(temp[variables[0]], temp[variables[1]])
        agree = float((temp[variables[0]] == temp[variables[1]]).mean()) if len(temp) else np.nan
        result_headers = ["指标", "值"]
        result_rows = [["观察一致率", _fmt(agree, 4)], ["Kappa", _fmt(kappa, 4)]]
        smart_parts.append(f"自动识别为两个分类判定变量，Kappa={_fmt(kappa, 3)}。")
    elif primary == "组内相关系数" and all_numeric and len(variables) >= 2:
        temp = df[variables].apply(pd.to_numeric, errors="coerce").dropna()
        if len(temp) >= 2:
            n, k = temp.shape
            mean_raters = temp.mean(axis=1)
            grand_mean = float(temp.to_numpy().mean())
            ss_between = k * ((mean_raters - grand_mean) ** 2).sum()
            ss_within = ((temp.sub(mean_raters, axis=0)) ** 2).sum().sum()
            ms_between = ss_between / (n - 1) if n > 1 else np.nan
            ms_within = ss_within / (n * (k - 1)) if k > 1 and n > 0 else np.nan
            icc = (ms_between - ms_within) / (ms_between + (k - 1) * ms_within) if pd.notna(ms_between) and pd.notna(ms_within) and (ms_between + (k - 1) * ms_within) != 0 else np.nan
        else:
            icc = np.nan
        result_headers = ["指标", "值"]
        result_rows = [["ICC(1,k)近似", _fmt(icc, 4)], ["变量数", str(len(variables))]]
        smart_parts.append(f"自动识别为多个数值评价变量，ICC 近似值为 {_fmt(icc, 3)}。")

    sections = [
        _sec_table("变量识别结果", ["变量", "识别类型", "有效样本", "唯一值数", "Shapiro-Wilk p"], profile_rows, description="自动求解器会先识别变量形态，再根据变量组合推荐更合适的相关或一致性分析方法。"),
        _sec_table("推荐方法", ["优先级", "推荐方法", "推荐理由"], rec_rows or [["1", "相关性分析", "当前数据可先从基础相关分析开始查看变量间关系。"]]),
    ]
    if result_headers and result_rows:
        sections.append(_sec_table("自动求解结果", result_headers, result_rows, note="注：此处展示的是自动求解器根据当前变量组合选出的首选结果。"))
    sections.append(_sec_advice(
        "自动求解器适合在你不确定该先用 Pearson、Spearman、Cochran's Q、Kappa 还是 ICC 时快速给出方向；"
        "如果你已经明确研究问题，比如关注一致性而不是相关性，仍建议直接使用对应的专业方法页。"
    ))
    smart_text = "；".join(smart_parts) if smart_parts else f"自动推荐的首选方法为“{primary}”。"
    sections.append(_sec_smart(smart_text))
    sections.append(_sec_refs(_REFS_CORRELATION))

    return {
        "name": METHOD_META["label"],
        "headers": result_headers or ["优先级", "推荐方法", "推荐理由"],
        "rows": result_rows or rec_rows,
        "description": f"自动求解完成，首选推荐方法为“{primary}”。",
        "sections": sections,
    }
