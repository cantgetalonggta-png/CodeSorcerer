"""
Thin adapters behind BaseLLM.

These are intentionally minimal. They exist so the rest of the system
can call a uniform interface while you plug in real credentials / clients.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
import json
import os

from llm.base import BaseLLM, Message, LLMResponse, ToolSpec


class OpenAIAdapter(BaseLLM):
    """
    Minimal OpenAI-compatible adapter.
    Requires `openai` package and OPENAI_API_KEY.
    """

    def __init__(self, model: str = "gpt-4o-mini", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except Exception as e:
            self.client = None
            self._init_error = str(e)

    def complete(
        self,
        messages: List[Message],
        tools: Optional[List[ToolSpec]] = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        if self.client is None:
            return LLMResponse(content=f"[OpenAIAdapter unavailable: {getattr(self, '_init_error', 'no client')}]")

        oai_messages = [{"role": m.role, "content": m.content} for m in messages]
        kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": oai_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if tools:
            kwargs["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.parameters or {"type": "object", "properties": {}},
                    },
                }
                for t in tools
            ]

        resp = self.client.chat.completions.create(**kwargs)
        choice = resp.choices[0].message
        tool_calls = []
        if getattr(choice, "tool_calls", None):
            for tc in choice.tool_calls:
                tool_calls.append({
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                })
        return LLMResponse(content=choice.content or "", tool_calls=tool_calls, raw=resp)


class AnthropicAdapter(BaseLLM):
    """
    Minimal Anthropic adapter.
    Requires `anthropic` package and ANTHROPIC_API_KEY.
    """

    def __init__(self, model: str = "claude-3-5-sonnet-20241022", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
        except Exception as e:
            self.client = None
            self._init_error = str(e)

    def complete(
        self,
        messages: List[Message],
        tools: Optional[List[ToolSpec]] = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        if self.client is None:
            return LLMResponse(content=f"[AnthropicAdapter unavailable: {getattr(self, '_init_error', 'no client')}]")

        # Anthropic wants system as a separate field
        system = ""
        oai_style = []
        for m in messages:
            if m.role == "system":
                system += m.content + "\n"
            else:
                oai_style.append({"role": m.role if m.role != "tool" else "user", "content": m.content})

        resp = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system.strip() or "You are a helpful assistant.",
            messages=oai_style,
        )
        text = ""
        for block in resp.content:
            if hasattr(block, "text"):
                text += block.text
        return LLMResponse(content=text, tool_calls=[], raw=resp)


class LocalOpenAICompatibleAdapter(BaseLLM):
    """
    Adapter for any OpenAI-compatible local server (vLLM, Ollama, llama.cpp server, etc.).
    """

    def __init__(self, base_url: str = "http://localhost:11434/v1", model: str = "llama3.2", api_key: str = "local"):
        self.base_url = base_url
        self.model = model
        self.api_key = api_key
        try:
            from openai import OpenAI
            self.client = OpenAI(base_url=base_url, api_key=api_key)
        except Exception as e:
            self.client = None
            self._init_error = str(e)

    def complete(
        self,
        messages: List[Message],
        tools: Optional[List[ToolSpec]] = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        if self.client is None:
            return LLMResponse(content=f"[LocalAdapter unavailable: {getattr(self, '_init_error', 'no client')}]")

        oai_messages = [{"role": m.role, "content": m.content} for m in messages]
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=oai_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        choice = resp.choices[0].message
        return LLMResponse(content=choice.content or "", tool_calls=[], raw=resp)
