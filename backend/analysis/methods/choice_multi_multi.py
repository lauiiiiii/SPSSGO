# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "choice_multi_multi"
METHOD_META = {'label': '选择题【多选&多选】',
 'category': '高级问卷分析包',
 'description': '比较两组多选题之间的联合选择结构，适合研究题项组合与共现关系',
 'order': 100,
 'slots': [{'key': 'variables_a',
            'label': '多选题A',
            'type': 'multiple',
            'accept': 'categorical',
            'min': 2,
            'hint': '放入第一组多选题变量'},
           {'key': 'variables_b',
            'label': '多选题B',
            'type': 'multiple',
            'accept': 'categorical',
            'min': 2,
            'hint': '放入第二组多选题变量'}],
 'options': [],
 'param_builder': 'direct'}
def run(df, params):
    variables_a = _resolve_cols(df, params.get("variables_a", []))
    variables_b = _resolve_cols(df, params.get("variables_b", []))
    if len(variables_a) < 2 or len(variables_b) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "两组多选题变量都至少需要 2 个拆分字段。"}

    rows = []
    total = len(df)
    if total == 0:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "没有可用样本。"}

    for var_a in variables_a:
        mask_a = _selected_mask(df[var_a])
        for var_b in variables_b:
            mask_b = _selected_mask(df[var_b])
            co_count = int((mask_a & mask_b).sum())
            rate = co_count / total * 100
            rows.append([var_a, var_b, str(co_count), f"{_fmt(rate, 1)}%"])

    rows.sort(key=lambda row: float(row[3].rstrip("%")), reverse=True)
    top_rows = rows[:30]

    sections = [
        _sec_table(
            "多选题共现结果",
            ["A选项", "B选项", "共同选择人数", "共同选择率"],
            top_rows,
            description="该表展示两组多选题之间最常一起出现的选项组合，用于观察偏好搭配和联动关系。",
        ),
        _sec_advice("如果后续需要更深入判断组合强度，可在当前独立模块中继续加入 lift、Jaccard 系数或卡方检验。"),
        _sec_smart(f"本次共比较 {len(variables_a) * len(variables_b)} 组多选项配对，并按共同选择率输出了最高的组合。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {
        "name": METHOD_META["label"],
        "headers": ["A选项", "B选项", "共同选择人数", "共同选择率"],
        "rows": top_rows,
        "description": "已完成两组多选题的共现关系分析。",
        "sections": sections,
    }
