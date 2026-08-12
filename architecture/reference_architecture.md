# Reference Architecture

## Layered Design

```
L3  Loop Controllers + Anytime-Valid Gates
     (GRO mixture e-process, harmonic spending, conformal gate)
          |
L2  Versioned Harness
     Skills / SOPs | Memory Bank | Tools | Ontology | Metrics Store
          |
L1  Steering Adapter
     (lightweight residual / context injector / retrieval policy)
          |
L0  Frozen Base Model
```

## Cross-cutting Bayesian Core

- Hierarchical NumPyro model jointly tracks all `self.*` quantities
- Interventional likelihood masking (agent actions ≠ ordinary evidence)
- Sufficient statistics stored in belief store / `self.metrics`
- Model definition itself is versioned inside the harness

## Safety Invariants

1. Base model weights remain frozen.
2. Only external (non-agent) evidence updates posteriors.
3. Every live mutation of `self.memory_bank`, `self.policy`, `self.learning_rate`, etc. carries an anytime-valid certificate.
4. Soft canary stage is the default path before hard atomic commit.
5. Family-wise spending controls lifetime false-commit rate.
