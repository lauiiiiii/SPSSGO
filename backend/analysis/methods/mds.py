# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "mds"
METHOD_META = {'label': '多维尺度分析',
 'category': '数据检验',
 'description': '基于变量间距离关系建立二维空间坐标，用于观察接近结构',
 'slots': [{'key': 'variables',
            'label': '分析变量',
            'type': 'multiple',
            'accept': 'numeric',
            'min': 2,
            'hint': '放入需要比较结构接近性的变量'}],
 'options': [],
 'param_builder': 'direct'}

def multidimensional_scaling_analysis(df, params):
    """
    多维尺度分析：根据变量间相关关系映射二维坐标
    """
    variables = _resolve_cols(df, params.get("variables", []))
    if len(variables) < 2:
        return {"name": "多维尺度分析", "headers": [], "rows": [], "description": "至少需要2个变量。"}

    data = df[variables].apply(pd.to_numeric, errors="coerce").dropna()
    if len(data) < 2:
        return {"name": "多维尺度分析", "headers": [], "rows": [], "description": "有效样本不足。"}

    corr = data.corr().fillna(0)
    diss = 1 - corr.abs()
    model = MDS(n_components=2, dissimilarity="precomputed", random_state=42, normalized_stress="auto")
    coords = model.fit_transform(diss.values)

    headers = ["变量", "维度1", "维度2"]
    rows = []
    for i, var in enumerate(variables):
        rows.append([var, _fmt(coords[i, 0], 4), _fmt(coords[i, 1], 4)])

    stress_headers = ["指标", "值"]
    stress_rows = [["Stress", _fmt(getattr(model, "stress_", None), 4)], ["变量数", str(len(variables))]]

    sections = []
    sections.append(_sec_table("MDS坐标表", headers, rows, description="坐标越接近的变量，表示其相关结构越相似。"))
    sections.append(_sec_table("模型摘要", stress_headers, stress_rows))
    smart = f"对{len(variables)}个变量进行了多维尺度分析，结果可用于观察变量在二维空间中的相对接近关系。"
    sections.append(_sec_smart(smart))
    sections.append(_sec_refs(_REFS_GENERAL))
    return {"name": "多维尺度分析", "headers": headers, "rows": rows, "description": smart, "sections": sections}

run = multidimensional_scaling_analysis
