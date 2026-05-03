# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *
from backend.analysis.methods.anova_oneway import run as anova_run

METHOD_KEY = "summary_oneway_anova"
METHOD_META = {'label': '摘要单因素方差分析',
 'category': '差异对比分析包',
 'description': '以简化摘要形式呈现单因素方差分析核心结果',
 'order': 55,
 'slots': [{'key': 'group_var', 'label': '分组变量', 'type': 'single', 'accept': 'categorical', 'hint': '放入分组变量'},
           {'key': 'test_vars', 'label': '检验变量', 'type': 'multiple', 'accept': 'numeric', 'min': 1, 'hint': '放入检验变量'}],
 'options': [{'key': 'post_hoc', 'label': '事后比较', 'choices': ['LSD', 'Bonferroni', 'Tukey'], 'default': 'Bonferroni'}],
 'param_builder': 'anova'}


def run(df, params):
    result = anova_run(df, params)
    if isinstance(result, dict):
        result["name"] = METHOD_META["label"]
    return result
