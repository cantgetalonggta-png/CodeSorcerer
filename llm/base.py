"""
LLM integration point

Provides a minimal, swappable interface for a concrete base model
and tool calling. Designed so the rest of CodeSorcerer stays
independent of any particular provider.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class ToolSpec:
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)  # JSON-schema style


@dataclass
class Message:
    role: str          # system | user | assistant | tool
    content: str
    tool_call_id: Optional[str] = None
    name: Optional[str] = None


@dataclass
class LLMResponse:
    content: str
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    raw: Any = None


class BaseLLM(ABC):
    """Abstract base for any concrete LLM backend."""

    @abstractmethod
    def complete(
        self,
        messages: List[Message],
        tools: Optional[List[ToolSpec]] = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        ...


class EchoLLM(BaseLLM):
    """
    Deterministic placeholder LLM for testing and local development.
    Echoes the last user message and can emit a fake tool call if asked.
    """

    def complete(
        self,
        messages: List[Message],
        tools: Optional[List[ToolSpec]] = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        last_user = ""
        for m in reversed(messages):
            if m.role == "user":
                last_user = m.content
                break
        content = f"[EchoLLM] Received: {last_user[:200]}"
        tool_calls = []
        if tools and "tool" in last_user.lower():
            tool_calls.append({
                "id": "call_echo_1",
                "type": "function",
                "function": {"name": tools[0].name, "arguments": "{}"},
            })
        return LLMResponse(content=content, tool_calls=tool_calls, raw=None)


class ToolRouter:
    """Simple name → callable router for tool execution."""

    def __init__(self):
        self._tools: Dict[str, Callable[..., Any]] = {}

    def register(self, name: str, fn: Callable[..., Any]) -> None:
        self._tools[name] = fn

    def call(self, name: str, arguments: Dict[str, Any]) -> Any:
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        return self._tools[name](**arguments)

    def specs(self) -> List[ToolSpec]:
        return [ToolSpec(name=n, description=f"Tool {n}") for n in self._tools]
