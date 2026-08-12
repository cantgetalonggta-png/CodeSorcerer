# CodeSorcerer

**Custom Agent Framework & Persistent Workspace — Orchestrated by Grok**

A production-oriented **Bayesian autonomous agent** system. The agent improves its own skills, memory, policy, and learning dynamics under **causal** (interventional) updates and **anytime-valid statistical certificates**. Every live change to the agent’s state is gated; self-delusion is structurally prevented.

---

## Core Principles

1. **Frozen base model + mutable harness**
2. **Interventional discipline** — only external observations update posteriors
3. **Anytime-valid certificates** — GRO e-process + harmonic spending
4. **Soft canary → hard commit** — empirical second lock
5. **Auditability** — certificates and replay

---

## Architecture

```
L3  Gates (GRO + conformal + canary)
L2  Harness (skills, policy, memory refs)
L1  Swarm agents + skill packs
L0  BaseLLM (echo / OpenAI / Anthropic / local)
```

**Bayesian inference stack** (`bayesian_core/inference_layers.py`):

| Layer | Name | Role |
|-------|------|------|
| 0 | Conjugate BeliefStore | Fast Beta counts |
| 1 | Hierarchical NumPyro | Population + per-entity posteriors |
| 2 | Conformal | Distribution-free intervals |
| 3 | GRO e-process | Anytime-valid commit gate |
| 4 | Canary | Live empirical promotion check |

Docs: `architecture/bayesian_canary_safety.md`, `architecture/production_llm_wiring.md`, `architecture/drive_inventory.md`.

---

## Swarm multi-agent layer (`swarm/`)

Roles (Drive-aligned, safety-constrained):

- **MemoryVault** — tagged durable memory
- **PatternRecognition** — entity/timeline patterns with evidence
- **SourceAnalyst** — source grading + citations + contradictions
- **DocumentForensics** — PDF/text digests
- **QueryPlanner** — public query string builder only
- **ComplianceGate** — interventional discipline
- **Synthesizer** — final structured merge

```python
from llm.factory import create_llm
from swarm import SwarmRunner, get_roster

llm = create_llm()  # CODESORCERER_LLM_PROVIDER=openai|anthropic|local|echo
swarm = SwarmRunner(llm=llm, roster=get_roster())
result = swarm.run_sequential(task, context=doc_text)
# or result = swarm.run_parallel(task, context=doc_text)
print(result.synthesis)
```

Demo: `python -m examples.swarm_demo`

---

## Production LLM wiring

| Piece | Path |
|-------|------|
| Abstraction | `llm/base.py` (`BaseLLM`) |
| Adapters | `llm/adapters.py` |
| Factory | `llm/factory.py` → `create_llm()` |
| Guide | `architecture/production_llm_wiring.md` |

Env: `CODESORCERER_LLM_PROVIDER`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `LOCAL_LLM_BASE_URL`, etc.

---

## Evaluators

- `KeywordMatchEvaluator`, `ThresholdSuccessEvaluator` — `core/evaluator.py`
- `LengthPenaltyEvaluator`, `ExternalTagEvaluator`, `CompositeEvaluator` — `core/evaluators_extra.py`

---

## Skill packs

See `skills_data/PACKS.md`. Domains: research, evidence, agent, documents, recovery (educational only).

---

## Quick Start

```bash
pip install -r requirements.txt
python tests/test_core.py
python -m examples.basic_loop
python -m examples.full_cycle
python -m examples.orchestrated_canary
python -m examples.swarm_demo
```

CI: `.github/workflows/ci.yml`

---

## Status

| Area | State |
|------|--------|
| Bayesian layers 0–4 + canary safety | in place |
| Swarm multi-agent layer | in place |
| Production LLM factory + adapters | in place |
| Extra evaluators | in place |
| Skill packs + Drive alignment | in place |
| Orchestrator / canary / hard-commit | in place |
| CI | in place |
