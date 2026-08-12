# Production LLM Wiring

## Abstraction

All models implement `llm.base.BaseLLM.complete(messages, tools=..., temperature=..., max_tokens=...) -> LLMResponse`.

| Class | Use |
|-------|-----|
| `EchoLLM` | Local tests, CI, offline |
| `OpenAIAdapter` | OpenAI API |
| `AnthropicAdapter` | Anthropic API |
| `LocalOpenAICompatibleAdapter` | Ollama, vLLM, llama.cpp server |

Factory: `llm.factory.create_llm(provider=..., model=...)`.

## Environment variables

```bash
export CODESORCERER_LLM_PROVIDER=openai   # echo | openai | anthropic | local
export OPENAI_API_KEY=sk-...
export OPENAI_MODEL=gpt-4o-mini

# or
export CODESORCERER_LLM_PROVIDER=anthropic
export ANTHROPIC_API_KEY=...
export ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# or local
export CODESORCERER_LLM_PROVIDER=local
export LOCAL_LLM_BASE_URL=http://localhost:11434/v1
export LOCAL_LLM_MODEL=llama3.2
```

## Code

```python
from llm.factory import create_llm
from swarm.runner import SwarmRunner

llm = create_llm()  # reads env
swarm = SwarmRunner(llm=llm)
result = swarm.run_sequential("Summarize the evidence trail.", context=doc_text)
print(result.synthesis)
```

## Tools

Register callables on `ToolRouter` and pass `ToolSpec` list into `complete` when the backend supports tools (OpenAI path).

## Safety note

LLM output is always **agent_intervention** when written into sessions. Only external tool/environment results update BeliefStore counts.
