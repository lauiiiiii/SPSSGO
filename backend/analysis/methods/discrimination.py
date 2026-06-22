# -*- coding: utf-8 -*-
# 区分度分析：检验题项是否能够有效区分高水平与低水平样本。
# 支持分位数选择（25/27/30），对齐 SPSSAU 的分组方式。
from io import StringIO

from backend.analysis.common import _resolve_cols
from backend.r_runner import RExecutionError, is_r_runtime_available, run_r_script

METHOD_KEY = "discrimination"
METHOD_META = {
    'label': '区分度分析',
    'category': '高级问卷分析包',
    'description': '检验题项是否能够有效区分高水平与低水平样本',
    'order': 140,
    'slots': [
        {
            'key': 'variables',
            'label': '题项变量',
            'type': 'multiple',
            'accept': 'numeric',
            'min': 2,
            'hint': '放入量表题项',
        }
    ],
    'options': [
        {
            'key': 'percentile',
            'label': '分位数',
            'choices': [
                {'value': 25, 'label': '25/75'},
                {'value': 27, 'label': '27/73'},
                {'value': 30, 'label': '30/70'},
            ],
            'default': 27,
            'hint': '按总分排序后取前后指定百分比作为高分组和低分组，中间为中间组。',
        },
    ],
    'param_builder': 'direct',
}


def _clean_percentile(value):
    """将前端传入的分位数标准化为 25/27/30，非法值回退到 27。"""
    if value is None:
        return 27
    try:
        v = int(value)
    except (TypeError, ValueError):
        return 27
    if v in (25, 27, 30):
        return v
    return 27


def run(df, params):
    """
    题项区分度入口：Python 保留字段入口，R 输出项目分析表和建议。

    @param df: 当前数据集
    @param params: variables（题项变量数组）、percentile（分位数，默认 27）
    @return: 对齐 SPSSAU 的结果 sections
    """
    variables = _resolve_cols(df, params.get("variables", []))
    if len(variables) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "至少需要 2 个题项变量。"}

    if not is_r_runtime_available():
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "R 运行环境不可用，区分度分析需要 R 引擎执行。"}

    percentile = _clean_percentile(params.get("percentile", 27))

    csv_buffer = StringIO()
    df[variables].to_csv(csv_buffer, index=False)
    payload = {
        "variables": variables,
        "data_file": "discrimination_input.csv",
        "percentile": percentile,
    }
    try:
        result = run_r_script(
            "discrimination.R",
            payload=payload,
            temp_files={"discrimination_input.csv": csv_buffer.getvalue()},
        )
    except RExecutionError as exc:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": f"R 区分度分析执行失败：{str(exc)}"}

    if isinstance(result, dict) and result.get("success"):
        result["name"] = METHOD_META["label"]
        return result
    if isinstance(result, dict) and result.get("error"):
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": str(result["error"])}
    return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "R 区分度分析未返回有效结果。"}
