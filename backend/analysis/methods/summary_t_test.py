# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *
from backend.analysis.methods.independent_t_test import run as indep_t_run

METHOD_KEY = "summary_t_test"
METHOD_META = {'label': '摘要T检验',
 'category': '差异对比分析包',
 'description': '以简化摘要形式呈现T检验核心结果',
 'order': 20,
 'slots': [{'key': 'group_var', 'label': '分组变量', 'type': 'single', 'accept': 'categorical', 'hint': '放入二分类分组变量'},
           {'key': 'test_vars', 'label': '检验变量', 'type': 'multiple', 'accept': 'numeric', 'min': 1, 'hint': '放入检验变量'}],
 'options': [],
 'param_builder': 't_test'}


def run(df, params):
    result = indep_t_run(df, params)
    if isinstance(result, dict):
        result["name"] = METHOD_META["label"]
    return result
