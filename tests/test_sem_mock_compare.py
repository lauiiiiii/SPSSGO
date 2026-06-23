# -*- coding: utf-8 -*-
"""SEM mock data test -- compare with SPSSPRO output.
   Generate 3-factor 11-variable data with realistic factor structure
   and a collinear pair ("happy"/"satisfied") to validate the new logic.
"""

import json
import sys
import os

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "backend"))

import numpy as np
import pandas as pd

from backend.analysis.methods import sem

np.random.seed(123)
N = 300

# ── Generate data with realistic SEM factor structure ──
# Latent factors (standardized)
F1 = np.random.normal(0, 1, N)   # factor 1: basic needs
F2 = np.random.normal(0, 1, N)   # factor 2: school resources
F3 = 0.45 * F1 + 0.55 * F2 + np.random.normal(0, 0.5, N)  # factor 3 depends on F1 & F2

# Observed variables = factor loadings + noise, scaled to 1-5 Likert
def scale_likert(x):
    return np.round(np.clip(x * 0.8 + 3, 1, 5)).astype(int)

衣   = scale_likert(0.70 * F1 + np.random.normal(0, 0.55, N))
食   = scale_likert(0.55 * F1 + np.random.normal(0, 0.65, N))
住   = scale_likert(0.80 * F1 + np.random.normal(0, 0.45, N))
行   = scale_likert(0.65 * F1 + np.random.normal(0, 0.60, N))

学校资源 = scale_likert(0.75 * F2 + np.random.normal(0, 0.50, N))
补课程度 = scale_likert(0.35 * F2 + np.random.normal(0, 0.80, N))
父母关心 = scale_likert(0.60 * F2 + np.random.normal(0, 0.60, N))
同学相处 = scale_likert(0.50 * F2 + np.random.normal(0, 0.70, N))

老师指导 = scale_likert(0.65 * F3 + np.random.normal(0, 0.60, N))
# 快乐感 and 满足感: nearly identical — only 1/300 row differs by 1 pt
快乐感   = scale_likert(0.70 * F3 + np.random.normal(0, 0.50, N))
满足感   = 快乐感.copy()
满足感[0] = np.clip(快乐感[0] + np.random.choice([-1, 1]), 1, 5).astype(int)

df = pd.DataFrame({
    "衣": 衣, "食": 食, "住": 住, "行": 行,
    "学校资源": 学校资源, "补课程度": 补课程度, "父母关心": 父母关心, "同学相处": 同学相处,
    "老师指导": 老师指导, "快乐感": 快乐感, "满足感": 满足感,
})

corr = df[["快乐感", "满足感"]].corr().iloc[0, 1]
print(f"[collinearity] happy <-> satisfied r = {corr:.4f}  (|r| >= 0.999: {abs(corr) >= 0.999})")
print(f"[sample] N = {len(df)}, 11 vars")

params = {
    "factor1_vars": ["衣", "食", "住", "行"],
    "factor2_vars": ["学校资源", "补课程度", "父母关心", "同学相处"],
    "factor3_vars": ["老师指导", "快乐感", "满足感"],
    "factor_labels": {"F1": "因子1", "F2": "因子2", "F3": "因子3"},
    "structural_paths": [
        {"dependent": "F3", "predictors": ["F1", "F2"]}
    ],
}

print("\n" + "=" * 60)
print("Calling sem.run(df, params) ...")
print("=" * 60)

try:
    result = sem.run(df, params)
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print(f"\nname: {result.get('name')}")
print(f"description: {result.get('description')}")

sections = result.get("sections", [])
more_sections = result.get("more_sections", [])

print(f"\n--- Main sections ({len(sections)}) ---")
for sec in sections:
    stype = sec.get("type", "?")
    title = sec.get("title", "")
    note = sec.get("note", "")
    content = sec.get("content", "")
    headers = sec.get("headers", [])
    rows = sec.get("rows", [])
    if stype == "text":
        print(f"  [{stype}] {title}")
        print(f"    {content[:200]}")
    elif stype == "table":
        print(f"  [{stype}] {title} | {headers}  (rows={len(rows)})")
        for row in rows[:5]:
            print(f"    {row}")
        if len(rows) > 5:
            print(f"    ... ({len(rows)} rows total)")
    elif stype == "model_path":
        chart = sec.get("chart", {})
        print(f"  [{stype}] {title} | nodes={len(chart.get('nodes',[]))} edges={len(chart.get('edges',[]))}")
    else:
        print(f"  [{stype}] {title}")
    if note:
        print(f"    NOTE: {note[:150]}")

print(f"\n--- More sections ({len(more_sections)}) ---")
for sec in more_sections:
    title = sec.get("title", "")
    headers = sec.get("headers", [])
    rows = sec.get("rows", [])
    print(f"  [table] {title} | {headers}  (rows={len(rows)})")

had_dropped = any("剔除" in (s.get("content", "") + s.get("note", "")) for s in sections)
print(f"\n{'='*60}")
print(f"Autoclean triggered: {had_dropped}")
print(f"Total vars in model: {len(result.get('rows', []))} rows")
print("Done.")
