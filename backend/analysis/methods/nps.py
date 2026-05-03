# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "nps"
METHOD_META = {'label': 'NPS净推荐值分析',
 'category': '高级问卷分析包',
 'description': '基于 0-10 推荐评分计算贬损者、被动者、推荐者及净推荐值',
 'order': 130,
 'slots': [{'key': 'score_var',
            'label': 'NPS评分变量',
            'type': 'single',
            'accept': 'numeric',
            'hint': '放入 0-10 推荐评分变量'}],
 'options': [],
 'param_builder': 'direct'}
def run(df, params):
    score_var = params.get("score_var", "")
    if score_var not in df.columns:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": f"变量 {score_var} 不存在。"}

    scores = pd.to_numeric(df[score_var], errors="coerce").dropna()
    valid = scores[(scores >= 0) & (scores <= 10)]
    if len(valid) == 0:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效评分不足，NPS 需要 0-10 分数据。"}

    total = len(valid)
    detractors = int((valid <= 6).sum())
    passives = int(((valid >= 7) & (valid <= 8)).sum())
    promoters = int((valid >= 9).sum())
    detractor_rate = detractors / total * 100
    passive_rate = passives / total * 100
    promoter_rate = promoters / total * 100
    nps_value = promoter_rate - detractor_rate
    mean_score = float(valid.mean())

    headers = ["类别", "人数", "占比"]
    rows = [
        ["推荐者（9-10分）", str(promoters), f"{_fmt(promoter_rate, 1)}%"],
        ["被动者（7-8分）", str(passives), f"{_fmt(passive_rate, 1)}%"],
        ["贬损者（0-6分）", str(detractors), f"{_fmt(detractor_rate, 1)}%"],
        ["NPS", _fmt(nps_value, 1), ""],
    ]

    sections = [
        _sec_table("NPS分类结果", headers, rows, description="NPS = 推荐者占比 - 贬损者占比，取值范围通常为 -100 到 100。"),
        _sec_table(
            "评分概况",
            ["指标", "值"],
            [
                ["有效样本量", str(total)],
                ["平均推荐分", _fmt(mean_score, 2)],
                ["最高分", _fmt(valid.max(), 0)],
                ["最低分", _fmt(valid.min(), 0)],
            ],
        ),
    ]

    if nps_value >= 50:
        level = "表现非常强"
    elif nps_value >= 20:
        level = "表现较好"
    elif nps_value >= 0:
        level = "处于可接受区间"
    else:
        level = "需要重点优化"
    sections.append(
        _sec_smart(
            f"基于 {score_var} 的 NPS 分析显示，推荐者占比为 {_fmt(promoter_rate, 1)}%，贬损者占比为 {_fmt(detractor_rate, 1)}%，"
            f"NPS = {_fmt(nps_value, 1)}，整体口碑{level}。"
        )
    )
    sections.append(
        _sec_advice(
            "第一：优先关注贬损者比例是否偏高；\n"
            "第二：NPS 最好结合人群、产品线或时间维度做细分对比；\n"
            "第三：若样本并非 0-10 分量表，请先完成量表映射后再使用 NPS。"
        )
    )
    sections.append(_sec_refs(_REFS_GENERAL))

    return {
        "name": METHOD_META["label"],
        "headers": headers,
        "rows": rows,
        "description": f"NPS 分析完成，共纳入 {total} 个有效样本，净推荐值为 {_fmt(nps_value, 1)}。",
        "sections": sections,
    }
