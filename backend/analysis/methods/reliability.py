# -*- coding: utf-8 -*-
# spssgo
from io import StringIO

from backend.analysis.common import *
from backend.r_runner import RExecutionError, is_r_runtime_available, run_r_script

METHOD_KEY = "reliability"
METHOD_META = {'label': '信度分析',
 'category': '问卷分析包',
 'description': '信度分析用于分析问卷中各题目的可靠性，检验量表内部一致性',
 'order': 20,
 'slots': [{'key': 'variables',
            'label': '分析变量',
            'type': 'multiple',
            'accept': 'numeric',
            'min': 2,
            'hint': '放入同一量表的所有题项'}],
 'options': [{'key': 'type',
              'label': '类型',
              'choices': ["Cronbach's α", "折半系数", "McDonald Omega", "theta系数"],
              'default': "Cronbach's α"}],
 'param_builder': 'reliability'}

def _build_r_payload(df, items_groups: dict[str, list[str]], selected_type: str = "Cronbach's α"):
    scale_payload = {}
    selected_cols: list[str] = []
    for scale_name, item_cols in items_groups.items():
        cols = _resolve_cols(df, item_cols)
        if len(cols) >= 2:
            scale_payload[scale_name] = cols
            for col in cols:
                if col not in selected_cols:
                    selected_cols.append(col)
    if not scale_payload:
        return None, None
    csv_buffer = StringIO()
    df[selected_cols].to_csv(csv_buffer, index=False)
    payload = {
        "items_groups": scale_payload,
        "data_file": "reliability_input.csv",
        "selected_type": selected_type,
    }
    return payload, csv_buffer.getvalue()


def reliability_analysis(df, params):
    items_groups = params.get("items_groups", {})
    if not items_groups:
        return {"name": "信度分析", "headers": [], "rows": [], "description": "未指定量表题目。"}
    if not is_r_runtime_available():
        return {"name": "信度分析", "headers": [], "rows": [], "description": "R 运行环境不可用，信度分析需要 R 引擎执行。"}

    selected_type = params.get("type", "Cronbach's α")
    payload, csv_text = _build_r_payload(df, items_groups, selected_type)
    if not payload or not csv_text:
        return {"name": "信度分析", "headers": [], "rows": [], "description": "请至少为一个量表放入 2 个有效题项。"}

    try:
        result = run_r_script(
            "reliability.R",
            payload=payload,
            temp_files={"reliability_input.csv": csv_text},
        )
    except RExecutionError as exc:
        return {"name": "信度分析", "headers": [], "rows": [], "description": f"R 信度分析执行失败：{str(exc)}"}

    if isinstance(result, dict) and result.get("success"):
        return {
            "name": result.get("name") or "信度分析",
            "headers": result.get("headers") or [],
            "rows": result.get("rows") or [],
            "description": result.get("description") or "信度分析完成。",
            "sections": result.get("sections") or [],
        }
    if isinstance(result, dict) and result.get("error"):
        return {"name": "信度分析", "headers": [], "rows": [], "description": str(result["error"])}
    return {"name": "信度分析", "headers": [], "rows": [], "description": "R 信度分析未返回有效结果。"}


run = reliability_analysis
