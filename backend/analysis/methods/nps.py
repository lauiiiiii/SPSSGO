# -*- coding: utf-8 -*-
# NPS 净推荐值分析，支持多个 NPS 打分变量对比（对齐 SPSSAU）。
# 输入为 0-10 推荐评分变量，输出各分数段占比、NPS 分类占比、NPS 值对比图和类型分布图。
from backend.analysis.common import *

METHOD_KEY = "nps"

METHOD_META = {
    "label": "NPS净推荐值分析",
    "category": "高级问卷分析包",
    "description": "基于 0-10 推荐评分计算贬损者、被动者、推荐者及净推荐值，支持多个 NPS 打分变量对比",
    "order": 130,
    "slots": [
        {
            "key": "score_vars",
            "label": "NPS测量项",
            "type": "multiple",
            "accept": "numeric",
            "min": 1,
            "hint": "放入 0-10 推荐评分变量，支持多个 NPS 打分项对比",
        }
    ],
    "options": [],
    "param_builder": "direct",
}


def _error(message):
    return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": message}


def _nps_chart(labels, values, title="NPS值"):
    return {
        "chartType": "metric_comparison",
        "title": title,
        "data": {
            "metric": title,
            "labels": labels,
            "values": values,
        },
    }


def _nps_type_chart(labels, metrics, title="NPS类型分布"):
    return {
        "chartType": "metric_comparison",
        "title": title,
        "data": {
            "multiSeries": True,
            "metrics": metrics,
            "labels": labels,
        },
    }


def _gauge_chart(value, label="NPS"):
    """仪表盘图：展示单个 NPS 值。"""
    return {
        "chartType": "gauge",
        "title": f"{label}仪表盘",
        "data": {
            "value": value,
            "label": label,
            "min": -100,
            "max": 100,
        },
    }


def _type_bar_chart(detractor_rate, passive_rate, promoter_rate, title="NPS类型占比"):
    """横向柱形图：展示贬损者/被动者/推荐者占比。"""
    return {
        "chartType": "metric_comparison",
        "title": title,
        "data": {
            "metric": title,
            "labels": ["贬损者", "被动者", "推荐者"],
            "values": [round(detractor_rate, 3), round(passive_rate, 3), round(promoter_rate, 3)],
            "defaultMode": "horizontalBar",
        },
    }


def _score_distribution_chart(score_distribution, title="分数分布"):
    """柱形图：展示 0-10 分的频数/占比分布。"""
    labels = [f"{sd['score']}分" for sd in score_distribution]
    values = [round(sd["pct"], 3) for sd in score_distribution]
    return {
        "chartType": "metric_comparison",
        "title": title,
        "data": {
            "metric": title,
            "labels": labels,
            "values": values,
            "defaultMode": "bar",
        },
    }


def _nps_level(nps_value):
    """根据 NPS 值给出评级描述（参考行业通用标准）。"""
    if nps_value > 70:
        return "世界级", "极其优秀，用户口碑极好"
    elif nps_value > 50:
        return "优秀", "显著高于行业平均水平"
    elif nps_value > 30:
        return "良好", "处于行业中上水平"
    elif nps_value >= 0:
        return "一般", "尚有提升空间，建议关注贬损者反馈"
    else:
        return "需改善", "贬损者多于推荐者，产品/服务存在明显短板"


def run(df, params):
    """
    执行 NPS 净推荐值分析（对齐 SPSSAU）。

    @param df: 当前数据集
    @param params: score_vars（NPS 打分变量名数组）
    @return: 对齐 SPSSAU 的结果 sections
    """
    params = params or {}
    score_vars = params.get("score_vars", [])
    if isinstance(score_vars, str):
        score_vars = [score_vars]

    if not score_vars:
        return _error("请放入至少 1 个 NPS 评分变量。")

    valid_vars = [v for v in score_vars if v in df.columns]
    if not valid_vars:
        return _error("所选变量在数据集中不存在。")

    # 每个变量计算 NPS 指标
    item_results = []
    for var in valid_vars:
        scores = pd.to_numeric(df[var], errors="coerce").dropna()
        valid = scores[(scores >= 0) & (scores <= 10)]
        total = len(valid)
        if total == 0:
            continue

        detractors = int((valid <= 6).sum())
        passives = int(((valid >= 7) & (valid <= 8)).sum())
        promoters = int((valid >= 9).sum())
        detractor_rate = detractors / total * 100
        passive_rate = passives / total * 100
        promoter_rate = promoters / total * 100
        nps_value = promoter_rate - detractor_rate

        # 各分数段占比（0-10 分）
        score_distribution = []
        for s in range(11):
            count = int((valid == s).sum())
            pct = count / total * 100
            score_distribution.append({"score": s, "count": count, "pct": pct})

        # 众数分数
        sorted_by_count = sorted(score_distribution, key=lambda d: d["count"], reverse=True)
        mode_score = sorted_by_count[0]["score"]

        item_results.append({
            "var": var,
            "total": total,
            "detractors": detractors,
            "passives": passives,
            "promoters": promoters,
            "detractor_rate": detractor_rate,
            "passive_rate": passive_rate,
            "promoter_rate": promoter_rate,
            "nps_value": nps_value,
            "score_distribution": score_distribution,
            "mode_score": mode_score,
        })

    if not item_results:
        return _error("有效评分不足，NPS 需要 0-10 分数据。")

    item_labels = [r["var"] for r in item_results]

    # 表 1：各分数段占比情况（支持百分比/数字切换）
    headers_1 = ["项"] + [f"{s}分" for s in range(11)]
    # 百分比模式（默认）
    rows_percent = []
    for r in item_results:
        row = [r["var"]]
        for sd in r["score_distribution"]:
            row.append(f"{sd['pct']:.3f}%")
        rows_percent.append(row)
    # 数字模式（频数）
    rows_count = []
    for r in item_results:
        row = [r["var"]]
        for sd in r["score_distribution"]:
            row.append(str(sd["count"]))
        rows_count.append(row)

    # 表 2：各类型占比情况（支持百分比/数字切换）
    headers_2 = ["项", "贬损者（0-6分）", "被动者（7-8分）", "推荐者（9-10分）", "NPS值"]
    # 百分比模式（默认）
    rows_2_percent = []
    for r in item_results:
        rows_2_percent.append([
            r["var"],
            f"{r['detractor_rate']:.3f}%",
            f"{r['passive_rate']:.3f}%",
            f"{r['promoter_rate']:.3f}%",
            f"{r['nps_value']:.3f}%",
        ])
    # 数字模式（频数）
    rows_2_count = []
    for r in item_results:
        rows_2_count.append([
            r["var"],
            str(r["detractors"]),
            str(r["passives"]),
            str(r["promoters"]),
            f"{r['nps_value']:.3f}%",  # NPS 值始终显示百分比
        ])

    # ---- 动态分析建议 ----

    # 最佳和最差 NPS
    sorted_by_nps = sorted(item_results, key=lambda r: r["nps_value"], reverse=True)
    best_item = sorted_by_nps[0]
    worst_item = sorted_by_nps[-1]
    best_level, best_desc = _nps_level(best_item["nps_value"])
    worst_level, worst_desc = _nps_level(worst_item["nps_value"])

    # 多变量对比洞察
    nps_values_list = [r["nps_value"] for r in item_results]
    nps_range = max(nps_values_list) - min(nps_values_list)
    if nps_range > 20:
        variation_note = "各测量项之间 NPS 值差异较大（极差 > 20%），说明不同产品/服务/时期的用户口碑存在明显分化，建议重点分析低分项背后的原因。"
    elif nps_range > 10:
        variation_note = "各测量项之间 NPS 值存在一定差异（极差 10%~20%），说明用户对不同测量项的推荐意愿略有不同，可进一步结合业务背景分析差异来源。"
    else:
        variation_note = "各测量项之间 NPS 值较为接近（极差 < 10%），说明用户对不同测量项的推荐意愿整体一致。"

    # 各变量分数分布洞察
    dist_insights = []
    for r in item_results:
        low_score_pct = sum(sd["pct"] for sd in r["score_distribution"] if sd["score"] <= 3)
        high_score_pct = sum(sd["pct"] for sd in r["score_distribution"] if sd["score"] >= 9)
        mode = r["mode_score"]
        dist_insights.append(
            f"「{r['var']}」：众数 {mode} 分，低分(0-3分)占比 {low_score_pct:.1f}%，高分(9-10分)占比 {high_score_pct:.1f}%；"
            f"评分集中于 {'高端' if mode >= 8 else ('中端' if mode >= 5 else '低端')}区间。"
        )

    # 贬损者洞察
    high_detractor_items = [r for r in item_results if r["detractor_rate"] > 20]
    if high_detractor_items:
        detractor_note = f"以下测量项的贬损者占比超过 20%，建议深入分析这部分用户不满意的原因：" + \
                         "；".join([f"「{r['var']}」({r['detractor_rate']:.1f}%)" for r in high_detractor_items]) + "。"
    else:
        detractor_note = "各测量项贬损者占比均在 20% 以内，整体用户负面情绪控制较好。"

    # 被动者转化提醒
    high_passive_items = [r for r in item_results if r["passive_rate"] > 30]
    if high_passive_items:
        passive_note = f"特别注意以下测量项的被动者占比较高（>30%），这部分用户处于观望状态，是最容易转化为推荐者的群体：" + \
                       "；".join([f"「{r['var']}」({r['passive_rate']:.1f}%)" for r in high_passive_items]) + \
                       "。建议针对性优化体验，推动被动者向推荐者转化。"
    else:
        passive_note = ""

    # 图表 1：NPS 值对比图
    nps_values = [round(r["nps_value"], 3) for r in item_results]
    nps_chart = _nps_chart(item_labels, nps_values, "NPS值")

    if len(item_results) >= 2:
        nps_chart_desc = (
            f"柱形越高表示 NPS 值越大，净推荐意愿越强。"
            f"本次分析中，「{best_item['var']}」的 NPS 值最高（{best_item['nps_value']:.2f}%），属于「{best_level}」水平；"
            f"「{worst_item['var']}」的 NPS 值最低（{worst_item['nps_value']:.2f}%），属于「{worst_level}」水平。"
            f"\n判断标准：NPS > 50% 为优秀，NPS 在 0~50% 之间为一般，NPS < 0% 说明贬损者多于推荐者，需要重点关注。"
        )
    else:
        nps_chart_desc = (
            f"柱形越高表示 NPS 值越大，净推荐意愿越强。"
            f"本次「{best_item['var']}」的 NPS 值为 {best_item['nps_value']:.2f}%，属于「{best_level}」水平。"
            f"\n判断标准：NPS > 50% 为优秀，NPS 在 0~50% 之间为一般，NPS < 0% 说明贬损者多于推荐者，需要重点关注。"
        )

    # 图表 2：NPS 类型分布图（多序列）
    type_chart = _nps_type_chart(
        ["贬损者", "被动者", "推荐者"],
        {
            r["var"]: [round(r["detractor_rate"], 3), round(r["passive_rate"], 3), round(r["promoter_rate"], 3)]
            for r in item_results
        },
        "NPS类型分布",
    )

    type_chart_desc = (
        "分组柱形图展示各测量项中贬损者（0-6分）、被动者（7-8分）、推荐者（9-10分）的占比构成。"
        f"\n看推荐者占比：越高说明用户口碑越好，「{best_item['var']}」推荐者占比最高（{best_item['promoter_rate']:.1f}%）；"
        f"\n看贬损者占比：越低说明不满意用户越少，「{worst_item['var']}」贬损者占比为 {worst_item['detractor_rate']:.1f}%；"
        "\n看被动者占比：这部分用户态度中立，是未来提升 NPS 的关键转化目标。"
    )

    # 表 1 的 description
    table1_desc = (
        "上表展示各 NPS 测量项在 0~10 分每个分数段上的占比分布。"
        "通过观察分数分布形态，可判断评分的集中趋势和离散程度："
        "高分段（9-10分）集中说明用户推荐意愿强，低分段（0-6分）集中说明用户体验存在明显问题。"
    )

    # 表 2 的 description
    table2_desc = (
        "上表将 0-10 分归为三种用户类型：贬损者（0-6分，不满意且可能传播负面口碑）、"
        "被动者（7-8分，态度中立，容易受竞品影响）、推荐者（9-10分，忠实用户，会主动推荐）。"
        "NPS = 推荐者占比 - 贬损者占比，取值范围为 -100%~+100%。"
    )

    # 汇总分析
    avg_nps = sum(nps_values_list) / len(nps_values_list)
    avg_level, avg_desc = _nps_level(avg_nps)
    total_valid = sum(r["total"] for r in item_results)

    # 构建复合表数据（对齐 SPSSPRO：合并分数段 + 类型占比 + NPS 值）
    compound_rows = []
    for r in item_results:
        compound_rows.append({
            "var": r["var"],
            "cells": [{"score": sd["score"], "count": sd["count"], "pct": f"{sd['pct']:.0f}"} for sd in r["score_distribution"]],
            "detractorRate": f"{r['detractor_rate']:.0f}",
            "passiveRate": f"{r['passive_rate']:.0f}",
            "promoterRate": f"{r['promoter_rate']:.0f}",
            "npsValue": str(round(r["nps_value"])),
        })

    # 构建 sections
    sections = [
        {
            "type": "nps_compound_table",
            "title": "NPS统计分析表",
            "rows": compound_rows,
            "description": "上表合并展示各 NPS 测量项的分数段分布（频数 + 百分比）、贬损者/被动者/推荐者占比及 NPS 值。",
        },
        _sec_advice(
            "NPS(客户净推荐值)用于衡量用户体验、客户忠诚度、产品口碑；"
            "\n第一：NPS打分题最低为0分，最高为10分，分值越高代表愿意推荐某产品/功能；"
            "\n第二：贬损者（0-6分）占比越高说明不满意用户越多，推荐者（9-10分）占比越高说明用户口碑越好；"
            "\n第三：NPS = 推荐者% - 贬损者%，取值范围 -100%~+100%，通常高于 50% 说明比较优秀。"
        ),
    ]

    # 每个 NPS 项输出：仪表盘 + 类型占比图 + 分数分布图（对齐 SPSSPRO 风格）
    for r in item_results:
        gauge = _gauge_chart(r["nps_value"], r["var"])
        type_bar = _type_bar_chart(r["detractor_rate"], r["passive_rate"], r["promoter_rate"], f"{r['var']}类型占比")
        score_dist = _score_distribution_chart(r["score_distribution"], f"{r['var']}分数分布")

        item_level, item_desc = _nps_level(r["nps_value"])
        item_charts_desc = (
            f"上图展示了{r['var']}的NPS得分，以及贬损者（0-6分）、被动者（7-8分）、推荐者（9-10分）的占比情况。"
            f"\nNPS 值为 {r['nps_value']:.2f}%，属于「{item_level}」水平。"
        )

        sections.append(_sec_charts(f"{r['var']}NPS分析", [gauge, type_bar, score_dist], item_charts_desc))

    # 汇总对比图（多变量时）
    if len(item_results) >= 2:
        sections.append(_sec_charts("NPS值对比", [nps_chart], nps_chart_desc))
        sections.append(_sec_charts("NPS类型分布对比", [type_chart], type_chart_desc))

    # 综合分析
    if len(item_results) >= 2:
        smart_text = (
            f"【综合分析】本次共对{len(item_results)}个测量项进行 NPS 分析，有效样本合计 {total_valid} 份。"
            f"\n平均 NPS 值为 {avg_nps:.2f}%，整体属于「{avg_level}」水平。"
            f"\n{variation_note}"
        )
        if passive_note:
            smart_text += f"\n{passive_note}"
        smart_text += (
            f"\n{detractor_note}"
            "\nNPS（净推荐值）是衡量客户忠诚度的关键指标，建议定期追踪 NPS 变化趋势，结合定性反馈（如用户评论、客服记录）深入理解贬损者不满的根因。"
        )
    else:
        smart_text = (
            f"【分析小结】本次对「{item_results[0]['var']}」进行 NPS 分析，有效样本 {item_results[0]['total']} 份。"
            f"\nNPS 值为 {item_results[0]['nps_value']:.2f}%，属于「{_nps_level(item_results[0]['nps_value'])[0]}」水平。"
            f"\n推荐者占比 {item_results[0]['promoter_rate']:.1f}%，贬损者占比 {item_results[0]['detractor_rate']:.1f}%。"
            "\nNPS（净推荐值）是衡量客户忠诚度的关键指标，建议定期追踪 NPS 变化趋势，结合定性反馈（如用户评论、客服记录）深入理解贬损者不满的根因。"
        )

    sections.append(_sec_smart(smart_text))
    sections.append(_sec_refs(_REFS_GENERAL))

    total_nps = sum(r["nps_value"] for r in item_results) / len(item_results)

    return {
        "name": METHOD_META["label"],
        "headers": ["项", "NPS值"],
        "rows": [[r["var"], f"{r['nps_value']:.3f}%"] for r in item_results],
        "description": f"NPS 分析完成，共 {len(item_results)} 个测量项，平均 NPS 值为 {total_nps:.2f}%。",
        "sections": sections,
    }
