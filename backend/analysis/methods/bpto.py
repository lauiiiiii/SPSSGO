# -*- coding: utf-8 -*-
# spssgo
from backend.analysis.common import *

METHOD_KEY = "bpto"
METHOD_META = {'label': '品牌价格抵补模型BPTO',
 'category': '高级问卷分析包',
 'description': '评估品牌优势是否足以抵补价格劣势',
 'order': 210,
 'slots': [{'key': 'choice_var',
            'label': '选择结果',
            'type': 'single',
            'accept': 'categorical',
            'hint': '放入选择结果变量'},
           {'key': 'brand_var',
            'label': '品牌变量',
            'type': 'single',
            'accept': 'categorical',
            'hint': '放入品牌变量'},
           {'key': 'price_var',
            'label': '价格变量',
            'type': 'single',
            'accept': 'numeric',
            'hint': '放入价格变量'}],
 'options': [],
 'param_builder': 'direct'}


def run(df, params):
    choice_var = params.get("choice_var", "")
    brand_var = params.get("brand_var", "")
    price_var = params.get("price_var", "")
    for variable in [choice_var, brand_var, price_var]:
        if variable not in df.columns:
            return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": f"变量 {variable} 不存在。"}

    temp = df[[choice_var, brand_var, price_var]].copy()
    temp[price_var] = pd.to_numeric(temp[price_var], errors="coerce")
    temp = temp.dropna()
    if len(temp) < 8:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效样本不足。"}

    chosen = _selected_mask(temp[choice_var])
    overall_price = float(temp[price_var].mean())
    rows = []
    for brand, group in temp.groupby(brand_var):
        choose_rate = chosen.loc[group.index].mean() * 100
        avg_price = float(group[price_var].mean())
        premium = avg_price - overall_price
        compensate = choose_rate - premium
        rows.append([str(brand), _fmt(avg_price, 2), _fmt(premium, 2), f"{_fmt(choose_rate, 1)}%", _fmt(compensate, 2)])
    rows.sort(key=lambda row: float(row[4]), reverse=True)

    sections = [
        _sec_table("品牌价格抵补结果", ["品牌", "平均价格", "相对溢价", "选择率", "抵补指数"], rows, description="抵补指数采用“选择率 - 相对溢价”的简化近似，用于快速识别品牌优势是否足以覆盖价格劣势。"),
        _sec_advice("当前版本提供的是 BPTO 的简化判读视图。"),
        _sec_smart(f"BPTO 分析完成，当前抵补指数最高的品牌为 {rows[0][0]}。"),
        _sec_refs(_REFS_GENERAL),
    ]
    return {"name": METHOD_META["label"], "headers": ["品牌", "平均价格", "相对溢价", "选择率", "抵补指数"], "rows": rows, "description": f"BPTO 分析完成，共比较 {len(rows)} 个品牌。", "sections": sections}
