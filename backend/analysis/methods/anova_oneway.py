# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "anova_oneway"
METHOD_META = {'label': '单因素方差分析',
 'category': '差异对比分析包',
 'description': '比较三个及以上组别在某个连续变量上的均值差异',
 'slots': [{'key': 'group_var',
            'label': '分组变量',
            'type': 'single',
            'accept': 'categorical',
            'hint': '放入分组变量（须为3组及以上）'},
           {'key': 'test_vars',
            'label': '检验变量',
            'type': 'multiple',
            'accept': 'numeric',
            'min': 1,
            'hint': '放入需要检验差异的定量变量'}],
 'options': [{'key': 'post_hoc',
              'label': '事后比较',
              'choices': ['LSD', 'Bonferroni', 'Tukey'],
              'default': 'LSD'}],
 'param_builder': 'anova'}
METADATA_INJECTOR = "group_labels"


def _group_label(group_labels, value):
    text = str(value)
    if text in group_labels:
        return group_labels[text]
    try:
        numeric_text = str(int(float(value)))
        if numeric_text in group_labels:
            return group_labels[numeric_text]
    except Exception:
        pass
    return text

def anova_oneway(df, params):
    """
    单因素方差分析 + 事后检验，含 SS/MS/eta-squared

    @param df: 数据 DataFrame
    @param params: 包含 group_var, dependent 的参数字典
    @return: 含 sections 的结果字典或列表
    """
    group_var = params.get("group_var", "")
    dependent = params.get("dependent", [])
    if isinstance(dependent, str):
        dependent = [dependent]
    group_labels = params.get("group_labels", {})
    post_hoc = params.get("post_hoc", "LSD")

    if group_var not in df.columns:
        return {"name": "单因素方差分析", "headers": [], "rows": [], "description": f"分组变量 {group_var} 不存在。"}

    all_results = []
    for dep in dependent:
        if dep not in df.columns:
            continue
        temp = df[[group_var, dep]].dropna()
        temp[dep] = pd.to_numeric(temp[dep], errors="coerce")
        temp = temp.dropna()
        groups_keys = sorted(temp[group_var].unique())
        if len(groups_keys) < 3:
            continue

        groups = {g: temp[temp[group_var] == g][dep] for g in groups_keys}
        f_val, f_p = f_oneway(*[groups[g] for g in groups_keys])
        lev_stat, lev_p = levene(*[groups[g] for g in groups_keys], center="mean")

        grand_mean = temp[dep].mean()
        ss_between = sum(len(groups[g]) * (groups[g].mean() - grand_mean)**2 for g in groups_keys)
        ss_within = sum(((groups[g] - groups[g].mean())**2).sum() for g in groups_keys)
        ss_total = ss_between + ss_within
        df_between = len(groups_keys) - 1
        df_within = len(temp) - len(groups_keys)
        ms_between = ss_between / df_between if df_between > 0 else 0
        ms_within = ss_within / df_within if df_within > 0 else 0
        eta_sq = ss_between / ss_total if ss_total > 0 else 0

        sections = []

        # 表 1：分组描述统计
        g_headers = ["组别", "N", "均值", "标准差", "最小值", "最大值"]
        g_rows = []
        for g in groups_keys:
            grp = groups[g]
            label = _group_label(group_labels, g)
            g_rows.append([label, str(len(grp)), _fmt(grp.mean()), _fmt(grp.std()), _fmt(grp.min()), _fmt(grp.max())])
        sections.append(_sec_table("分组描述统计", g_headers, g_rows))

        sections.append(_sec_table(
            "方差齐性检验",
            ["检验", "统计量", "p", "结论"],
            [["Levene", _fmt(lev_stat, 3), _fmt(lev_p, 4), "方差齐" if lev_p > 0.05 else "方差不齐"]],
            description="Levene 检验采用均值中心口径，与 SPSS 单因素方差分析常见输出口径保持一致。"
        ))

        # 表 2：方差分析表
        anova_headers = ["变异来源", "SS", "df", "MS", "F", "p", "η²"]
        anova_rows = [
            ["组间", _fmt(ss_between, 2), str(df_between), _fmt(ms_between, 2), _fmt(f_val, 2), _fmt(f_p), _fmt(eta_sq, 3)],
            ["组内", _fmt(ss_within, 2), str(df_within), _fmt(ms_within, 2), "", "", ""],
            ["总计", _fmt(ss_total, 2), str(df_between + df_within), "", "", "", ""],
        ]
        eta_level = "大" if eta_sq >= 0.14 else ("中等" if eta_sq >= 0.06 else "小")
        sections.append(_sec_table("方差分析表", anova_headers, anova_rows,
                                   description=f"η²={_fmt(eta_sq, 3)}，效应量{eta_level}。"))

        # 兼容旧格式主表
        headers = ["组别", "N", "M", "SD", "F", "p"]
        rows = []
        for i, g in enumerate(groups_keys):
            grp = groups[g]
            label = _group_label(group_labels, g)
            row = [label, str(len(grp)), _fmt(grp.mean()), _fmt(grp.std()), "", ""]
            if i == 0:
                row[4] = _fmt(f_val)
                row[5] = _fmt(f_p)
            rows.append(row)

        smart = ""
        name = f"单因素方差分析：{dep}在{group_var}上的差异"

        if f_p < 0.05:
            smart = (
                f"以{group_var}为自变量、{dep}为因变量进行单因素方差分析。"
                f"结果表明，不同{group_var}的{dep}得分差异具有统计学意义"
                f"（F={_fmt(f_val, 2)}，{_p_expr(f_p)}，η²={_fmt(eta_sq, 3)}）。"
            )
            ph_results = []
            try:
                from statsmodels.stats.multicomp import pairwise_tukeyhsd
            except Exception:
                pairwise_tukeyhsd = None

            if post_hoc == "Tukey" and pairwise_tukeyhsd is not None:
                mc = pairwise_tukeyhsd(endog=temp[dep], groups=temp[group_var], alpha=0.05)
                for row in mc.summary().data[1:]:
                    g1, g2, md, p_adj, _, _, reject = row
                    ph_results.append((g1, g2, float(md), float(p_adj), bool(reject)))
            else:
                pair_count = len(list(combinations(groups_keys, 2)))
                for (g1, g2) in combinations(groups_keys, 2):
                    t_ph, p_ph = ttest_ind(groups[g1], groups[g2], equal_var=(lev_p > 0.05))
                    md = groups[g1].mean() - groups[g2].mean()
                    if post_hoc == "Bonferroni":
                        p_adj = min(float(p_ph) * pair_count, 1.0)
                    else:
                        p_adj = float(p_ph)
                    ph_results.append((g1, g2, md, p_adj, p_adj < 0.05))

            ph_headers = ["比较组(I)", "比较组(J)", "均值差(I-J)", "p"]
            ph_rows = []
            for g1, g2, md, p_ph, _ in ph_results:
                l1 = _group_label(group_labels, g1)
                l2 = _group_label(group_labels, g2)
                ph_rows.append([l1, l2, _fmt(md) + _sig(p_ph), _fmt(p_ph)])
            sections.append(_sec_table(f"事后多重比较（{post_hoc}）", ph_headers, ph_rows,
                                       description="LSD 使用未校正两两比较；Bonferroni 使用 Bonferroni 校正；Tukey 使用 Tukey HSD，尽量贴近 SPSS 常见口径。"))

            sig_pairs = [(g1, g2, md, p_ph) for g1, g2, md, p_ph, reject in ph_results if reject]
            if sig_pairs:
                from collections import defaultdict
                wins = defaultdict(list)
                for g1, g2, md, p_ph in sig_pairs:
                    l1 = _group_label(group_labels, g1)
                    l2 = _group_label(group_labels, g2)
                    if md > 0:
                        wins[l1].append(l2)
                    else:
                        wins[l2].append(l1)
                group_means = {_group_label(group_labels, g): groups[g].mean() for g in groups}
                sorted_g = sorted(wins.keys(), key=lambda x: group_means.get(x, 0), reverse=True)
                parts = [f"{g}显著高于{'、'.join(wins[g])}" for g in sorted_g if wins[g]]
                smart += f"事后多重比较（{post_hoc}）表明，{'，'.join(parts)}。"
        else:
            smart = (
                f"以{group_var}为自变量、{dep}为因变量进行单因素方差分析。"
                f"结果表明，不同{group_var}的{dep}得分差异不具有统计学意义"
                f"（F={_fmt(f_val, 2)}，{_p_expr(f_p)}）。"
            )

        # 分析建议
        advice = (
            "单因素方差分析用于比较3组及以上在某连续变量上的均值差异；\n"
            "第一：若F检验p<0.05，说明组间差异显著，需进一步做事后多重比较判断具体哪些组之间存在差异；\n"
            "第二：η²衡量效应量大小，≥0.14为大，0.06~0.14为中，<0.06为小；\n"
            "第三：事后比较中p<0.05的组对存在显著差异。"
        )
        sections.append(_sec_advice(advice))
        sections.append(_sec_smart(smart))
        sections.append(_sec_refs(_REFS_GENERAL))

        all_results.append({"name": name, "headers": headers, "rows": rows, "description": smart, "sections": sections})

    if not all_results:
        return {"name": "单因素方差分析", "headers": [], "rows": [], "description": "未找到有效变量。"}
    return all_results if len(all_results) > 1 else all_results[0]

run = anova_oneway
