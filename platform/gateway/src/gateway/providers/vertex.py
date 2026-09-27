"""Vertex AI / Gemini LLM provider configuration for LiteLLM."""
from __future__ import annotations

import os
from typing import Any

import litellm


def get_litellm_config() -> dict[str, Any]:
    """Return LiteLLM configuration for Vertex AI."""
    return {
        "model": os.getenv("LLM_MODEL", "vertex_ai/gemini-1.5-pro"),
        "vertex_project": os.getenv("VERTEX_AI_PROJECT", ""),
        "vertex_location": os.getenv("VERTEX_AI_LOCATION", "us-central1"),
        "temperature": float(os.getenv("LLM_TEMPERATURE", "0.0")),
        "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "8192")),
    }


async def call_llm(
    prompt: str,
    system: str = "",
    **kwargs: Any,
) -> str:
    """Call the configured LLM with the given prompt."""
    config = get_litellm_config()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = await litellm.acompletion(
        model=config["model"],
        messages=messages,
        temperature=config["temperature"],
        max_tokens=config["max_tokens"],
        vertex_project=config.get("vertex_project"),
        vertex_location=config.get("vertex_location"),
        **kwargs,
    )
    return response.choices[0].message.content or ""
