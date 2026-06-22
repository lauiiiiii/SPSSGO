# -*- coding: utf-8 -*-
# spssgo
# 路径分析：支持用户自定义路径，每条路径定义一个变量对另一个变量的影响。
# 前端逐条定义路径：[变量A] 影响 [变量B]
from io import StringIO

from backend.analysis.common import _resolve_cols
from backend.r_runner import RExecutionError, is_r_runtime_available, run_r_script

METHOD_KEY = "path_analysis"
METHOD_META = {
    'label': '路径分析',
    'category': '高级回归&因果分析包',
    'description': '分析多个观测变量之间的直接路径与间接路径，输出直接效应、间接效应、总效应及修正指数',
    'order': 100,
    'slots': [],
    'options': [],
    'param_builder': 'direct'
}


def run(df, params):
    """
    路径分析入口：Python 只做字段校验和数据打包，模型估计固定交给 R/lavaan。
    用户在前端逐条定义路径，每条路径包含 from 和 to 两个变量。
    """
    paths = params.get("paths", [])

    if not paths or len(paths) < 1:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "至少需要定义 1 条路径。"}

    # 解析路径，提取所有涉及的变量
    all_variables = set()
    valid_paths = []
    for path in paths:
        from_var = path.get("from", "")
        to_var = path.get("to", "")
        if from_var and to_var and from_var != to_var:
            all_variables.add(from_var)
            all_variables.add(to_var)
            valid_paths.append({"from": from_var, "to": to_var})

    if not valid_paths:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "没有有效的路径定义。"}

    all_variables = list(all_variables)

    # 检查变量是否存在
    missing = [v for v in all_variables if v not in df.columns]
    if missing:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": f"以下变量不存在：{', '.join(missing)}。"}

    if not is_r_runtime_available():
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "R 运行环境不可用，路径分析需要 R 引擎执行。"}

    csv_buffer = StringIO()
    df[all_variables].to_csv(csv_buffer, index=False)
    payload = {
        "paths": valid_paths,
        "data_file": "path_analysis_input.csv",
    }
    try:
        result = run_r_script(
            "path_analysis.R",
            payload=payload,
            temp_files={"path_analysis_input.csv": csv_buffer.getvalue()},
        )
    except RExecutionError as exc:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": f"R 路径分析执行失败：{str(exc)}"}

    if isinstance(result, dict) and result.get("success"):
        result["name"] = METHOD_META["label"]
        return result
    if isinstance(result, dict) and result.get("error"):
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": str(result["error"])}
    return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "R 路径分析未返回有效结果。"}
