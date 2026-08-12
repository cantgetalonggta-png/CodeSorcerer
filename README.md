# CodeSorcerer

Custom Agent Framework & Persistent Workspace — Orchestrated by Grok

## Bayesian Autonomous Agent Core

Production-oriented Bayesian framework for self-improving autonomous agents.

### Key Features

- **Interventional updates** — agent actions are treated as interventions, not observations
- **Hierarchical Bayesian tracking** of `self.memory_bank`, `self.metrics`, `self.learning_rate`, `self.policy`, and confidence/values (NumPyro)
- **Anytime-valid commit gates** using GRO mixture e-processes + harmonic family-wise spending
- **Soft vs Hard commit** with real canary runner and conformal gates
- **Persistent BeliefStore + versioned Harness**
- **Orchestrator** coordinating the full improvement cycle
- **Skill / SOP registry** (Markdown + Python skills)
- **Session memory** with trajectory tagging (agent vs external)
- **LLM integration point** + tool router (EchoLLM for local testing)
- **Hardened hard-commit** that actually merges candidate patches
- **Ontology ↔ Bayesian sync** + multi-agent federation stubs
- **Audit-log schema** with replay helpers
- **Simple test suite**

### Core Principles

1. Frozen base model + mutable harness
2. Only external evidence updates posteriors (interventional mask)
3. Every live change to `self.*` requires an anytime-valid certificate
4. Soft canary stage (with real extra sessions) before hard atomic commit
5. Family-wise spending controls lifetime false-commit rate

### Directory Structure

```
core/
  belief_store.py           # Persistent posterior sufficient statistics
  harness.py                # Versioned skills / policy / memory container
  orchestrator.py           # Main improvement cycle controller
  session_memory.py         # Trajectory tagging + session persistence
  canary.py                 # Real canary runner (extra sessions)
  commit.py                 # Hard-commit path (merge candidate into harness)
bayesian_core/
  hierarchical_model.py
  interventional.py
  eprocess.py
  conformal.py
commit_gate/
  soft_hard.py
skills/
  registry.py               # Load Markdown + Python skills
llm/
  base.py                   # BaseLLM, EchoLLM, ToolRouter
audit/
  schema.py
ontology/
  sync.py
federation/
  posterior_share.py
architecture/
  reference_architecture.md
  combined_protocol.md
config/
  default.yaml
examples/
  basic_loop.py
  full_cycle.py
tests/
  test_core.py
requirements.txt
.gitignore
```

### Quick Start

```bash
pip install -r requirements.txt
python -m examples.basic_loop
python -m examples.full_cycle
python tests/test_core.py
```

State (belief store, harness, audit log, canaries, sessions) is written under `./state/`.

### Status

Core statistical, architectural, persistence, canary, skill, session, and LLM-integration pieces are in place. Ready for real evaluators and production LLM backends.
