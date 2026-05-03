# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "correspondence_analysis"
METHOD_META = {'label': '对应分析',
 'category': '问卷分析包',
 'description': '对两个分类变量的列联表进行降维，观察类别之间的接近关系',
 'order': 70,
 'slots': [{'key': 'var1',
            'label': '行变量',
            'type': 'single',
            'accept': 'categorical',
            'hint': '放入第一个分类变量'},
           {'key': 'var2',
            'label': '列变量',
            'type': 'single',
            'accept': 'categorical',
            'hint': '放入第二个分类变量'}],
 'options': [],
 'param_builder': 'direct'}
METADATA_INJECTOR = "cross_labels"

def correspondence_analysis(df, params):
    """
    对应分析：对二维列联表做坐标降维
    """
    var1 = params.get("var1", "")
    var2 = params.get("var2", "")
    var1_labels = params.get("var1_labels", {})
    var2_labels = params.get("var2_labels", {})
    if var1 not in df.columns or var2 not in df.columns:
        return {"name": "对应分析", "headers": [], "rows": [], "description": "变量不存在。"}

    ct = pd.crosstab(df[var1], df[var2])
    if ct.shape[0] < 2 or ct.shape[1] < 2:
        return {"name": "对应分析", "headers": [], "rows": [], "description": "对应分析至少需要2×2的列联表。"}

    P = ct / ct.values.sum()
    r = P.sum(axis=1).values.reshape(-1, 1)
    c = P.sum(axis=0).values.reshape(1, -1)
    expected = r @ c
    S = (P.values - expected) / np.sqrt(expected)
    U, singular_values, VT = np.linalg.svd(S, full_matrices=False)
    dim_count = min(2, len(singular_values))
    inertia = singular_values ** 2

    row_coords = U[:, :dim_count] * singular_values[:dim_count]
    col_coords = VT.T[:, :dim_count] * singular_values[:dim_count]

    row_headers = ["行类别", "维度1", "维度2"]
    row_rows = []
    for idx, coord in zip(ct.index, row_coords):
        row_rows.append([
            var1_labels.get(str(idx), str(idx)),
            _fmt(coord[0], 4),
            _fmt(coord[1], 4) if dim_count > 1 else "—",
        ])

    col_headers = ["列类别", "维度1", "维度2"]
    col_rows = []
    for idx, coord in zip(ct.columns, col_coords):
        col_rows.append([
            var2_labels.get(str(idx), str(idx)),
            _fmt(coord[0], 4),
            _fmt(coord[1], 4) if dim_count > 1 else "—",
        ])

    inertia_headers = ["维度", "特征值", "惯量占比(%)", "累计占比(%)"]
    inertia_rows = []
    cum = 0.0
    for i in range(dim_count):
        pct = inertia[i] / inertia.sum() * 100 if inertia.sum() > 0 else 0
        cum += pct
        inertia_rows.append([f"维度{i+1}", _fmt(inertia[i], 4), _fmt(pct, 2), _fmt(cum, 2)])

    sections = []
    sections.append(_sec_table("维度解释表", inertia_headers, inertia_rows, description="展示对应分析前两个维度对总惯量的解释比例。"))
    sections.append(_sec_table("行类别坐标", row_headers, row_rows))
    sections.append(_sec_table("列类别坐标", col_headers, col_rows))
    smart = (
        f"对{var1}与{var2}进行对应分析。"
        f"前两个维度累计解释惯量为{_fmt(cum, 2)}%，可用于观察类别之间的接近关系。"
    )
    sections.append(_sec_smart(smart))
    sections.append(_sec_refs(_REFS_GENERAL))
    return {"name": f"对应分析：{var1} × {var2}", "headers": inertia_headers, "rows": inertia_rows, "description": smart, "sections": sections}

run = correspondence_analysis
