# -*- coding: utf-8 -*-
"""
AI 分析引擎：对接 DeepSeek API
- 阶段1：生成分析计划（文字）
- 阶段2：生成 JSON 分析任务配置（优先模板） / 降级为 Python 代码
"""
import httpx
import json
from backend.services.ai_settings_service import get_ai_runtime_config
from backend.template_executor import get_available_methods

SYSTEM_PROMPT_PLAN = """你是一位专业的 SPSS 数据分析专家。用户会提供数据集结构、问卷内容、研究假设。
请根据信息，生成一份详细的数据分析计划，用编号列表格式，每项包含：分析名称、分析方法、涉及的变量。"""

SYSTEM_PROMPT_TASK = """你是一位数据分析专家。你需要根据用户的分析计划，输出一个 JSON 数组，每个元素是一个分析任务。

## 重要规则
1. 只输出 JSON 数组，不要有其他文字说明
2. 变量名必须与数据集中的列名完全一致（区分大小写）
3. method 字段必须是下方列表中的有效值
4. 如果某个分析需求无法用下列方法覆盖，设 method 为 "custom"，并在 "custom_desc" 字段描述需求

{methods}

## 输出格式示例
```json
[
  {{"method": "descriptive", "variables": ["社会支持", "自我效能感", "就业焦虑"]}},
  {{"method": "independent_t_test", "group_var": "q1", "dependent": ["就业焦虑"], "group_labels": {{"1": "男", "2": "女"}}}},
  {{"method": "pearson_correlation", "variables": ["社会支持", "自我效能感", "就业焦虑"]}}
]
```
"""

SYSTEM_PROMPT_CODE = """你是一位专业的 SPSS 数据分析专家。用户需要你编写 Python 代码来完成一项自定义分析。

代码规范：
- 数据已加载为 df（pandas DataFrame），无需再 read_excel
- 可用库：pandas, numpy, scipy, statsmodels, pingouin, factor_analyzer
- 将每项分析结果追加到 RESULT 列表，格式为：
  RESULT.append({
      "name": "分析名称",
      "headers": ["列1", "列2", ...],
      "rows": [["值1", "值2", ...], ...],
      "description": "学术风格的文字描述，包含具体统计量。"
  })
- 数值保留3位小数，p值用 <0.001/<0.01/<0.05 表示
- 文字描述用规范的学术中文撰写
- 不要使用 print()，不要使用 open()，不要 import os/sys
- 只输出 Python 代码块，不要其他说明文字
"""


async def call_deepseek(messages: list[dict], temperature=0.3, max_tokens=4000) -> str:
    ai_config = await get_ai_runtime_config()
    if not ai_config["api_key"]:
        raise RuntimeError("缺少 AI API Key，请在管理员后台或项目根目录 .env 中配置")

    headers = {
        "Authorization": f"Bearer {ai_config['api_key']}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": ai_config["model"],
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            f"{ai_config['base_url'].rstrip('/')}/chat/completions",
            headers=headers,
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


async def generate_plan(data_context: str, research_topic: str, variable_desc: str,
                        hypotheses: str, analysis_request: str) -> str:
    user_msg = f"""请根据以下信息，生成一份详细的数据分析计划。

## 研究主题
{research_topic}

## 变量说明
{variable_desc}

## 研究假设
{hypotheses}

## 用户要求的分析
{analysis_request if analysis_request else "请根据研究假设自动决定需要哪些分析。"}

## 数据结构
{data_context}

请输出分析计划，用编号列表格式，每项包含：分析名称、分析方法、涉及的变量。
"""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_PLAN},
        {"role": "user", "content": user_msg},
    ]
    return await call_deepseek(messages, max_tokens=4000)


async def generate_tasks_json(data_context: str, plan: str, research_info: str) -> str:
    """根据确认的计划，生成 JSON 分析任务配置"""
    methods_doc = get_available_methods()
    system = SYSTEM_PROMPT_TASK.format(methods=methods_doc)

    user_msg = f"""请根据以下分析计划，输出 JSON 分析任务数组。

## 研究背景
{research_info}

## 数据结构
{data_context}

## 分析计划
{plan}

请直接输出 JSON 数组。
"""
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_msg},
    ]
    return await call_deepseek(messages, temperature=0.1, max_tokens=4000)


async def generate_code(data_context: str, plan: str, research_info: str,
                        error_feedback: str = "") -> str:
    """降级方案：生成可执行 Python 代码（用于 custom 任务或模板失败时）"""
    user_msg = f"""请根据以下分析需求，生成完整的 Python 分析代码。

## 研究背景
{research_info}

## 数据结构
{data_context}

## 分析需求
{plan}

"""
    if error_feedback:
        user_msg += f"""## 上次执行报错
{error_feedback}

请修复代码中的错误，重新生成完整代码。
"""
    user_msg += """
## 重要要求
1. df 已经加载好了，不要再 read_excel
2. 每项分析结果必须 RESULT.append({ "name": ..., "headers": [...], "rows": [[...], ...], "description": "..." })
3. 数值格式化为字符串保留3位小数
4. description 用规范学术中文撰写，包含具体统计量（如 t=x.xx, p<0.05）
5. 只输出 Python 代码块，不要其他说明文字
"""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_CODE},
        {"role": "user", "content": user_msg},
    ]
    response = await call_deepseek(messages, max_tokens=8000)

    code = response
    if "```python" in code:
        code = code.split("```python", 1)[1]
        if "```" in code:
            code = code.split("```", 1)[0]
    elif "```" in code:
        code = code.split("```", 1)[1]
        if "```" in code:
            code = code.split("```", 1)[0]

    return code.strip()

