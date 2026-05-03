# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *
from backend.analysis.methods.two_way_anova import _factorial_anova

METHOD_KEY = "n_way_anova"
METHOD_META = {'label': '多因素方差分析',
 'category': '差异对比分析包',
 'description': '检验多个分类因素及其交互作用对因变量的影响',
 'order': 50,
 'slots': [{'key': 'factors', 'label': '因素变量', 'type': 'multiple', 'accept': 'categorical', 'min': 2, 'hint': '放入多个因素变量'},
           {'key': 'dependent', 'label': '因变量', 'type': 'single', 'accept': 'numeric', 'hint': '放入因变量'}],
 'options': [],
 'param_builder': 'direct'}


def run(df, params):
    factors = _resolve_cols(df, params.get("factors", []))
    return _factorial_anova(df, factors, params.get("dependent", ""), METHOD_META["label"])
