# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "independent_t_test"
METHOD_META = {'label': '独立样本T检验',
 'category': '差异对比分析包',
 'description': '比较两个独立组别在某个连续变量上的均值差异',
 'slots': [{'key': 'group_var',
            'label': '分组变量',
            'type': 'single',
            'accept': 'categorical',
            'hint': '放入分组变量（如性别，须为2组）'},
           {'key': 'test_vars',
            'label': '检验变量',
            'type': 'multiple',
            'accept': 'numeric',
            'min': 1,
            'hint': '放入需要检验差异的定量变量'}],
 'options': [],
 'param_builder': 't_test'}
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

def independent_t_test(df, params):
    """
    独立样本 t 检验，含 Levene 方差齐性检验、Cohen's d 效应量

    @param df: 数据 DataFrame
    @param params: 包含 group_var, dependent 的参数字典
    @return: 含 sections 的结果字典或列表
    """
    group_var = params.get("group_var", "")
    dependent = params.get("dependent", [])
    if isinstance(dependent, str):
        dependent = [dependent]
    group_labels = params.get("group_labels", {})

    if group_var not in df.columns:
        return {"name": "独立样本t检验", "headers": [], "rows": [], "description": f"分组变量 {group_var} 不存在。"}

    all_results = []
    for dep in dependent:
        if dep not in df.columns:
            continue
        temp = df[[group_var, dep]].dropna()
        temp[dep] = pd.to_numeric(temp[dep], errors="coerce")
        temp = temp.dropna()
        groups = sorted(temp[group_var].unique())
        if len(groups) != 2:
            continue

        g1_label = _group_label(group_labels, groups[0])
        g2_label = _group_label(group_labels, groups[1])
        g1_data = temp[temp[group_var] == groups[0]][dep]
        g2_data = temp[temp[group_var] == groups[1]][dep]

        lev_stat, lev_p = levene(g1_data, g2_data, center="mean")
        equal_var = lev_p > 0.05
        t_val, t_p = ttest_ind(g1_data, g2_data, equal_var=equal_var)

        # Cohen's d
        n1, n2 = len(g1_data), len(g2_data)
        pooled_std = np.sqrt(((n1 - 1) * g1_data.std()**2 + (n2 - 1) * g2_data.std()**2) / (n1 + n2 - 2))
        cohens_d = (g1_data.mean() - g2_data.mean()) / pooled_std if pooled_std > 0 else 0
        if equal_var:
            df_val = n1 + n2 - 2
        else:
            s1_sq = g1_data.var(ddof=1)
            s2_sq = g2_data.var(ddof=1)
            numerator = (s1_sq / n1 + s2_sq / n2) ** 2
            denominator = ((s1_sq / n1) ** 2) / (n1 - 1) + ((s2_sq / n2) ** 2) / (n2 - 1)
            df_val = numerator / denominator if denominator > 0 else n1 + n2 - 2

        sections = []

        # 表 1：分组描述统计
        desc_headers = ["组别", "N", "均值", "标准差"]
        desc_rows = [
            [g1_label, str(n1), _fmt(g1_data.mean()), _fmt(g1_data.std())],
            [g2_label, str(n2), _fmt(g2_data.mean()), _fmt(g2_data.std())],
        ]
        sections.append(_sec_table("分组描述统计", desc_headers, desc_rows))

        # 表 2：Levene 方差齐性检验
        lev_headers = ["检验", "F", "p", "结论"]
        lev_conclusion = "方差齐" if equal_var else "方差不齐"
        lev_rows = [["Levene检验", _fmt(lev_stat, 2), _fmt(lev_p), lev_conclusion]]
        sections.append(_sec_table("Levene方差齐性检验", lev_headers, lev_rows,
                                   description="Levene 检验采用均值中心口径，与 SPSS 独立样本 t 检验常用输出保持一致。p>0.05 说明可按等方差假定解释，否则优先参考不等方差结果。"))

        # 表 3：t 检验结果（SPSS 风格保留两行）
        t_headers = ["方差假定", "t", "df", "p", "均值差", "Cohen's d", "推荐解读"]
        mean_diff = g1_data.mean() - g2_data.mean()
        t_equal, p_equal = ttest_ind(g1_data, g2_data, equal_var=True)
        s1_sq = g1_data.var(ddof=1)
        s2_sq = g2_data.var(ddof=1)
        welch_num = (s1_sq / n1 + s2_sq / n2) ** 2
        welch_den = ((s1_sq / n1) ** 2) / (n1 - 1) + ((s2_sq / n2) ** 2) / (n2 - 1)
        welch_df = welch_num / welch_den if welch_den > 0 else n1 + n2 - 2
        t_welch, p_welch = ttest_ind(g1_data, g2_data, equal_var=False)
        t_rows = [
            ["等方差假定", _fmt(t_equal, 3), _fmt(n1 + n2 - 2, 3), _fmt(p_equal, 4), _fmt(mean_diff, 4), _fmt(abs(cohens_d), 3), "是" if equal_var else "否"],
            ["不等方差假定", _fmt(t_welch, 3), _fmt(welch_df, 3), _fmt(p_welch, 4), _fmt(mean_diff, 4), _fmt(abs(cohens_d), 3), "否" if equal_var else "是"],
        ]
        d_level = "大" if abs(cohens_d) >= 0.8 else ("中等" if abs(cohens_d) >= 0.5 else "小")
        sections.append(_sec_table("独立样本t检验", t_headers, t_rows,
                                   description=f"为贴近 SPSS 输出，这里同时给出“等方差假定”和“不等方差假定”两行结果。当前推荐解读行为“{'等方差假定' if equal_var else '不等方差假定'}”。Cohen's d={_fmt(abs(cohens_d), 2)}，效应量{d_level}。"))

        # 分析建议
        advice = (
            "独立样本t检验用于比较两组独立样本在某连续变量上的均值差异；\n"
            "第一：首先查看Levene方差齐性检验，若p>0.05则方差齐性假设成立，采用标准t检验；否则采用Welch校正；\n"
            "第二：若t检验p<0.05，说明两组差异具有统计学意义；\n"
            "第三：Cohen's d用于衡量效应量大小，|d|≥0.8为大效应，0.5~0.8为中效应，0.2~0.5为小效应。"
        )
        sections.append(_sec_advice(advice))

        # 智能分析
        if t_p < 0.05:
            higher = g1_label if g1_data.mean() > g2_data.mean() else g2_label
            lower = g2_label if higher == g1_label else g1_label
            smart = (
                f"以{group_var}为分组变量，以{dep}为检验变量进行独立样本t检验。"
                f"结果表明，不同{group_var}的{dep}得分差异具有统计学意义"
                f"（t={_fmt(t_val, 2)}，df={_fmt(df_val, 3)}，{_p_expr(t_p)}）。"
                f"{higher}的{dep}水平显著高于{lower}，"
                f"效应量Cohen's d={_fmt(abs(cohens_d), 2)}，属于{d_level}效应。"
            )
        else:
            smart = (
                f"以{group_var}为分组变量，以{dep}为检验变量进行独立样本t检验。"
                f"结果表明，不同{group_var}的{dep}得分差异不具有统计学意义"
                f"（t={_fmt(t_val, 2)}，df={_fmt(df_val, 3)}，{_p_expr(t_p)}）。"
            )
        sections.append(_sec_smart(smart))
        sections.append(_sec_refs(_REFS_GENERAL))

        # 兼容旧格式
        headers = ["组别", "N", "M", "SD", "t", "p"]
        rows = [
            [g1_label, str(n1), _fmt(g1_data.mean()), _fmt(g1_data.std()), "", ""],
            [g2_label, str(n2), _fmt(g2_data.mean()), _fmt(g2_data.std()), _fmt(t_val), _fmt(t_p)],
        ]
        name = f"独立样本t检验：{dep}在{group_var}上的差异"
        all_results.append({"name": name, "headers": headers, "rows": rows, "description": smart, "sections": sections})

    if not all_results:
        return {"name": "独立样本t检验", "headers": [], "rows": [], "description": "未找到有效的分组或因变量。"}
    if len(all_results) == 1:
        return all_results[0]
    return all_results

run = independent_t_test
