# -*- coding: utf-8 -*-
"""从后端 METHOD_META 生成分析方法参数文档，别手写一份容易和代码跑偏的清单。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.analysis import METHOD_CATEGORIES, METHOD_META, build_execute_params  # noqa: E402
from backend.analysis.common import build_slot_param_example  # noqa: E402

OUTPUT_FILE = PROJECT_ROOT / "docs" / "ANALYSIS_METHOD_PARAMS.md"


def _json_block(value: object) -> str:
    return "```json\n" + json.dumps(value, ensure_ascii=False, indent=2) + "\n```"


def _slot_type(slot: dict) -> str:
    slot_type = slot.get("type", "single")
    accept = slot.get("accept", "any")
    min_count = slot.get("min")
    parts = ["多选" if slot_type == "multiple" else "单选"]
    if accept == "numeric":
        parts.append("定量变量")
    elif accept == "categorical":
        parts.append("定类变量")
    else:
        parts.append("任意变量")
    if min_count:
        parts.append(f"至少 {min_count} 个")
    return "，".join(parts)


def _render_slots(slots: list[dict]) -> str:
    if not slots:
        return "无变量槽位。"
    lines = ["| 参数 key | 名称 | 类型 | 说明 |", "| --- | --- | --- | --- |"]
    for slot in slots:
        lines.append(
            "| {key} | {label} | {slot_type} | {hint} |".format(
                key=slot.get("key", ""),
                label=slot.get("label", ""),
                slot_type=_slot_type(slot),
                hint=slot.get("hint", ""),
            )
        )
    return "\n".join(lines)


def _render_options(options: list[dict]) -> str:
    if not options:
        return "无额外选项。"
    lines = ["| 参数 key | 名称 | 默认值 | 可选值 | 说明 |", "| --- | --- | --- | --- | --- |"]
    for option in options:
        choices = option.get("choices") or []
        lines.append(
            "| {key} | {label} | {default} | {choices} | {hint} |".format(
                key=option.get("key", ""),
                label=option.get("label", ""),
                default=json.dumps(option.get("default", ""), ensure_ascii=False),
                choices=", ".join(str(item) for item in choices),
                hint=option.get("hint", ""),
            )
        )
    return "\n".join(lines)


def _render_method(method_key: str, meta: dict) -> str:
    slot_example = build_slot_param_example(meta)
    execute_params = build_execute_params(method_key, slot_example)
    lines = [
        f"### `{method_key}` - {meta.get('label', method_key)}",
        "",
        f"- 分类：{meta.get('category', '未分类')}",
        f"- 说明：{meta.get('description', '') or '暂无说明'}",
        f"- 参数构建器：`{meta.get('param_builder', 'direct')}`",
        "",
        "变量槽位：",
        "",
        _render_slots(meta.get("slots", [])),
        "",
        "额外选项：",
        "",
        _render_options(meta.get("options", [])),
        "",
        "前端槽位示例：",
        "",
        _json_block(slot_example),
        "",
        "`POST /api/execute-method/{session_id}` 最终 `params` 示例：",
        "",
        _json_block(execute_params),
        "",
    ]
    return "\n".join(lines)


def build_document() -> str:
    category_labels = {item["key"]: item.get("label", item["key"]) for item in METHOD_CATEGORIES}
    grouped: dict[str, list[tuple[str, dict]]] = {item["key"]: [] for item in METHOD_CATEGORIES}
    grouped.setdefault("未分类", [])
    for method_key, meta in METHOD_META.items():
        grouped.setdefault(meta.get("category", "未分类"), []).append((method_key, meta))

    lines = [
        "# 统计分析方法参数文档",
        "",
        "本文档由 `scripts/generate_analysis_method_docs.py` 根据后端 `METHOD_META` 自动生成。",
        "",
        "接口入口：",
        "",
        "```http",
        "POST /api/execute-method/{session_id}",
        "Content-Type: application/json",
        "Authorization: Bearer <access_token>",
        "```",
        "",
        "统一请求体：",
        "",
        "```json",
        "{",
        '  "method": "frequency",',
        '  "params": {}',
        "}",
        "```",
        "",
        "说明：",
        "",
        "- `method` 使用下方每个标题里的方法 key。",
        "- `params` 是后端真正执行时读取的参数结构。",
        "- “前端槽位示例”对应 `/api/methods` 返回的变量槽位；部分方法会通过参数构建器转换成最终 `params`。",
        "- 变量名必须来自 `GET /api/variables/{session_id}` 返回的变量列表。",
        "",
    ]

    total = sum(len(items) for items in grouped.values())
    lines.extend([f"当前共整理 {total} 个统计分析方法。", ""])

    for category_key, items in grouped.items():
        if not items:
            continue
        lines.extend([f"## {category_labels.get(category_key, category_key)}", ""])
        for method_key, meta in items:
            lines.append(_render_method(method_key, meta))

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(build_document(), encoding="utf-8")
    print(f"generated {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
