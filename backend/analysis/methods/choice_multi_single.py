# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "choice_multi_single"
METHOD_META = {'label': '多选-单选（对比分析）',
 'category': '问卷分析包',
 'description': '比较不同单选分组在多选题上的选择偏好差异',
 'order': 56,
 'slots': [{'key': 'multiple_vars',
            'label': '多选题变量',
            'type': 'multiple',
            'accept': 'categorical',
            'min': 2,
            'hint': '放入同一题目的多选拆分变量'},
           {'key': 'single_var',
            'label': '单选分组变量',
            'type': 'single',
            'accept': 'categorical',
            'hint': '放入用于分组的单选题变量'}],
 'options': [{'key': 'count_value',
              'label': '计数值',
              'choices': ['1', '2', '0'],
              'choice_labels': {'1': '计数值，默认1'},
              'default': '1',
              'hint': '默认按照数字1作为选中项标记进行计算，可设置数字2或者数字0作为某项种类的标记。'}],
 'param_builder': 'direct'}
def run(df, params):
    single_var = params.get("single_var", "")
    multiple_vars = _resolve_cols(df, params.get("multiple_vars", []))
    count_value = params.get("count_value", "1")
    if single_var not in df.columns:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": f"单选变量 {single_var} 不存在。"}
    if len(multiple_vars) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "至少需要 2 个多选拆分变量。"}

    temp = df[[single_var] + multiple_vars].copy()
    temp = temp[temp[single_var].notna()]
    groups = [str(value) for value in temp[single_var].dropna().unique().tolist()]
    headers = ["多选项"] + groups
    rows = []
    for variable in multiple_vars:
        selected = _count_value_mask(temp[variable], count_value)
        row = [variable]
        for group in groups:
            group_mask = temp[single_var].astype(str) == group
            base = int(group_mask.sum())
            rate = selected[group_mask].sum() / base * 100 if base else 0
            row.append(f"{_fmt(rate, 1)}%")
        rows.append(row)

    sections = [
        _sec_table("分组选择率", headers, rows, description="表格展示不同单选分组下，各多选项被选择的比例。"),
        _sec_advice(f"本次按计数值 {count_value} 判定多选题选中项。如果需要进一步判断组间差异是否显著，可在当前独立模块基础上继续补充卡方检验或比例差异检验。"),
        _sec_smart(f"本次以 {single_var} 为分组变量，按计数值 {count_value} 比较了 {len(multiple_vars)} 个多选项在不同单选人群中的选择差异。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {
        "name": METHOD_META["label"],
        "headers": headers,
        "rows": rows,
        "description": f"已完成 {single_var} 与多选题之间的组合分析。",
        "sections": sections,
    }
