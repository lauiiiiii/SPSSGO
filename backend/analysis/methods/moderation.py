# -*- coding: utf-8 -*-
# spssgo
from io import StringIO

from backend.r_runner import RExecutionError, is_r_runtime_available, run_r_script

METHOD_KEY = "moderation"
METHOD_META = {'label': '调节作用',
 'category': '回归&因果分析包',
 'description': '检验调节变量 W 是否改变了自变量 X 对因变量 Y 的影响（分层回归）',
 'slots': [{'key': 'y', 'label': '因变量(Y)', 'type': 'single', 'accept': 'numeric', 'hint': '放入因变量'},
           {'key': 'x',
            'label': '自变量(X)',
            'type': 'single',
            'accept': 'any',
            'acceptLabel': '定量/定类',
            'hint': '放入自变量'},
           {'key': 'w',
            'label': '调节变量(W)',
            'type': 'single',
            'accept': 'any',
            'acceptLabel': '定量/定类',
            'hint': '放入调节变量'},
           {'key': 'controls',
            'label': '控制变量',
            'type': 'multiple',
            'accept': 'numeric',
            'min': 0,
            'hint': '可选，放入需要控制的变量'}],
 'options': [{'key': 'moderation_type',
              'label': '调节类型',
              'choices': ['X定量W定量(默认)', 'X定量W定类', 'X定类W定量'],
              'default': 'X定量W定量(默认)',
              'hint': '因变量Y固定为定量变量；当X或W为定类变量时会按哑变量进入模型。'},
             {'key': 'data_process',
              'label': '数据处理',
              'choices': ['中心化(默认)', '标准化', '不处理'],
              'default': '中心化(默认)',
              'hint': '仅处理定量自变量X和定量调节变量W；因变量和控制变量不处理。'}],
 'param_builder': 'direct'}

def moderation_analysis(df, params):
    """
    调节效应检验入口：Python 只做字段校验和数据打包，计算固定交给 R。

    @param df: 数据 DataFrame
    @param params: 包含 x, w, y 的参数字典
    @return: 含 sections 的结果字典
    """
    x = params.get("x", "")
    w = params.get("w", "")
    y = params.get("y", "")
    controls = params.get("controls") or []
    if isinstance(controls, str):
        controls = [controls]
    controls = [col for col in controls if col in df.columns and col not in {x, w, y}]
    if not all(v in df.columns for v in [x, w, y]):
        return {"name": "调节效应检验", "headers": [], "rows": [], "description": "缺少所需变量。"}

    if not is_r_runtime_available():
        return {"name": "调节效应检验", "headers": [], "rows": [], "description": "R 运行环境不可用，调节效应分析需要 R 引擎执行。"}

    csv_buffer = StringIO()
    df[[x, w, y] + controls].to_csv(csv_buffer, index=False)
    payload = {
        "x": x,
        "w": w,
        "y": y,
        "controls": controls,
        "moderation_type": params.get("moderation_type") or "X定量W定量(默认)",
        "data_process": params.get("data_process") or "中心化(默认)",
        "data_file": "moderation_input.csv",
    }
    try:
        result = run_r_script(
            "moderation.R",
            payload=payload,
            temp_files={"moderation_input.csv": csv_buffer.getvalue()},
        )
    except RExecutionError as exc:
        return {"name": "调节效应检验", "headers": [], "rows": [], "description": f"R 调节效应分析执行失败：{str(exc)}"}

    if isinstance(result, dict) and result.get("success"):
        return result
    if isinstance(result, dict) and result.get("error"):
        return {"name": "调节效应检验", "headers": [], "rows": [], "description": str(result["error"])}
    return {"name": "调节效应检验", "headers": [], "rows": [], "description": "R 调节效应分析未返回有效结果。"}

run = moderation_analysis
