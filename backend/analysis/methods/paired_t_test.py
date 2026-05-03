# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "paired_t_test"
METHOD_META = {'label': '配对样本T检验',
 'category': '差异对比分析包',
 'description': '比较同一组受试者在两个条件/时间点上的均值差异',
 'slots': [{'key': 'var1',
            'label': '变量1',
            'type': 'single',
            'accept': 'numeric',
            'hint': '放入第一个测量变量'},
           {'key': 'var2',
            'label': '变量2',
            'type': 'single',
            'accept': 'numeric',
            'hint': '放入第二个测量变量'}],
 'options': [],
 'param_builder': 'direct'}

def paired_t_test(df, params):
    """
    配对样本 t 检验，含效应量 Cohen's d

    @param df: 数据 DataFrame
    @param params: 包含 var1, var2 的参数字典
    @return: 含 sections 的结果字典
    """
    var1 = params.get("var1", "")
    var2 = params.get("var2", "")
    if var1 not in df.columns or var2 not in df.columns:
        return {"name": "配对样本t检验", "headers": [], "rows": [], "description": "变量不存在。"}

    temp = df[[var1, var2]].apply(pd.to_numeric, errors="coerce").dropna()
    s1, s2 = temp[var1], temp[var2]
    t_val, t_p = ttest_rel(s1, s2)
    diff = s1 - s2
    diff_std = diff.std(ddof=1)
    cohens_d = diff.mean() / diff_std if diff_std > 0 else 0
    n = len(s1)
    corr, corr_p = pearsonr(s1, s2) if n >= 3 and s1.nunique() > 1 and s2.nunique() > 1 else (np.nan, np.nan)
    se_diff = diff_std / np.sqrt(n) if n > 0 else np.nan
    t_crit = stats.t.ppf(0.975, n - 1) if n > 1 else np.nan
    ci_low = diff.mean() - t_crit * se_diff if n > 1 else np.nan
    ci_high = diff.mean() + t_crit * se_diff if n > 1 else np.nan

    sections = []

    # 表 1：配对描述统计
    desc_headers = ["变量", "N", "均值", "标准差"]
    desc_rows = [
        [var1, str(n), _fmt(s1.mean()), _fmt(s1.std(ddof=1)), _fmt(s1.std(ddof=1) / np.sqrt(n) if n else np.nan)],
        [var2, str(n), _fmt(s2.mean()), _fmt(s2.std(ddof=1)), _fmt(s2.std(ddof=1) / np.sqrt(n) if n else np.nan)],
        ["差值", str(n), _fmt(diff.mean()), _fmt(diff_std), _fmt(se_diff)],
    ]
    desc_headers = ["变量", "N", "均值", "标准差", "标准误"]
    sections.append(_sec_table("配对描述统计", desc_headers, desc_rows))

    pair_corr_headers = ["配对变量", "N", "相关系数", "p"]
    pair_corr_rows = [[f"{var1} & {var2}", str(n), _fmt(corr, 4), _fmt(corr_p, 4)]]
    sections.append(_sec_table("配对样本相关", pair_corr_headers, pair_corr_rows, description="该表对应 SPSS 常见的 Paired Samples Correlations 输出。"))

    # 表 2：检验结果
    d_level = "大" if abs(cohens_d) >= 0.8 else ("中等" if abs(cohens_d) >= 0.5 else "小")
    t_headers = ["均值差", "差值标准差", "差值标准误", "95% CI 下限", "95% CI 上限", "t", "df", "p", "Cohen's d", "效应量"]
    t_rows = [[_fmt(diff.mean()), _fmt(diff_std), _fmt(se_diff), _fmt(ci_low), _fmt(ci_high), _fmt(t_val, 2), str(n - 1), _fmt(t_p), _fmt(abs(cohens_d), 2), d_level]]
    sections.append(_sec_table("配对样本t检验", t_headers, t_rows))

    # 分析建议
    advice = (
        "配对样本t检验用于比较同一组受试者在两个条件/时间点上的均值差异；\n"
        "第一：若p<0.05，说明两个测量之间存在显著差异；\n"
        "第二：Cohen's d用于衡量效应量，|d|≥0.8为大，0.5~0.8为中，0.2~0.5为小。"
    )
    sections.append(_sec_advice(advice))

    # 智能分析
    smart = (
        f"对{var1}与{var2}进行配对样本t检验。结果表明，两者差异"
        f"{'具有' if t_p < 0.05 else '不具有'}统计学意义"
        f"（t={_fmt(t_val, 2)}，df={n - 1}，{_p_expr(t_p)}），"
        f"均值差的95%CI为[{_fmt(ci_low, 3)}, {_fmt(ci_high, 3)}]，"
        f"效应量Cohen's d={_fmt(abs(cohens_d), 2)}，属于{d_level}效应。"
    )
    sections.append(_sec_smart(smart))
    sections.append(_sec_refs(_REFS_GENERAL))

    headers = ["变量", "N", "M", "SD", "t", "p"]
    rows = [
        [var1, str(n), _fmt(s1.mean()), _fmt(s1.std()), "", ""],
        [var2, str(n), _fmt(s2.mean()), _fmt(s2.std()), _fmt(t_val), _fmt(t_p)],
    ]
    return {"name": f"配对样本t检验：{var1} vs {var2}", "headers": headers, "rows": rows, "description": smart, "sections": sections}

run = paired_t_test
