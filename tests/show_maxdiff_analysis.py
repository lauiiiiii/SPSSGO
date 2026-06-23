# -*- coding: utf-8 -*-
"""展示 MaxDiff 专业分析结果"""
import pandas as pd
import numpy as np
import sys
sys.path.insert(0, ".")

from backend.analysis.methods import maxdiff

np.random.seed(42)

ATTRIBUTES = ["价格", "电池", "拍照", "系统", "屏幕", "品牌", "外观", "存储"]
TRUE_PREFERENCES = {
    "价格": 0.25, "电池": 0.20, "拍照": 0.18, "系统": 0.12,
    "屏幕": 0.10, "品牌": 0.07, "外观": 0.05, "存储": 0.03,
}

# 生成模拟数据
records = []
for r in range(1, 101):
    for t in range(1, 6):
        shown_attrs = np.random.choice(ATTRIBUTES, size=4, replace=False)
        probs = np.array([TRUE_PREFERENCES[attr] for attr in shown_attrs])
        probs = probs / probs.sum()
        best_idx = np.random.choice(len(shown_attrs), p=probs)
        best_choice = shown_attrs[best_idx]
        worst_probs = 1 - probs
        worst_probs = worst_probs / worst_probs.sum()
        worst_idx = np.random.choice(len(shown_attrs), p=worst_probs)
        worst_choice = shown_attrs[worst_idx]
        while worst_choice == best_choice:
            worst_idx = np.random.choice(len(shown_attrs), p=worst_probs)
            worst_choice = shown_attrs[worst_idx]
        record = {"respondent": f"R{r:03d}-T{t}", "best_choice": best_choice, "worst_choice": worst_choice}
        for attr in ATTRIBUTES:
            record[attr] = attr
        records.append(record)

df = pd.DataFrame(records)

# 运行分析
result = maxdiff.run(
    df,
    {
        "best_variable": "best_choice",
        "worst_variable": "worst_choice",
        "option_variables": ATTRIBUTES,
    },
)

# 展示结果分析
print("=" * 80)
print("MaxDiff 专业分析结果展示")
print("=" * 80)

for section in result["sections"]:
    if section["type"] == "advice":
        print(f"\n【{section['title']}】\n")
        print(section["content"])
        break

print("\n" + "=" * 80)
