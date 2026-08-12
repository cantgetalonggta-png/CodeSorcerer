# CodeSorcerer

Custom Agent Framework & Persistent Workspace — Orchestrated by Grok

## Bayesian Autonomous Agent Core

This repository contains a production-oriented Bayesian framework for self-improving autonomous agents. The system is designed around:

- **Interventional updates** (causal correctness — agent actions are interventions, not observations)
- **Hierarchical Bayesian tracking** of `self.memory_bank`, `self.metrics`, `self.learning_rate`, `self.policy`, and confidence/values
- **Anytime-valid commit gates** using GRO mixture e-processes + family-wise spending
- **Soft vs Hard commit** with canary deployments and conformal prediction
- **Ontology-aware** belief management

### Core Principles

1. Frozen base model + mutable harness
2. Only external evidence updates posteriors (interventional mask)
3. Every live change to `self.*` requires an anytime-valid certificate
4. Soft canary stage before hard atomic commit

### Directory Structure

```
bayesian_core/
  hierarchical_model.py   # Joint NumPyro hierarchical model
  interventional.py       # Interventional likelihood mask
  eprocess.py             # GRO mixture + harmonic spending
  conformal.py            # Conformal prediction helpers
commit_gate/
  soft_hard.py            # Soft/Hard commit logic + canary
architecture/
  reference_architecture.md
  combined_protocol.md
```

### Status

Actively developed. All statistical licenses are designed to survive the endogenous self-improvement loop.
