# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "descriptive"
METHOD_META = {'label': '描述性统计',
 'category': '数据概览',
 'description': '计算各变量的均值、标准差、最小值、最大值等描述性指标',
 'order': 30,
 'slots': [{'key': 'variables',
            'label': '分析变量',
            'type': 'multiple',
            'accept': 'numeric',
            'min': 1,
            'hint': '放入需要描述的定量变量'}],
 'options': [],
 'param_builder': 'direct'}

def descriptive(df, params):
    """
    描述统计分析，输出含中位数、偏度、峰度的丰富报告

    @param df: 数据 DataFrame
    @param params: 包含 variables 的参数字典
    @return: 含 sections 的结果字典
    """
    variables = _resolve_cols(df, params.get("variables", []))
    if not variables:
        return {"name": "描述性统计", "headers": [], "rows": [], "description": "未找到指定变量。"}

    headers = ["变量", "N", "均值", "标准差", "最小值", "最大值", "中位数", "偏度", "峰度"]
    rows = []
    descs = []
    for v in variables:
        s = pd.to_numeric(df[v], errors="coerce").dropna()
        rows.append([
            v, str(len(s)), _fmt(s.mean()), _fmt(s.std()),
            _fmt(s.min()), _fmt(s.max()), _fmt(s.median()),
            _fmt(s.skew()), _fmt(s.kurtosis()),
        ])
        descs.append(f"{v}的均值为{_fmt(s.mean())}（SD={_fmt(s.std())}）")

    sections = []
    desc_text = (
        "上表展示了各变量的描述性统计结果。"
        "均值和标准差反映了数据的集中趋势和离散程度；"
        "偏度和峰度用于判断数据分布形态。"
    )
    sections.append(_sec_table("总体描述结果", headers, rows, description=desc_text))

    # 智能分析
    smart_parts = []
    for v in variables:
        s = pd.to_numeric(df[v], errors="coerce").dropna()
        skew = s.skew()
        cv = s.std() / s.mean() if s.mean() != 0 else 0
        skew_desc = "近似对称" if abs(skew) < 0.5 else ("右偏" if skew > 0 else "左偏")
        cv_note = f"变异系数（CV）为{_fmt(abs(cv), 3)}，{'大于0.15，当前数据中可能存在异常值，建议对异常或者表现较为突出的指标进行分析' if abs(cv) > 0.15 else '小于0.15，数据离散程度较低'}。"
        smart_parts.append(
            f"基于{v}，{cv_note}"
        )
    sections.append(_sec_smart("\n".join(smart_parts)))

    # 直方图
    hist_charts = [c for c in (_hist_chart(v, df[v]) for v in variables) if c]
    if hist_charts:
        hist_desc = (
            "上图以直方图的形式展示了各变量的频率分布情况，"
            "可用来直观了解数据的分布特征。"
        )
        sections.append(_sec_charts("直方图", hist_charts, hist_desc))

    # 箱型图
    box_charts = [c for c in (_box_chart(v, df[v]) for v in variables) if c]
    if box_charts:
        box_desc = (
            "上图以箱型图的形式展示了各变量高峰趋势分析的结果，"
            "高峰趋势用极大值、极小值、25%分位数、中位数、75%分位数等统计指标对数据分布进行差异（稳定性）溯源。\n"
            "PS：极大值、极小值并非该数据的最大值、最小值，"
            "该值为箱型图的内限，即大于极大值或小于极小值的点视为异常点。"
        )
        sections.append(_sec_charts("箱型图", box_charts, box_desc))

    sections.append(_build_missing_table(df, variables))
    sections.append(_sec_refs(_REFS_GENERAL))

    description = f"各变量的描述统计结果如表所示。{'，'.join(descs)}。"
    return {"name": "描述性统计", "headers": headers, "rows": rows, "description": description, "sections": sections}

run = descriptive
