# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *
from backend.analysis.methods.two_way_anova import _factorial_anova

METHOD_KEY = "three_way_anova"
METHOD_META = {'label': '三因素方差分析',
 'category': '差异对比分析包',
 'description': '检验三个分类因素及其交互作用对因变量的影响',
 'order': 45,
 'slots': [{'key': 'factor1', 'label': '因素1', 'type': 'single', 'accept': 'categorical', 'hint': '放入第一个因素'},
           {'key': 'factor2', 'label': '因素2', 'type': 'single', 'accept': 'categorical', 'hint': '放入第二个因素'},
           {'key': 'factor3', 'label': '因素3', 'type': 'single', 'accept': 'categorical', 'hint': '放入第三个因素'},
           {'key': 'dependent', 'label': '因变量', 'type': 'single', 'accept': 'numeric', 'hint': '放入因变量'}],
 'options': [],
 'param_builder': 'direct'}


def run(df, params):
    return _factorial_anova(df, [params.get("factor1", ""), params.get("factor2", ""), params.get("factor3", "")], params.get("dependent", ""), METHOD_META["label"])
