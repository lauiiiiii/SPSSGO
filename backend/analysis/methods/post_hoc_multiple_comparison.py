# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "post_hoc_multiple_comparison"
METHOD_META = {'label': '事后多重比较',
 'category': '差异对比分析包',
 'description': '在方差分析显著后，对组间差异进行事后多重比较',
 'order': 35,
 'slots': [{'key': 'group_var', 'label': '分组变量', 'type': 'single', 'accept': 'categorical', 'hint': '放入分组变量（3组及以上）'},
           {'key': 'test_var', 'label': '检验变量', 'type': 'single', 'accept': 'numeric', 'hint': '放入检验变量'}],
 'options': [{'key': 'method', 'label': '比较方法', 'choices': ['LSD', 'Bonferroni', 'Tukey'], 'default': 'Bonferroni'}],
 'param_builder': 'direct'}


def run(df, params):
    group_var = params.get("group_var", "")
    test_var = params.get("test_var", "")
    method = params.get("method", "Bonferroni")
    if group_var not in df.columns or test_var not in df.columns:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "分组变量或检验变量不存在。"}
    temp = df[[group_var, test_var]].copy()
    temp[test_var] = pd.to_numeric(temp[test_var], errors="coerce")
    temp = temp.dropna()
    groups = sorted(pd.Series(temp[group_var]).dropna().unique())
    if len(groups) < 3:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "事后多重比较至少需要 3 个组。"}

    group_data = {g: temp.loc[temp[group_var] == g, test_var] for g in groups}
    pair_count = len(list(combinations(groups, 2)))
    rows = []
    if method == "Tukey":
        try:
            from statsmodels.stats.multicomp import pairwise_tukeyhsd
            result = pairwise_tukeyhsd(endog=temp[test_var], groups=temp[group_var], alpha=0.05)
            for row in result.summary().data[1:]:
                g1, g2, md, p_adj, _, _, reject = row
                rows.append([str(g1), str(g2), _fmt(md, 4), _fmt(p_adj, 4), "显著" if reject else "不显著"])
        except Exception as exc:
            return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": f"Tukey 计算失败：{str(exc)}"}
    else:
        lev_stat, lev_p = levene(*[group_data[g] for g in groups], center="mean")
        equal_var = lev_p > 0.05
        for g1, g2 in combinations(groups, 2):
            t_val, p_val = ttest_ind(group_data[g1], group_data[g2], equal_var=equal_var)
            mean_diff = float(group_data[g1].mean() - group_data[g2].mean())
            if method == "Bonferroni":
                p_adj = min(float(p_val) * pair_count, 1.0)
            else:
                p_adj = float(p_val)
            rows.append([str(g1), str(g2), _fmt(mean_diff, 4), _fmt(p_adj, 4), "显著" if p_adj < 0.05 else "不显著"])

    sections = [
        _sec_table(f"事后多重比较（{method}）", ["组别I", "组别J", "均值差(I-J)", "调整后p", "结论"], rows),
        _sec_advice("事后多重比较通常在方差分析显著后使用。Bonferroni 更保守，Tukey 适合两两均衡比较。"),
        _sec_smart(f"事后多重比较完成，共比较 {len(rows)} 组。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": METHOD_META["label"], "headers": ["组别I", "组别J", "均值差(I-J)", "调整后p", "结论"], "rows": rows, "description": "事后多重比较完成。", "sections": sections}
