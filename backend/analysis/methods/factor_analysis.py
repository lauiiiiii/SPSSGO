# -*- coding: utf-8 -*-
# spssgo
from io import StringIO

from backend.analysis.common import *
from backend.r_runner import RExecutionError, is_r_runtime_available, run_r_script

METHOD_KEY = "factor_analysis"
METHOD_META = {'label': '效度分析',
 'category': '问卷分析包',
 'description': '通过 KMO 和 Bartlett 球形检验判断数据是否适合做因子分析',
 'order': 30,
 'slots': [{'key': 'variables',
            'label': '分析变量',
            'type': 'multiple',
            'accept': 'numeric',
            'min': 3,
            'hint': '放入同一量表的所有题项（至少3个）'}],
 'options': [{'key': 'factor_count',
              'label': '维度个数设置',
              'type': 'factor_count',
              'default': 'auto'}],
 'param_builder': 'factor'}


def _build_r_payload(df, items: list[str], scale_name: str, factor_count="auto"):
    cols = _resolve_cols(df, items)
    if len(cols) < 3:
        return None, None
    csv_buffer = StringIO()
    df[cols].to_csv(csv_buffer, index=False)
    payload = {
        "items": cols,
        "scale_name": scale_name,
        "factor_count": factor_count,
        "data_file": "factor_analysis_input.csv",
    }
    return payload, csv_buffer.getvalue()


def factor_analysis_check(df, params):
    items = params.get("items", [])
    scale_name = params.get("scale_name", "量表")
    factor_count = params.get("factor_count", "auto")
    payload, csv_text = _build_r_payload(df, items, scale_name, factor_count)
    if not payload or not csv_text:
        return {"name": "效度检验", "headers": [], "rows": [], "description": "需要至少3个题目。"}
    if not is_r_runtime_available():
        return {"name": "效度检验", "headers": [], "rows": [], "description": "R 运行环境不可用，效度分析需要 R 引擎执行。"}

    try:
        result = run_r_script(
            "factor_analysis.R",
            payload=payload,
            temp_files={"factor_analysis_input.csv": csv_text},
        )
    except RExecutionError as exc:
        return {"name": "效度检验", "headers": [], "rows": [], "description": f"R 效度分析执行失败：{str(exc)}"}

    if isinstance(result, dict) and result.get("success"):
        return {
            "name": result.get("name") or f"效度检验：{scale_name}",
            "headers": result.get("headers") or [],
            "rows": result.get("rows") or [],
            "description": result.get("description") or "效度分析完成。",
            "sections": result.get("sections") or [],
        }
    if isinstance(result, dict) and result.get("error"):
        return {"name": "效度检验", "headers": [], "rows": [], "description": str(result["error"])}
    return {"name": "效度检验", "headers": [], "rows": [], "description": "R 效度分析未返回有效结果。"}


run = factor_analysis_check
