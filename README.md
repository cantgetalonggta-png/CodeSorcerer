# CodeSorcerer

Custom Agent Framework & Persistent Workspace — Orchestrated by Grok

## Bayesian Autonomous Agent Core

Production-oriented Bayesian framework for self-improving autonomous agents.

### Key Features

- **Interventional updates** — agent actions are treated as interventions, not observations
- **Hierarchical Bayesian tracking** of `self.memory_bank`, `self.metrics`, `self.learning_rate`, `self.policy`, and confidence/values (NumPyro)
- **Anytime-valid commit gates** using GRO mixture e-processes + harmonic family-wise spending
- **Soft vs Hard commit** with canary deployments and conformal prediction gates
- **Persistent BeliefStore + versioned Harness**
- **Orchestrator** coordinating the full improvement cycle
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
core/
  belief_store.py           # Persistent posterior sufficient statistics
  harness.py                # Versioned skills / policy / memory container
  orchestrator.py           # Main improvement cycle controller
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
config/
  default.yaml
examples/
  basic_loop.py
  full_cycle.py             # Full Orchestrator-based example
requirements.txt
.gitignore
```

### Quick Start

```bash
pip install -r requirements.txt
python -m examples.basic_loop
python -m examples.full_cycle
```

State (belief store, harness, audit log, canaries) is written under `./state/`.

### Status

Core statistical, architectural, and persistence pieces are in place. The system is ready for real task evaluators and deeper runtime integration.
