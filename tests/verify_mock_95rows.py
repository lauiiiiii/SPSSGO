# -*- coding: utf-8 -*-
"""快速验证 95 行 mock 数据的灰色关联分析输出，确认 previewLimit 和 exportRows 正确。"""
import os
import pandas as pd
from backend.analysis.methods import grey_relational_analysis

CSV_PATH = os.path.join(os.path.dirname(__file__), "mock_grey_relational_95rows.csv")

df = pd.read_csv(CSV_PATH)
print(f"数据集行数: {len(df)}")
print(f"列: {list(df.columns)}")

result = grey_relational_analysis.run(
    df,
    {
        "feature_vars": ["q2", "q3"],
        "mother_var": ["q4"],
        "index_var": ["name"],
        "dimensionless_method": "mean",
        "rho": 0.5,
    },
)

# 找关联系数表
coeff_table = next(s for s in result["sections"] if s["title"] == "输出结果1：灰色关联系数")

print(f"\n关联系数表 headers: {coeff_table['headers']}")
print(f"预览行数: {len(coeff_table['rows'])}")
print(f"previewLimit: {coeff_table.get('previewLimit', '未设置')}")
print(f"exportRows 行数: {len(coeff_table.get('exportRows', []))}")
print(f"note: {coeff_table.get('note', '无')}")

# 找关联系数图
coeff_chart_section = next(s for s in result["sections"] if s["title"] == "输出结果2：关联系数图")
coeff_chart = coeff_chart_section["charts"][0]
print(f"\n关联系数图标题: {coeff_chart['title']}")
print(f"multiSeries: {coeff_chart['data'].get('multiSeries', '未设置')}")
print(f"yRange: {coeff_chart['data'].get('yRange', '未设置')}")
print(f"特征序列数: {len(coeff_chart['data'].get('metrics', {}))}")

# 找排序图
chart_section = next(s for s in result["sections"] if s["title"] == "输出结果4：灰色关联度排序图")
chart = chart_section["charts"][0]
print(f"\n排序图标题: {chart['title']}")
print(f"yRange: {chart['data'].get('yRange', '未设置')}")

# 关联度结果
grade_table = next(s for s in result["sections"] if s["title"] == "输出结果3：灰色关联度结果")
print(f"\n关联度结果:")
for row in grade_table["rows"]:
    print(f"  {row[0]}: 关联度={row[1]}, 排名={row[2]}")
