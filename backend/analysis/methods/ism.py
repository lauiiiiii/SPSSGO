# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "ism"
METHOD_META = {'label': '解释结构模型（ISM）',
 'category': '综合评价',
 'description': '基于变量间关系构建多层级的解释结构',
 'order': 140,
 'slots': [{'key': 'variables', 'label': '结构变量', 'type': 'multiple', 'accept': 'numeric', 'min': 3, 'hint': '放入需要构建结构层级的变量'}],
 'options': [{'key': 'threshold', 'label': '关系阈值', 'choices': ['0.3', '0.4', '0.5'], 'default': '0.3'}],
 'param_builder': 'direct'}


def run(df, params):
    variables = _resolve_cols(df, params.get("variables", []))
    if len(variables) < 3:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "ISM 至少需要 3 个变量。"}
    data = df[variables].apply(pd.to_numeric, errors="coerce").dropna()
    if len(data) < 4:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效样本不足。"}

    threshold = float(params.get("threshold", 0.3) or 0.3)
    corr = data.corr().abs().fillna(0.0)
    adjacency = (corr >= threshold).astype(int).copy()
    adjacency_values = adjacency.to_numpy(copy=True)
    np.fill_diagonal(adjacency_values, 1)
    reachability = adjacency_values.copy()
    n = len(variables)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                reachability[i, j] = int(reachability[i, j] or (reachability[i, k] and reachability[k, j]))

    remaining = list(range(n))
    levels = []
    while remaining:
        current = []
        for idx in remaining:
            reach_set = {j for j in remaining if reachability[idx, j] == 1}
            antecedent_set = {j for j in remaining if reachability[j, idx] == 1}
            if reach_set.issubset(antecedent_set):
                current.append(idx)
        if not current:
            current = [remaining[0]]
        levels.append(current)
        remaining = [idx for idx in remaining if idx not in current]

    rows = []
    for level_no, level_items in enumerate(levels, start=1):
        for idx in level_items:
            rows.append([f"第{level_no}层", variables[idx]])
    sections = [
        _sec_table("ISM 层级结果", ["层级", "变量"], rows),
        _sec_advice("当前 ISM 根据相关阈值构造可达矩阵，适合做结构层级的初步探索。"),
        _sec_smart(f"ISM 分析完成，共识别 {len(levels)} 个层级。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": METHOD_META["label"], "headers": ["层级", "变量"], "rows": rows, "description": f"ISM 分析完成，共识别 {len(levels)} 个层级。", "sections": sections}
