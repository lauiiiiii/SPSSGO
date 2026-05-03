# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "coupling_coordination"
METHOD_META = {'label': '耦合协调度',
 'category': '综合评价',
 'description': '衡量多个子系统之间的耦合关系与协调发展水平',
 'order': 70,
 'slots': [{'key': 'group1_vars', 'label': '子系统1指标', 'type': 'multiple', 'accept': 'numeric', 'min': 1, 'hint': '放入子系统1指标'},
           {'key': 'group2_vars', 'label': '子系统2指标', 'type': 'multiple', 'accept': 'numeric', 'min': 1, 'hint': '放入子系统2指标'},
           {'key': 'group3_vars', 'label': '子系统3指标', 'type': 'multiple', 'accept': 'numeric', 'min': 0, 'hint': '可选：放入子系统3指标'}],
 'options': [],
 'param_builder': 'direct'}


def run(df, params):
    groups = []
    for key in ["group1_vars", "group2_vars", "group3_vars"]:
        cols = _resolve_cols(df, params.get(key, []))
        if cols:
            groups.append(cols)
    if len(groups) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "耦合协调度至少需要 2 个子系统。"}
    all_vars = list(dict.fromkeys([col for group in groups for col in group]))
    data = df[all_vars].apply(pd.to_numeric, errors="coerce").dropna()
    if len(data) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效样本不足。"}

    normalized = _normalize_benefit_frame(data)
    subsystem_scores = []
    for group in groups:
        subsystem_scores.append(normalized[group].mean(axis=1))
    subsystem_df = pd.concat(subsystem_scores, axis=1)
    subsystem_df.columns = [f"U{i+1}" for i in range(len(groups))]
    k = len(groups)
    product = subsystem_df.prod(axis=1)
    mean_u = subsystem_df.mean(axis=1)
    coupling = (product / (mean_u ** k + 1e-12)) ** (1 / k)
    coordination = np.sqrt(coupling * mean_u)
    rows = [[str(idx), _fmt(mean_u.loc[idx], 4), _fmt(coupling.loc[idx], 4), _fmt(coordination.loc[idx], 4)] for idx in coordination.sort_values(ascending=False).head(10).index]
    sections = [
        _sec_table("耦合协调度 Top10", ["样本索引", "综合发展指数T", "耦合度C", "协调度D"], rows),
        _sec_advice("协调度 D 越高，说明多个子系统之间发展越协调。"),
        _sec_smart(f"耦合协调度计算完成，当前协调度最高的样本索引为 {rows[0][0]}。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": METHOD_META["label"], "headers": ["样本索引", "综合发展指数T", "耦合度C", "协调度D"], "rows": rows, "description": f"耦合协调度完成，共评估 {len(coordination)} 个样本。", "sections": sections}
