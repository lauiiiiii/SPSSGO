# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "category_summary"
METHOD_META = {'label': '分类汇总',
 'category': '数据概览',
 'description': '按分类变量分组汇总一个或多个定量变量的样本量、均值和极值',
 'order': 40,
 'slots': [{'key': 'group_var',
            'label': '分类变量',
            'type': 'single',
            'accept': 'categorical',
            'hint': '放入用于分组汇总的分类变量'},
           {'key': 'summary_vars',
            'label': '汇总变量',
            'type': 'multiple',
            'accept': 'numeric',
            'min': 1,
            'hint': '放入需要按组汇总的定量变量'}],
 'options': [],
 'param_builder': 'direct'}
METADATA_INJECTOR = "group_labels"

def category_summary(df, params):
    """
    分类汇总：按分类变量对定量变量做分组描述统计

    @param df: 数据 DataFrame
    @param params: 包含 group_var, summary_vars, group_labels 的参数字典
    @return: 含 sections 的结果字典
    """
    group_var = params.get("group_var", "")
    summary_vars = _resolve_cols(df, params.get("summary_vars", []))
    group_labels = params.get("group_labels", {})
    if group_var not in df.columns:
        return {"name": "分类汇总", "headers": [], "rows": [], "description": "分组变量不存在。"}
    if not summary_vars:
        return {"name": "分类汇总", "headers": [], "rows": [], "description": "未指定需要汇总的定量变量。"}

    headers = ["汇总变量", "类别", "样本量", "均值", "标准差", "最小值", "最大值"]
    rows = []
    smart_parts = []

    for summary_var in summary_vars:
        temp = df[[group_var, summary_var]].copy()
        temp[summary_var] = pd.to_numeric(temp[summary_var], errors="coerce")
        temp = temp.dropna(subset=[group_var, summary_var])
        if temp.empty:
            continue

        grouped = temp.groupby(group_var)[summary_var]
        means = []
        for group_value, series in grouped:
            label = group_labels.get(str(group_value), str(group_value))
            rows.append([
                summary_var,
                label,
                str(int(series.shape[0])),
                _fmt(series.mean()),
                _fmt(series.std()),
                _fmt(series.min()),
                _fmt(series.max()),
            ])
            means.append((label, float(series.mean())))

        if means:
            max_group = max(means, key=lambda item: item[1])
            min_group = min(means, key=lambda item: item[1])
            smart_parts.append(
                f"在{summary_var}上，{max_group[0]}的均值最高（{_fmt(max_group[1])}），"
                f"{min_group[0]}的均值最低（{_fmt(min_group[1])}）"
            )

    if not rows:
        return {"name": "分类汇总", "headers": [], "rows": [], "description": "没有可用于分类汇总的有效数据。"}

    sections = []
    sections.append(_sec_table("分类汇总结果", headers, rows, description="按分类变量分组展示各定量变量的样本量、均值与离散程度。"))

    advice = (
        "分类汇总适合先观察不同类别下的指标分布情况；\n"
        "第一：可先比较各类别样本量是否均衡；\n"
        "第二：再比较均值、标准差和极值，快速识别组间差异方向；\n"
        "第三：若需要进一步判断显著性，可继续使用t检验、方差分析等方法。"
    )
    sections.append(_sec_advice(advice))

    smart = "；".join(smart_parts) + "。" if smart_parts else "分类汇总结果如表所示。"
    sections.append(_sec_smart(smart))
    sections.append(_sec_refs(_REFS_GENERAL))

    return {"name": f"分类汇总：按{group_var}分组", "headers": headers, "rows": rows, "description": smart, "sections": sections}

run = category_summary
