# -*- coding: utf-8 -*-
# spssgo
from io import StringIO

from backend.analysis.common import _resolve_cols
from backend.r_runner import RExecutionError, is_r_runtime_available, run_r_script

METHOD_KEY = "path_analysis"
METHOD_META = {'label': '路径分析',
 'category': '高级回归&因果分析包',
 'description': '分析多个观测变量之间的直接路径与间接路径',
 'order': 100,
 'slots': [{'key': 'dependent',
            'label': '因变量(Y)',
            'type': 'single',
            'accept': 'numeric',
            'hint': '放入最终结果变量'},
           {'key': 'predictors',
            'label': '路径变量',
            'type': 'multiple',
            'accept': 'numeric',
            'min': 2,
            'hint': '放入参与路径模型的变量'}],
 'options': [],
 'param_builder': 'direct'}


def run(df, params):
    """
    路径分析入口：Python 只做字段校验和数据打包，模型估计固定交给 R/lavaan。
    """
    dependent = params.get("dependent", "")
    predictors = _resolve_cols(df, params.get("predictors", []))
    if dependent not in df.columns:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": f"因变量 {dependent} 不存在。"}
    if len(predictors) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "至少需要 2 个路径变量。"}

    if not is_r_runtime_available():
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "R 运行环境不可用，路径分析需要 R 引擎执行。"}

    variables = [dependent] + predictors
    csv_buffer = StringIO()
    df[variables].to_csv(csv_buffer, index=False)
    payload = {"dependent": dependent, "predictors": predictors, "data_file": "path_analysis_input.csv"}
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
