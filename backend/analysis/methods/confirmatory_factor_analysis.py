# -*- coding: utf-8 -*-
# spssgo
from io import StringIO

from backend.analysis.common import *
from backend.r_runner import RExecutionError, is_r_runtime_available, run_r_script

METHOD_KEY = "confirmatory_factor_analysis"
METHOD_META = {'label': '验证性因子分析',
 'category': '问卷分析包',
 'description': '支持多因子测量模型的验证性因子分析，输出拟合指标、标准化残差和修正建议',
 'order': 80,
 'slots': [{'key': 'factor1_vars',
            'label': '因子1题项',
            'type': 'multiple',
            'accept': 'numeric',
            'min': 2,
            'hint': '放入因子1对应的题项'},
           {'key': 'factor2_vars',
            'label': '因子2题项',
            'type': 'multiple',
            'accept': 'numeric',
            'min': 0,
            'hint': '可选：放入因子2对应的题项'},
           {'key': 'factor3_vars',
            'label': '因子3题项',
            'type': 'multiple',
            'accept': 'numeric',
            'min': 0,
            'hint': '可选：放入因子3对应的题项'},
           {'key': 'factor4_vars',
            'label': '因子4题项',
            'type': 'multiple',
            'accept': 'numeric',
            'min': 0,
            'hint': '可选：放入因子4对应的题项'}],
 'options': [],
 'param_builder': 'direct'}

def confirmatory_factor_analysis(df, params):
    """
    验证性因子分析：支持多因子测量模型，使用 R 引擎执行。
    """
    factor_keys = []
    factor_pattern = re.compile(r"^factor(\d+)_vars$")
    for key in params.keys():
        match = factor_pattern.match(str(key))
        if match:
            factor_keys.append((int(match.group(1)), key))
    factor_keys.sort(key=lambda item: item[0])

    factor_candidates = []
    if factor_keys:
        for idx, key in factor_keys:
            factor_candidates.append((f"F{idx}", _resolve_cols(df, params.get(key, []))))
    else:
        factor_candidates.append(("F1", _resolve_cols(df, params.get("factor1_vars", []) or params.get("variables", []))))
    factor_map = {name: vars_ for name, vars_ in factor_candidates if vars_}
    variables = []
    for vars_ in factor_map.values():
        variables.extend(vars_)
    variables = list(dict.fromkeys(variables))

    if not factor_map:
        return {"name": "验证性因子分析", "headers": [], "rows": [], "description": "请至少为一个因子放入题项。"}
    if any(len(items) < 2 for items in factor_map.values()):
        return {"name": "验证性因子分析", "headers": [], "rows": [], "description": "每个因子至少需要2个题项。"}
    if len(variables) < 3:
        return {"name": "验证性因子分析", "headers": [], "rows": [], "description": "至少需要3个题项。" }

    if not is_r_runtime_available():
        return {"name": "验证性因子分析", "headers": [], "rows": [], "description": "R 运行环境不可用，验证性因子分析需要 R 引擎执行。"}

    csv_buffer = StringIO()
    df[variables].to_csv(csv_buffer, index=False)
    payload = {
        "factor_map": factor_map,
        "data_file": "cfa_input.csv",
    }
    try:
        r_result = run_r_script(
            "confirmatory_factor_analysis.R",
            payload=payload,
            temp_files={"cfa_input.csv": csv_buffer.getvalue()},
        )
    except RExecutionError as exc:
        return {"name": "验证性因子分析", "headers": [], "rows": [], "description": f"R 验证性因子分析执行失败：{str(exc)}"}

    if isinstance(r_result, dict) and r_result.get("success"):
        return {
            "name": r_result.get("name") or "验证性因子分析",
            "headers": r_result.get("headers") or [],
            "rows": r_result.get("rows") or [],
            "description": r_result.get("description") or "验证性因子分析完成。",
            "sections": r_result.get("sections") or [],
        }
    if isinstance(r_result, dict) and r_result.get("error"):
        return {"name": "验证性因子分析", "headers": [], "rows": [], "description": str(r_result["error"])}
    return {"name": "验证性因子分析", "headers": [], "rows": [], "description": "R 验证性因子分析未返回有效结果。"}

run = confirmatory_factor_analysis
