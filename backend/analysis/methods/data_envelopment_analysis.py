# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "data_envelopment_analysis"
METHOD_META = {'label': '数据包络分析',
 'category': '综合评价',
 'description': '使用 CCR 模型近似计算各决策单元的相对效率',
 'order': 40,
 'slots': [{'key': 'input_vars', 'label': '投入指标', 'type': 'multiple', 'accept': 'numeric', 'min': 1, 'hint': '放入投入指标'},
           {'key': 'output_vars', 'label': '产出指标', 'type': 'multiple', 'accept': 'numeric', 'min': 1, 'hint': '放入产出指标'}],
 'options': [],
 'param_builder': 'direct'}


def run(df, params):
    input_vars = _resolve_cols(df, params.get("input_vars", []))
    output_vars = _resolve_cols(df, params.get("output_vars", []))
    if not input_vars or not output_vars:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "DEA 至少需要 1 个投入指标和 1 个产出指标。"}
    data = df[input_vars + output_vars].apply(pd.to_numeric, errors="coerce").dropna()
    if len(data) < 3:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效样本不足。"}

    X = data[input_vars].to_numpy(dtype=float)
    Y = data[output_vars].to_numpy(dtype=float)
    eps = 1e-6
    rows = []
    for idx in range(len(data)):
        x0 = X[idx]
        y0 = Y[idx]
        c = np.concatenate([np.zeros(len(input_vars)), -y0])
        A_eq = np.concatenate([x0, np.zeros(len(output_vars))]).reshape(1, -1)
        b_eq = np.array([1.0])
        A_ub = []
        b_ub = []
        for j in range(len(data)):
            A_ub.append(np.concatenate([-X[j], Y[j]]))
            b_ub.append(0.0)
        bounds = [(eps, None)] * (len(input_vars) + len(output_vars))
        result = linprog(c=c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
        efficiency = -result.fun if result.success else np.nan
        rows.append([str(data.index[idx]), _fmt(efficiency, 4), "有效" if pd.notna(efficiency) and efficiency >= 0.999 else "无效"])
    rows.sort(key=lambda item: float(item[1]) if item[1] != "—" else -1, reverse=True)
    sections = [
        _sec_table("DEA 效率结果", ["样本索引", "CCR效率值", "是否有效"], rows),
        _sec_advice("当前 DEA 使用投入导向 CCR 近似模型，效率值越接近 1，说明相对效率越高。"),
        _sec_smart(f"数据包络分析完成，当前效率最高的决策单元为 {rows[0][0]}。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": METHOD_META["label"], "headers": ["样本索引", "CCR效率值", "是否有效"], "rows": rows, "description": f"DEA 完成，共评估 {len(rows)} 个决策单元。", "sections": sections}
