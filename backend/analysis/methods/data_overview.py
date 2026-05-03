# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "data_overview"
METHOD_META = {'label': '数据概览',
 'category': '数据概览',
 'description': '快速查看数据集规模、变量类型、缺失情况和变量明细',
 'order': 60,
 'slots': [{'key': 'variables',
            'label': '变量',
            'type': 'multiple',
            'accept': 'any',
            'min': 1,
            'hint': '放入需要概览的一个或多个变量'}],
 'options': [],
 'param_builder': 'direct'}

def data_overview(df, params):
    """
    数据概览：汇总数据规模、变量类型和缺失情况

    @param df: 数据 DataFrame
    @param params: 未使用
    @return: 含 sections 的结果字典
    """
    variables = params.get("variables", [])
    variables = _resolve_cols(df, variables) if variables else list(df.columns)
    if not variables:
        return {"name": "数据概览", "headers": [], "rows": [], "description": "未找到指定变量。"}

    sub_df = df[variables].copy()
    row_count = int(sub_df.shape[0])
    col_count = int(sub_df.shape[1])
    total_cells = row_count * col_count
    missing_cells = int(sub_df.isna().sum().sum())
    missing_rate = missing_cells / total_cells * 100 if total_cells else 0

    numeric_cols = [c for c in sub_df.columns if pd.api.types.is_numeric_dtype(sub_df[c])]
    categorical_cols = []
    text_cols = []
    for col in sub_df.columns:
        if col in numeric_cols:
            continue
        non_null = sub_df[col].dropna()
        nunique = int(non_null.nunique())
        unique_ratio = (nunique / len(non_null)) if len(non_null) else 0
        if nunique <= 50 and unique_ratio <= 0.5:
            categorical_cols.append(col)
        else:
            text_cols.append(col)

    overview_headers = ["指标", "值"]
    overview_rows = [
        ["样本量（行）", str(row_count)],
        ["变量数（列）", str(col_count)],
        ["定量变量数", str(len(numeric_cols))],
        ["定类变量数", str(len(categorical_cols))],
        ["文本变量数", str(len(text_cols))],
        ["缺失单元格数", str(missing_cells)],
        ["整体缺失率", _fmt(missing_rate, 1) + "%"],
    ]

    var_headers = ["变量名", "类型", "非缺失数", "缺失数", "缺失率", "唯一值数"]
    var_rows = []
    for col in sub_df.columns:
        non_null_count = int(sub_df[col].notna().sum())
        missing_count = row_count - non_null_count
        col_missing_rate = missing_count / row_count * 100 if row_count else 0
        if col in numeric_cols:
            var_type = "定量"
        elif col in categorical_cols:
            var_type = "定类"
        else:
            var_type = "文本"
        var_rows.append([
            str(col),
            var_type,
            str(non_null_count),
            str(missing_count),
            _fmt(col_missing_rate, 1) + "%",
            str(int(sub_df[col].nunique(dropna=True))),
        ])

    sections = []
    sections.append(_sec_table("数据集总体概览", overview_headers, overview_rows, description="展示当前数据集的规模、变量构成与整体缺失情况。"))
    sections.append(_sec_table("变量概览", var_headers, var_rows, description="逐个变量展示类型、缺失情况和唯一值数量，便于后续选取分析变量。"))

    advice = (
        "正式分析前建议先查看数据概览；\n"
        "第一：确认样本量和变量数量是否符合预期；\n"
        "第二：重点检查缺失率较高或唯一值异常的变量；\n"
        "第三：再根据变量类型选择后续适合的统计分析方法。"
    )
    sections.append(_sec_advice(advice))

    smart = (
        f"当前选中变量共有{col_count}个，样本量为{row_count}行，"
        f"其中定量变量{len(numeric_cols)}个、定类变量{len(categorical_cols)}个、文本变量{text_cols and len(text_cols) or 0}个。"
        f"整体缺失率为{_fmt(missing_rate, 1)}%。"
    )
    sections.append(_sec_smart(smart))
    sections.append(_sec_refs(_REFS_GENERAL))

    return {"name": "数据概览", "headers": overview_headers, "rows": overview_rows, "description": smart, "sections": sections}

run = data_overview
