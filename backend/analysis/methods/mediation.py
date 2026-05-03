# -*- coding: utf-8 -*-
# spssgo
from io import StringIO

from backend.r_runner import RExecutionError, is_r_runtime_available, run_r_script

METHOD_KEY = "mediation"
METHOD_META = {'label': '中介效应分析',
 'category': '回归&因果分析包',
 'description': '使用 R/lavaan 检验中介变量 M 在自变量 X 和因变量 Y 之间的中介作用',
 'slots': [{'key': 'x', 'label': '自变量(X)', 'type': 'single', 'accept': 'numeric', 'hint': '放入自变量'},
           {'key': 'm',
            'label': '中介变量(M)',
            'type': 'single',
            'accept': 'numeric',
            'hint': '放入中介变量'},
           {'key': 'y', 'label': '因变量(Y)', 'type': 'single', 'accept': 'numeric', 'hint': '放入因变量'}],
 'options': [],
 'param_builder': 'direct'}

def mediation_analysis(df, params):
    """
    中介效应检验入口：Python 只做字段校验和数据打包，计算固定交给 R/lavaan。

    @param df: 数据 DataFrame
    @param params: 包含 x, m, y 的参数字典
    @return: 含 sections 的结果字典
    """
    x = params.get("x", "")
    m = params.get("m", "")
    y = params.get("y", "")
    if not all(v in df.columns for v in [x, m, y]):
        return {"name": "中介效应检验", "headers": [], "rows": [], "description": "缺少所需变量。"}

    if not is_r_runtime_available():
        return {"name": "中介效应检验", "headers": [], "rows": [], "description": "R 运行环境不可用，中介效应分析需要 R 引擎执行。"}

    csv_buffer = StringIO()
    df[[x, m, y]].to_csv(csv_buffer, index=False)
    payload = {"x": x, "m": m, "y": y, "data_file": "mediation_input.csv"}
    try:
        result = run_r_script(
            "mediation.R",
            payload=payload,
            temp_files={"mediation_input.csv": csv_buffer.getvalue()},
        )
    except RExecutionError as exc:
        return {"name": "中介效应检验", "headers": [], "rows": [], "description": f"R 中介效应分析执行失败：{str(exc)}"}

    if isinstance(result, dict) and result.get("success"):
        return result
    if isinstance(result, dict) and result.get("error"):
        return {"name": "中介效应检验", "headers": [], "rows": [], "description": str(result["error"])}
    return {"name": "中介效应检验", "headers": [], "rows": [], "description": "R 中介效应分析未返回有效结果。"}

run = mediation_analysis
