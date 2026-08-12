# CodeSorcerer

Custom Agent Framework & Persistent Workspace — Orchestrated by Grok

## Bayesian Autonomous Agent Core

Production-oriented Bayesian framework for self-improving autonomous agents.

### Key Features

- **Interventional updates** — agent actions are treated as interventions, not observations
- **Hierarchical Bayesian tracking** of `self.memory_bank`, `self.metrics`, `self.learning_rate`, `self.policy`, and confidence/values (NumPyro)
- **Anytime-valid commit gates** using GRO mixture e-processes + harmonic family-wise spending
- **Soft vs Hard commit** with canary deployments and conformal prediction gates
- **Ontology ↔ Bayesian sync** stubs
- **Multi-agent federated posterior** sharing + certificate aggregation
- **Concrete audit-log schema** with replay helpers

### Core Principles

1. Frozen base model + mutable harness
2. Only external evidence updates posteriors (interventional mask)
3. Every live change to `self.*` requires an anytime-valid certificate
4. Soft canary stage is the default before hard atomic commit
5. Family-wise spending controls lifetime false-commit rate

### Directory Structure

```
bayesian_core/
  hierarchical_model.py     # Joint NumPyro hierarchical model
  interventional.py         # Interventional likelihood mask
  eprocess.py               # GRO mixture + harmonic spending
  conformal.py              # Conformal prediction helpers
commit_gate/
  soft_hard.py              # Soft / Hard commit + canary logic
audit/
  schema.py                 # Certificate records + AuditLog + replay
ontology/
  sync.py                   # Ontology ↔ Bayesian bidirectional sync
federation/
  posterior_share.py        # Multi-agent belief packets + aggregation
architecture/
  reference_architecture.md
  combined_protocol.md
examples/
  basic_loop.py             # Minimal end-to-end improvement cycle
requirements.txt
```

### Quick Start

```bash
pip install -r requirements.txt
python -m examples.basic_loop
```

### Status

Core statistical and architectural pieces are in place. Ready for extension into a full persistent agent runtime.
