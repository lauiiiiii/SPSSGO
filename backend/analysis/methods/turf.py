# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "turf"
METHOD_META = {'label': 'TURF分析',
 'category': '高级问卷分析包',
 'description': '寻找在给定数量约束下覆盖最多受众的最优选项组合',
 'order': 190,
 'slots': [{'key': 'variables',
            'label': '覆盖项变量',
            'type': 'multiple',
            'accept': 'categorical',
            'min': 2,
            'hint': '放入 0/1 覆盖变量'}],
 'options': [{'key': 'combo_size', 'label': '组合大小', 'choices': ['2', '3', '4'], 'default': '3'}],
 'param_builder': 'direct'}
def run(df, params):
    variables = _resolve_cols(df, params.get("variables", []))
    if len(variables) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "至少需要 2 个覆盖项变量。"}

    combo_size = int(params.get("combo_size", 3) or 3)
    combo_size = max(1, min(combo_size, len(variables)))
    binary = pd.DataFrame({variable: _selected_mask(df[variable]) for variable in variables})
    if len(binary) == 0:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "没有可用样本。"}

    base_rows = []
    for variable in variables:
        count = int(binary[variable].sum())
        base_rows.append([variable, str(count), f"{_fmt(count / len(binary) * 100, 1)}%"])

    combo_rows = []
    for combo in combinations(variables, combo_size):
        covered = binary[list(combo)].any(axis=1)
        count = int(covered.sum())
        combo_rows.append([", ".join(combo), str(count), f"{_fmt(count / len(binary) * 100, 1)}%"])

    combo_rows.sort(key=lambda row: float(row[2].rstrip("%")), reverse=True)
    top_combo_rows = combo_rows[:10]

    sections = [
        _sec_table("单项覆盖率", ["覆盖项", "覆盖人数", "覆盖率"], base_rows),
        _sec_table(
            f"组合大小 = {combo_size} 的最佳覆盖组合",
            ["组合", "覆盖人数", "覆盖率"],
            top_combo_rows,
            description="TURF 的核心是找到在给定资源限制下覆盖最多样本的组合，而不是单看某一个项目自身热度。",
        ),
    ]
    if top_combo_rows:
        sections.append(
            _sec_smart(
                f"当前最佳组合为 {top_combo_rows[0][0]}，可覆盖 {top_combo_rows[0][2]} 的样本。"
            )
        )
    sections.append(
        _sec_advice(
            "第一：TURF 变量最好是 0/1 覆盖结构或可明确识别是否被选择；\n"
            "第二：如果组合数很大，建议先筛选核心候选项，再做 TURF 组合搜索。"
        )
    )
    sections.append(_sec_refs(_REFS_GENERAL))

    return {
        "name": METHOD_META["label"],
        "headers": ["组合", "覆盖人数", "覆盖率"],
        "rows": top_combo_rows,
        "description": f"TURF 分析完成，已比较组合大小为 {combo_size} 的候选组合。",
        "sections": sections,
    }
