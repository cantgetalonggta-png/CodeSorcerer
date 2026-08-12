"""
Production LLM wiring

Select a concrete BaseLLM from environment variables or explicit provider name.
"""

from __future__ import annotations
from typing import Optional
import os

from llm.base import BaseLLM, EchoLLM
from llm.adapters import OpenAIAdapter, AnthropicAdapter, LocalOpenAICompatibleAdapter


def create_llm(
    provider: Optional[str] = None,
    model: Optional[str] = None,
) -> BaseLLM:
    """
    provider: echo | openai | anthropic | local
    Defaults:
      CODESORCERER_LLM_PROVIDER or echo
      model-specific env overrides
    """
    provider = (provider or os.getenv("CODESORCERER_LLM_PROVIDER") or "echo").lower().strip()

    if provider == "echo":
        return EchoLLM()

    if provider == "openai":
        return OpenAIAdapter(model=model or os.getenv("OPENAI_MODEL", "gpt-4o-mini"))

    if provider == "anthropic":
        return AnthropicAdapter(
            model=model or os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        )

    if provider == "local":
        return LocalOpenAICompatibleAdapter(
            base_url=os.getenv("LOCAL_LLM_BASE_URL", "http://localhost:11434/v1"),
            model=model or os.getenv("LOCAL_LLM_MODEL", "llama3.2"),
            api_key=os.getenv("LOCAL_LLM_API_KEY", "local"),
        )

    # Fallback
    return EchoLLM()
