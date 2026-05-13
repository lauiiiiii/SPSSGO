# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "choice_single_multi"
METHOD_META = {'label': '单选-多选（对比分析）',
 'category': '问卷分析包',
 'description': '从单选结果出发，分析不同单选人群在多选题上的偏好扩展',
 'order': 57,
 'slots': [{'key': 'single_var',
            'label': '单选变量',
            'type': 'single',
            'accept': 'categorical',
            'hint': '放入单选题变量'},
           {'key': 'multiple_vars',
            'label': '多选题变量',
            'type': 'multiple',
            'accept': 'categorical',
            'min': 2,
            'hint': '放入同一题目的多选拆分变量'}],
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
    headers = ["单选结果"] + multiple_vars
    rows = []
    for group in groups:
        group_mask = temp[single_var].astype(str) == group
        base = int(group_mask.sum())
        row = [group]
        for variable in multiple_vars:
            rate = _count_value_mask(temp.loc[group_mask, variable], count_value).mean() * 100 if base else 0
            row.append(f"{_fmt(rate, 1)}%")
        rows.append(row)

    sections = [
        _sec_table("单选结果下的多选偏好", headers, rows, description="表格展示不同单选结果对应人群在各多选项上的选择比例。"),
        _sec_advice(f"本次按计数值 {count_value} 判定多选题选中项。该方法适合从单选结果出发看偏好扩展。若需要显著性判断，可继续在当前模块中加入比例差异或卡方检验。"),
        _sec_smart(f"本次围绕单选变量 {single_var} 展开分析，按计数值 {count_value} 比较了 {len(groups)} 个单选结果对应的人群偏好。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {
        "name": METHOD_META["label"],
        "headers": headers,
        "rows": rows,
        "description": f"已完成 {single_var} 对应人群的多选偏好分析。",
        "sections": sections,
    }
