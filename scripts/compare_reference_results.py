# -*- coding: utf-8 -*-
"""
专业软件参考结果比对脚本

用法：
    python scripts/compare_reference_results.py

默认扫描 acceptance_refs/**/*.json，并输出逐文件比对摘要。
当前脚本先提供统一比对骨架，后续可以按方法继续扩展本地指标提取逻辑。
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


DEFAULT_TOLERANCES = {
    "SPSS": 1e-4,
    "PROCESS": 1e-4,
    "AMOS": 1e-3,
    "SmartPLS": 1e-3,
}


def load_references(root: Path):
    return sorted(root.glob("**/*_reference.json"))


def compare_metrics(reference_metrics: dict, actual_metrics: dict, tolerance: float):
    rows = []
    passed = 0
    missing = 0
    for key, expected in sorted(reference_metrics.items()):
        actual = actual_metrics.get(key)
        if actual is None:
            rows.append((key, expected, None, "missing", None))
            missing += 1
            continue
        try:
            expected_float = float(expected)
            actual_float = float(actual)
            diff = abs(actual_float - expected_float)
            status = "pass" if diff <= tolerance else "fail"
            if status == "pass":
                passed += 1
            rows.append((key, expected_float, actual_float, status, diff))
        except (TypeError, ValueError):
            status = "pass" if str(expected) == str(actual) else "fail"
            if status == "pass":
                passed += 1
            rows.append((key, expected, actual, status, None))
    return rows, passed, missing


def main():
    ref_root = ROOT / "acceptance_refs"
    files = load_references(ref_root)
    if not files:
        print("no reference files found")
        return

    print("reference comparison scaffold")
    print(f"found {len(files)} reference files")
    print()

    for path in files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        method_key = payload.get("method_key", "")
        tool = payload.get("tool", "")
        version = payload.get("version", "")
        reference_metrics = payload.get("metrics", {}) or {}
        tolerance = DEFAULT_TOLERANCES.get(tool, 1e-3)

        # 当前阶段只输出“待接入实际指标提取”的验收外壳。
        actual_metrics = payload.get("actual_metrics_placeholder", {})
        rows, passed, missing = compare_metrics(reference_metrics, actual_metrics, tolerance)
        total = len(rows)
        failed = len([row for row in rows if row[3] == "fail"])

        print(f"[{tool} {version}] {method_key} -> {path.relative_to(ROOT)}")
        print(f"  metrics: {total}, passed: {passed}, failed: {failed}, missing: {missing}, tolerance: {tolerance}")
        if failed or missing:
            for key, expected, actual, status, diff in rows[:10]:
                if status == "pass":
                    continue
                if diff is None or (isinstance(diff, float) and math.isnan(diff)):
                    print(f"    - {key}: expected={expected}, actual={actual}, status={status}")
                else:
                    print(f"    - {key}: expected={expected}, actual={actual}, diff={diff}, status={status}")
        print()

    print("done")
    print("note: this scaffold is ready for per-method actual-metric extraction wiring.")


if __name__ == "__main__":
    main()
