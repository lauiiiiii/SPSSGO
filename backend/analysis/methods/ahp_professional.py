# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *
from backend.analysis.methods.ahp_simplified import _ahp_from_means

METHOD_KEY = "ahp_professional"
METHOD_META = {'label': '层次分析法（AHP专业版）',
 'category': '综合评价',
 'description': '提供判断矩阵、一致性检验和综合得分的更完整 AHP 输出',
 'order': 10,
 'slots': [{'key': 'variables', 'label': '准则指标', 'type': 'multiple', 'accept': 'numeric', 'min': 2, 'hint': '放入用于构造 AHP 权重的准则变量'}],
 'options': [],
 'param_builder': 'direct'}


def run(df, params):
    result = __import__("backend.analysis.methods.ahp_simplified", fromlist=["run"]).run(df, params)
    if not result.get("sections"):
        return result
    result["name"] = METHOD_META["label"]
    result["description"] = result["description"].replace("AHP 简化版", "AHP 专业版")
    result["sections"].insert(1, _sec_advice("当前专业版在简化版基础上补充了一致性判断和判断矩阵输出，适合形成更完整的评价报告。", "专业版说明"))
    return result
