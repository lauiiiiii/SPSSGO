# -*- coding: utf-8 -*-
# Kano 模型：按正反向题配对输出分类矩阵、汇总表、Better/Worse 和有效样本量。
from backend.analysis.common import *

METHOD_KEY = "kano"
METHOD_META = {
    "label": "Kano模型",
    "category": "问卷分析包",
    "description": "基于正向题与反向题的配对回答识别题项的Kano类别",
    "order": 90,
    "slots": [
        {
            "key": "functional_vars",
            "label": "正向题",
            "type": "multiple",
            "accept": "categorical",
            "min": 1,
            "hint": "按顺序放入正向题变量",
        },
        {
            "key": "dysfunctional_vars",
            "label": "反向题",
            "type": "multiple",
            "accept": "categorical",
            "min": 1,
            "hint": "按顺序放入与正向题一一对应的反向题变量",
        },
    ],
    "options": [],
    "param_builder": "direct",
}

ANSWER_LABELS = {
    "1": "不喜欢",
    "2": "能忍受",
    "3": "无所谓",
    "4": "理应如此",
    "5": "喜欢",
}
ANSWER_ALIASES = {
    "勉强接受": "能忍受",
    "理所当然": "理应如此",
}
ANSWER_ORDER = ["不喜欢", "能忍受", "无所谓", "理应如此", "喜欢"]
CATEGORY_ORDER = ["A", "O", "M", "I", "R", "Q"]
CATEGORY_LABELS = {
    "A": "魅力属性",
    "O": "期望属性",
    "M": "必备属性",
    "I": "无差异属性",
    "R": "反向属性",
    "Q": "可疑属性",
}
KANO_MAP = {
    ("喜欢", "喜欢"): "Q",
    ("喜欢", "理应如此"): "A",
    ("喜欢", "无所谓"): "A",
    ("喜欢", "能忍受"): "A",
    ("喜欢", "不喜欢"): "O",
    ("理所当然", "喜欢"): "R",
    ("理应如此", "喜欢"): "R",
    ("理应如此", "理应如此"): "I",
    ("理应如此", "无所谓"): "I",
    ("理应如此", "能忍受"): "I",
    ("理应如此", "不喜欢"): "M",
    ("无所谓", "喜欢"): "R",
    ("无所谓", "理应如此"): "I",
    ("无所谓", "无所谓"): "I",
    ("无所谓", "能忍受"): "I",
    ("无所谓", "不喜欢"): "M",
    ("能忍受", "喜欢"): "R",
    ("能忍受", "理应如此"): "I",
    ("能忍受", "无所谓"): "I",
    ("能忍受", "能忍受"): "I",
    ("能忍受", "不喜欢"): "M",
    ("不喜欢", "喜欢"): "R",
    ("不喜欢", "理应如此"): "R",
    ("不喜欢", "无所谓"): "R",
    ("不喜欢", "能忍受"): "R",
    ("不喜欢", "不喜欢"): "Q",
}


def _answer_text(value):
    if pd.isna(value):
        return ""
    text = str(value).strip()
    numeric = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.notna(numeric) and float(numeric).is_integer():
        text = str(int(numeric))
    answer = ANSWER_LABELS.get(text, text)
    return ANSWER_ALIASES.get(answer, answer)


def _pct(value, total):
    return value / total * 100 if total else 0


def _pct_text(value, total):
    return f"{_fmt(_pct(value, total), 3)}%"


def _better(counts):
    denom = sum(counts[key] for key in ["A", "O", "M", "I"])
    return (counts["A"] + counts["O"]) / denom * 100 if denom else 0


def _worse(counts):
    denom = sum(counts[key] for key in ["A", "O", "M", "I"])
    return -1 * (counts["O"] + counts["M"]) / denom * 100 if denom else 0


def _dominant_category(counts):
    return max(CATEGORY_ORDER, key=lambda key: counts[key])


def _kano_matrix_rows():
    rows = []
    for index, positive in enumerate(ANSWER_ORDER):
        row = []
        if index == 0:
            row.append({
                "text": "正向题",
                "rowspan": len(ANSWER_ORDER),
                "class": "kano-axis-cell",
            })
        row.append({
            "text": f"{positive}\n({index + 1}分)",
            "class": "kano-answer-cell",
        })
        for negative in ANSWER_ORDER:
            category = KANO_MAP.get((positive, negative), "Q")
            row.append({
                "text": category,
                "class": f"kano-rule-cell kano-rule-{category.lower()}",
            })
        rows.append(row)
    return rows


def _kano_matrix_export_rows():
    rows = []
    for positive in ANSWER_ORDER:
        row = ["正向题", positive]
        for negative in ANSWER_ORDER:
            row.append(KANO_MAP.get((positive, negative), "Q"))
        rows.append(row)
    return rows


def _metric_chart(labels, better_values, worse_values):
    return {
        "chartType": "kano_better_worse",
        "title": "Better-Worse系数图",
        "data": {
            "labels": labels,
            "better": better_values,
            "worse": worse_values,
            "worseAbs": [abs(value) for value in worse_values],
            "xLabel": "Worse绝对值",
            "yLabel": "Better",
        },
    }


def kano_analysis(df, params):
    """
    Kano 模型：基于正向/反向题对计算 Kano 类别。

    @param df: 数据 DataFrame
    @param params: functional_vars 与 dysfunctional_vars 为一一配对题项
    @return: Kano 分类对照表、百分比/数字汇总、Better/Worse 和有效样本量
    """
    functional_vars = _resolve_cols(df, params.get("functional_vars", []))
    dysfunctional_vars = _resolve_cols(
        df,
        params.get("dysfunctional_vars", []),
    )
    if (
        not functional_vars
        or not dysfunctional_vars
        or len(functional_vars) != len(dysfunctional_vars)
    ):
        return {
            "name": "Kano模型",
            "headers": [],
            "rows": [],
            "description": "请成对提供等数量的正向题和反向题。",
        }

    percent_rows = []
    count_rows = []
    valid_rows = []
    labels = []
    better_values = []
    worse_values = []
    summaries = []
    for f_var, d_var in zip(functional_vars, dysfunctional_vars):
        item_label = f"{f_var} & {d_var}"
        temp = df[[f_var, d_var]].dropna()
        counts = {key: 0 for key in CATEGORY_ORDER}
        for _, row in temp.iterrows():
            f_ans = _answer_text(row[f_var])
            d_ans = _answer_text(row[d_var])
            counts[KANO_MAP.get((f_ans, d_ans), "Q")] += 1

        total = int(sum(counts.values()))
        dominant = _dominant_category(counts)
        better = _better(counts)
        worse = _worse(counts)
        labels.append(item_label)
        better_values.append(round(better, 3))
        worse_values.append(round(worse, 3))
        percent_rows.append([
            item_label,
            *[_pct_text(counts[key], total) for key in CATEGORY_ORDER],
            CATEGORY_LABELS[dominant],
            f"{_fmt(better, 3)}%",
            f"{_fmt(worse, 3)}%",
        ])
        count_rows.append([
            item_label,
            *[str(counts[key]) for key in CATEGORY_ORDER],
            CATEGORY_LABELS[dominant],
            f"{_fmt(better, 3)}%",
            f"{_fmt(worse, 3)}%",
        ])
        valid_rows.append([item_label, str(total)])
        summaries.append(f"{item_label} 的分类结果为{CATEGORY_LABELS[dominant]}")

    matrix_header_rows = [
        [
            {"text": "功能/服务", "colspan": 2, "rowspan": 2},
            {"text": "负向题", "colspan": len(ANSWER_ORDER)},
        ],
        [
            *[
                f"负向-{label}\n({index + 1}分)"
                for index, label in enumerate(ANSWER_ORDER)
            ],
        ],
    ]
    matrix_headers = [
        "功能/服务",
        "正向问题",
        *[f"负向-{label}" for label in ANSWER_ORDER],
    ]
    result_headers = [
        "功能/服务", "A", "O", "M", "I", "R", "Q",
        "分类结果", "Better", "Worse",
    ]
    sections = [
        _sec_table(
            "输出结果1：KANO模型评价结果分类对照表",
            matrix_headers,
            _kano_matrix_rows(),
            note="备注：A：魅力属性；O：期望属性；M：必备属性；I：无差异属性；R：反向属性；Q：可疑属性",
            description="上表展示正向题与反向题组合回答对应的Kano分类规则。",
        ) | {
            "headerRows": matrix_header_rows,
            "bodyRowspanColumns": 1,
            "exportRows": _kano_matrix_export_rows(),
            "tableClass": "tlt--kano-matrix",
        },
        _sec_advice(
            "KANO模型用于研究功能/服务需求与满意度之间的关系情况；\n"
            "第一：同一功能/服务的问题分别从正向题和反向题两个方面询问；\n"
            "第二：正向题指有该功能/服务时的评价，反向题指没有该功能/服务时的评价；\n"
            "第三：正向题和反向题答项之间的交叉汇总用于判断Kano类别。"
        ),
        _sec_table(
            "输出结果2：KANO模型分析结果汇总",
            result_headers,
            percent_rows,
            note="备注：A：魅力属性；O：期望属性；M：必备属性；I：无差异属性；R：反向属性；Q：可疑属性",
            description="上表展示Kano属性占比、分类结果、Better和Worse值。",
        ),
        _sec_advice(
            "KANO模型结果显示六种属性分别的占比情况，以及分类结果、Better和Worse值情况；\n"
            "第一：分类结果指六种属性中占比最高一项对应的属性；\n"
            "第二：Better表示满意影响力，Worse表示不满意影响力。"
        ),
        _sec_charts(
            "输出结果3：Better-Worse系数图",
            [_metric_chart(labels, better_values, worse_values)],
            "上图展示各功能/服务的Better值与Worse绝对值，用于辅助判断功能优先级。",
        ),
        _sec_table(
            "输出结果4：KANO模型分析结果汇总-数字结果",
            result_headers,
            count_rows,
            description="上表展示Kano属性分类的频数结果。",
        ),
        _sec_table(
            "输出结果5：KANO模型分析有效样本量",
            ["项", "分析有效样本量"],
            valid_rows,
            description="上表展示Kano模型分析时各配对项的有效样本量。",
        ),
        _sec_advice(
            "上表格展示KANO模型分析时各配对项的分析有效样本量；\n"
            "当有效样本量过少时，建议移除该类项后再次分析。"
        ),
        _sec_refs(_REFS_GENERAL),
    ]
    smart = "；".join(summaries) + "。"
    return {
        "name": "Kano模型",
        "headers": result_headers,
        "rows": percent_rows,
        "description": smart,
        "sections": sections,
    }


run = kano_analysis
