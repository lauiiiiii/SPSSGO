# -*- coding: utf-8 -*-
# AHP 专业版入口：只处理三层决策模型参数和 R bridge，别在 Python 里补矩阵公式。
# 第一版固定为“目标-指标-方案”，暂不支持任意多级指标树。
from backend.r_runner import RExecutionError, is_r_runtime_available, run_r_script

METHOD_KEY = "ahp_professional"
METHOD_META = {
    "label": "层次分析法（AHP专业版）",
    "category": "综合评价",
    "description": "构建目标-指标-方案三层 AHP 决策模型，输出权重、一致性检验和方案排序",
    "order": 10,
    "slots": [],
    "options": [
        {
            "key": "weight_method",
            "label": "计算方法",
            "choices": [
                {"value": "sum_product", "label": "和积法"},
                {"value": "root", "label": "方根法"},
                {"value": "eigen", "label": "特征向量法"},
            ],
            "default": "sum_product",
        },
    ],
    "param_builder": "direct",
}


def _error(message):
    return {
        "name": METHOD_META["label"],
        "headers": [],
        "rows": [],
        "description": message,
    }


def run(df, params):
    """
    AHP 专业版入口。

    @param df: 当前数据集；专业版使用专家判断矩阵，不读取样本数据
    @param params: goal、criteria、alternatives、criteria_matrix、alternative_matrices、weight_method
    @return: R 脚本返回的指标权重、局部权重、综合得分和一致性检验 sections
    """
    params = params or {}
    if not is_r_runtime_available():
        return _error("R 运行环境不可用，AHP 专业版需要 R 引擎执行。")

    payload = {
        "goal": params.get("goal") or "中心主题",
        "criteria": params.get("criteria") or [],
        "alternatives": params.get("alternatives") or [],
        "criteria_matrix": params.get("criteria_matrix"),
        "alternative_matrices": params.get("alternative_matrices") or {},
        "weight_method": params.get("weight_method") or "sum_product",
    }

    try:
        result = run_r_script("ahp_professional.R", payload=payload)
    except RExecutionError as exc:
        return _error(f"R AHP 专业版执行失败：{str(exc)}")

    if isinstance(result, dict) and result.get("success"):
        return {
            "name": result.get("name") or METHOD_META["label"],
            "headers": result.get("headers") or [],
            "rows": result.get("rows") or [],
            "description": result.get("description") or "AHP 专业版完成。",
            "sections": result.get("sections") or [],
        }
    if isinstance(result, dict) and result.get("error"):
        return _error(str(result["error"]))
    return _error("R AHP 专业版未返回有效结果。")
