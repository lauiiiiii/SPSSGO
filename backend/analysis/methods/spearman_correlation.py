# -*- coding: utf-8 -*-
# Spearman 单独入口只做快捷分发，统计口径跟相关性分析里的 Spearman 保持一致。
from backend.analysis.methods.pearson_correlation import pearson_correlation

METHOD_KEY = "spearman_correlation"
METHOD_META = {
    "label": "Spearman 等级相关",
    "category": "数据检验",
    "description": "分析两个或多个变量之间的等级相关程度（非参数）",
    "slots": [
        {
            "key": "variables",
            "label": "分析变量",
            "type": "multiple",
            "accept": "numeric",
            "min": 2,
            "hint": "放入需要分析相关性的变量（至少2个）",
        }
    ],
    "options": [],
    "param_builder": "direct",
}


def spearman_correlation(df, params):
    """
    固定使用相关性分析中的 Spearman 口径。

    @param df: 数据 DataFrame
    @param params: 包含 variables 的参数字典
    @return: 含 sections 的结果字典
    """
    next_params = dict(params or {})
    next_params["correlation_method"] = "Spearman相关系数"
    result = pearson_correlation(df, next_params)
    result["name"] = METHOD_META["label"]
    return result


run = spearman_correlation
