# -*- coding: utf-8 -*-
"""AI 供应商配置服务，别把后台表单和模型调用细节揉在一起。"""
from __future__ import annotations

from backend.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL
from backend.admin.repository import get_app_settings, save_app_settings

AI_PROVIDER_DEEPSEEK = "deepseek"
AI_PROVIDER_DOUBAO = "doubao"
AI_PROVIDER_QWEN = "qwen"
AI_PROVIDER_KIMI = "kimi"
AI_PROVIDER_OPENAI = "openai"
AI_PROVIDER_GEMINI = "gemini"
AI_PROVIDER_CLAUDE = "claude"
AI_PROVIDER_GROK = "grok"
AI_PROVIDER_MISTRAL = "mistral"
AI_PROVIDER_COHERE = "cohere"
AI_PROVIDER_CUSTOM = "custom"

AI_SETTING_KEYS = {
    "provider": "ai.provider",
    "api_key": "ai.api_key",
    "base_url": "ai.base_url",
    "model": "ai.model",
}

AI_PROVIDER_DEFAULTS = {
    AI_PROVIDER_DEEPSEEK: {
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
    },
    AI_PROVIDER_DOUBAO: {
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "model": "",
    },
    AI_PROVIDER_QWEN: {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-plus",
    },
    AI_PROVIDER_KIMI: {
        "base_url": "https://api.moonshot.cn/v1",
        "model": "moonshot-v1-8k",
    },
    AI_PROVIDER_OPENAI: {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
    },
    AI_PROVIDER_GEMINI: {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "model": "gemini-2.5-flash",
    },
    AI_PROVIDER_CLAUDE: {
        "base_url": "https://api.anthropic.com/v1",
        "model": "claude-sonnet-4-20250514",
    },
    AI_PROVIDER_GROK: {
        "base_url": "https://api.x.ai/v1",
        "model": "grok-4.20-reasoning",
    },
    AI_PROVIDER_MISTRAL: {
        "base_url": "https://api.mistral.ai/v1",
        "model": "mistral-large-latest",
    },
    AI_PROVIDER_COHERE: {
        "base_url": "https://api.cohere.ai/compatibility/v1",
        "model": "command-a-03-2025",
    },
    AI_PROVIDER_CUSTOM: {
        "base_url": "",
        "model": "",
    },
}


def _normalize_provider(provider: str | None) -> str:
    value = (provider or "").strip().lower()
    if value in AI_PROVIDER_DEFAULTS:
        return value
    return AI_PROVIDER_CUSTOM


def _mask_key(api_key: str) -> str:
    if not api_key:
        return ""
    if len(api_key) <= 8:
        return "****"
    return f"{api_key[:4]}****{api_key[-4:]}"


async def get_ai_runtime_config() -> dict[str, str]:
    rows = await get_app_settings(list(AI_SETTING_KEYS.values()))
    provider = _normalize_provider(rows.get(AI_SETTING_KEYS["provider"]) or AI_PROVIDER_DEEPSEEK)
    defaults = AI_PROVIDER_DEFAULTS[provider]
    stored_api_key = rows.get(AI_SETTING_KEYS["api_key"]) or ""
    # 豆包别蹭 DeepSeek 的 key，不然排查起来很烦。
    fallback_api_key = DEEPSEEK_API_KEY if provider == AI_PROVIDER_DEEPSEEK else ""
    return {
        "provider": provider,
        "api_key": stored_api_key or fallback_api_key,
        "base_url": rows.get(AI_SETTING_KEYS["base_url"]) or defaults["base_url"] or DEEPSEEK_BASE_URL,
        "model": rows.get(AI_SETTING_KEYS["model"]) or defaults["model"] or DEEPSEEK_MODEL,
    }


async def get_ai_config_for_admin() -> dict:
    config = await get_ai_runtime_config()
    return {
        "provider": config["provider"],
        "base_url": config["base_url"],
        "model": config["model"],
        "has_api_key": bool(config["api_key"]),
        "api_key_masked": _mask_key(config["api_key"]),
        "provider_defaults": AI_PROVIDER_DEFAULTS,
    }


async def save_ai_config_for_admin(payload: dict) -> dict:
    provider = _normalize_provider(payload.get("provider"))
    base_url = str(payload.get("base_url") or "").strip()
    model = str(payload.get("model") or "").strip()
    api_key = str(payload.get("api_key") or "").strip()
    clear_api_key = bool(payload.get("clear_api_key"))

    settings = {
        AI_SETTING_KEYS["provider"]: provider,
        AI_SETTING_KEYS["base_url"]: base_url,
        AI_SETTING_KEYS["model"]: model,
    }
    if clear_api_key:
        settings[AI_SETTING_KEYS["api_key"]] = ""
    elif api_key:
        # 留空就是不改旧 key，别把用户已经保存的配置手滑清了。
        settings[AI_SETTING_KEYS["api_key"]] = api_key

    await save_app_settings(settings)
    return await get_ai_config_for_admin()
