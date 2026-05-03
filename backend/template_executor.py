# -*- coding: utf-8 -*-
"""
模板执行器：接收 JSON 分析配置列表，调度内置分析函数，收集结果
"""
import json
import pandas as pd
from backend.analysis import METHOD_REGISTRY, build_available_methods_prompt


def execute_template_tasks(df: pd.DataFrame, tasks: list[dict]) -> dict:
    """
    执行分析任务列表

    Args:
        df: 已加载的 DataFrame
        tasks: [{"method": "descriptive", "variables": [...], ...}, ...]

    Returns:
        {"success": True/False, "results": [...], "error": "..."}
    """
    results = []
    errors = []

    for i, task in enumerate(tasks):
        method_name = task.get("method", "")
        func = METHOD_REGISTRY.get(method_name)

        if func is None:
            errors.append(f"任务{i+1}：未知分析方法 '{method_name}'")
            continue

        try:
            result = func(df, task)
            if isinstance(result, list):
                results.extend(result)
            elif isinstance(result, dict):
                results.append(result)
        except Exception as e:
            errors.append(f"任务{i+1}（{method_name}）执行出错：{str(e)}")

    if results:
        return {
            "success": True,
            "results": results,
            "error": "; ".join(errors) if errors else "",
        }
    else:
        return {
            "success": False,
            "results": [],
            "error": "; ".join(errors) if errors else "所有分析任务均未产生结果",
        }


def parse_ai_tasks(ai_response: str) -> list[dict]:
    """
    从 AI 返回的文本中提取 JSON 任务列表
    支持：纯 JSON / ```json ... ``` 包裹 / 混合文本
    """
    text = ai_response.strip()

    if "```json" in text:
        text = text.split("```json", 1)[1]
        if "```" in text:
            text = text.split("```", 1)[0]
    elif "```" in text:
        text = text.split("```", 1)[1]
        if "```" in text:
            text = text.split("```", 1)[0]

    text = text.strip()

    if not text.startswith("["):
        start = text.find("[")
        if start >= 0:
            end = text.rfind("]")
            if end > start:
                text = text[start:end+1]

    try:
        tasks = json.loads(text)
        if isinstance(tasks, list):
            return tasks
        if isinstance(tasks, dict):
            return [tasks]
    except json.JSONDecodeError:
        pass

    return []


def get_available_methods() -> str:
    """返回可用方法列表，供 AI prompt 使用"""
    return build_available_methods_prompt()

