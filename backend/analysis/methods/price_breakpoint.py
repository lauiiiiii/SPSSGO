# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "price_breakpoint"
METHOD_META = {'label': '价格断裂点模型',
 'category': '高级问卷分析包',
 'description': '识别价格敏感度研究中的心理接受边界与关键交点',
 'order': 180,
 'slots': [{'key': 'too_cheap',
            'label': '太便宜',
            'type': 'single',
            'accept': 'numeric',
            'hint': '放入“太便宜”价格变量'},
           {'key': 'cheap',
            'label': '便宜',
            'type': 'single',
            'accept': 'numeric',
            'hint': '放入“便宜”价格变量'},
           {'key': 'expensive',
            'label': '贵',
            'type': 'single',
            'accept': 'numeric',
            'hint': '放入“贵”价格变量'},
           {'key': 'too_expensive',
            'label': '太贵',
            'type': 'single',
            'accept': 'numeric',
            'hint': '放入“太贵”价格变量'}],
 'options': [],
 'param_builder': 'direct'}


def _curve(values, grid, le=True):
    values = pd.to_numeric(values, errors="coerce").dropna()
    if len(values) == 0:
        return np.zeros(len(grid))
    return np.array([(values <= point).mean() if le else (values >= point).mean() for point in grid])


def _cross(grid, left, right):
    idx = int(np.argmin(np.abs(left - right)))
    return float(grid[idx])


def run(df, params):
    keys = ["too_cheap", "cheap", "expensive", "too_expensive"]
    columns = [params.get(key, "") for key in keys]
    missing = [column for column in columns if column not in df.columns]
    if missing:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": f"以下变量不存在：{', '.join(missing)}。"}

    temp = df[columns].apply(pd.to_numeric, errors="coerce").dropna()
    if len(temp) < 8:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效样本不足。"}

    grid = np.linspace(float(temp.min().min()), float(temp.max().max()), 200)
    tc = _curve(temp.iloc[:, 0], grid, le=True)
    c = _curve(temp.iloc[:, 1], grid, le=True)
    e = _curve(temp.iloc[:, 2], grid, le=False)
    te = _curve(temp.iloc[:, 3], grid, le=False)
    pmc = _cross(grid, tc, e)
    pme = _cross(grid, c, te)
    opp = _cross(grid, tc, te)
    idp = _cross(grid, c, e)
    rows = [["PMC（最低可接受价格）", _fmt(pmc, 2)], ["PME（最高可接受价格）", _fmt(pme, 2)], ["OPP（最优价格点）", _fmt(opp, 2)], ["IDP（无差异价格点）", _fmt(idp, 2)]]

    sections = [
        _sec_table("关键价格交点", ["指标", "价格"], rows, description="当前实现基于 Van Westendorp 价格敏感度思想，通过经验曲线最近交点近似求解关键价格边界。"),
        _sec_table("样本与价格区间概况", ["项", "值"], [["有效样本量", str(len(temp))], ["推荐价格带", f"{_fmt(pmc, 2)} ~ {_fmt(pme, 2)}"]]),
        _sec_advice("如果问卷题型符合标准 PSM 设计，当前结果可作为价格带的快速估计。"),
        _sec_smart(f"价格断裂点分析完成，建议价格带约为 {_fmt(pmc, 2)} 到 {_fmt(pme, 2)}，其中最优价格点约为 {_fmt(opp, 2)}。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": METHOD_META["label"], "headers": ["指标", "价格"], "rows": rows, "description": f"价格断裂点分析完成，共纳入 {len(temp)} 条有效记录。", "sections": sections}
