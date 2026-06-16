# -*- coding: utf-8 -*-
# spssgo
from io import StringIO

from backend.analysis.common import *
from backend.r_runner import RExecutionError, is_r_runtime_available, run_r_script

METHOD_KEY = "exploratory_factor_analysis"
METHOD_META = {
    "label": "探索性因子分析（EFA）",
    "category": "综合评价",
    "description": "通过探索性因子分析识别潜在结构与指标归类",
    "order": 30,
    "slots": [
        {
            "key": "variables",
            "label": "分析变量",
            "type": "multiple",
            "accept": "numeric",
            "min": 3,
            "hint": "放入探索性因子分析变量",
        }
    ],
    "options": [
        {
            "key": "factor_count_mode",
            "label": "因子个数",
            "type": "choices",
            "choices": [
                {"value": "auto", "label": "自动抽取"},
                {"value": "fixed", "label": "固定个数"},
            ],
            "default": "auto",
            "hint": "自动抽取按特征根大于1的准则确定因子数；固定个数可手动指定提取的因子数量。",
        },
        {
            "key": "factor_count",
            "label": "固定因子数",
            "type": "number",
            "default": 2,
            "min": 1,
            "hint": "当因子个数选择「固定个数」时生效，需输入正整数。",
            "visible_if": {"factor_count_mode": "fixed"},
        },
        {
            "key": "save_factor_scores",
            "label": "保存因子得分",
            "type": "checkbox",
            "default": False,
            "hint": "将因子得分保存为新的标题，选中后每次分析均会新增生成标题，标题名称类似为FactorScore_****。",
        },
        {
            "key": "output_correlation_matrix",
            "label": "相关系数矩阵",
            "type": "checkbox",
            "default": False,
            "hint": "选中后会输出相关系数矩阵，用于分析相关关系情况。",
        },
        {
            "key": "save_composite_score",
            "label": "保存综合得分",
            "type": "checkbox",
            "default": False,
            "hint": "将综合得分保存为新的标题，选中后每次分析均会新增生成标题，标题名称类似为CompScore_****。",
        },
        {
            "key": "rotation_method",
            "label": "旋转方法",
            "choices": [
                {"value": "varimax", "label": "最大方差法Varimax(默认)"},
                {"value": "promax", "label": "最优斜交法Promax"},
            ],
            "default": "varimax",
            "hint": "旋转方法用于让因子结构更清晰，Varimax适合相互独立因子，Promax适合因子间可能相关的情况。",
        },
    ],
    "param_builder": "direct",
}


def _build_r_payload(df, variables, params):
    """构造 EFA 的 R 输入，保留原始行号给得分回填用。"""
    cols = _resolve_cols(df, variables)
    if len(cols) < 3:
        return None, None

    csv_buffer = StringIO()
    export_df = df[cols].copy()
    export_df.insert(0, "__row_id__", range(len(export_df.index)))
    export_df.to_csv(csv_buffer, index=False)
    payload = {
        "items": cols,
        "scale_name": params.get("scale_name", "量表"),
        "factor_count": params.get("factor_count") or "auto",
        "rotation_method": params.get("rotation_method", "varimax"),
        "output_correlation_matrix": bool(params.get("output_correlation_matrix")),
        "save_factor_scores": bool(params.get("save_factor_scores")),
        "save_composite_score": bool(params.get("save_composite_score")),
        "row_id_column": "__row_id__",
        "data_file": "efa_input.csv",
    }
    return payload, csv_buffer.getvalue()


def run(df, params):
    variables = _resolve_cols(df, params.get("variables", []))
    if len(variables) < 3:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "探索性因子分析至少需要 3 个变量。"}
    if not is_r_runtime_available():
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "R 运行环境不可用，探索性因子分析需要 R 引擎执行。"}

    payload, csv_text = _build_r_payload(df, variables, params)
    try:
        result = run_r_script(
            "exploratory_factor_analysis.R",
            payload=payload,
            temp_files={"efa_input.csv": csv_text},
        )
    except RExecutionError as exc:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": f"R 探索性因子分析执行失败：{str(exc)}"}

    if isinstance(result, dict) and result.get("success"):
        result["name"] = METHOD_META["label"]
        return result
    if isinstance(result, dict) and result.get("error"):
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": str(result["error"])}
    return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "R 探索性因子分析未返回有效结果。"}
