# Combined Protocol

For a system that owns:

- `self.memory_bank`
- `self.metrics` / `self.performance_metrics`
- `self.session`
- `self.learning_rate`
- `self.agents.values` / confidence
- `self.policy`

## Cycle

1. **Session execution**  
   Run task under current harness. Tag every event as agent-intervention vs external observation. Store in `self.session`.

2. **Verification**  
   Produce grounded success/failure + features. Write to `self.metrics`.

3. **Interventional Bayesian update**  
   Update hierarchical posteriors using **only** external evidence (interventional mask applied).

4. **Candidate generation**  
   From current posteriors and failure modes propose:
   - skill patches / new SOPs
   - memory consolidations or reweights
   - learning-rate adaptations
   - policy / retrieval adjustments
   - value / confidence recalibrations

5. **Anytime-valid gate**  
   For each candidate run paired evaluation. Feed outcomes into GRO mixture e-process + harmonic spender. Optionally compute conformal p-value and interval width from the hierarchical model.

6. **Soft / Hard decision**  
   - `hard_commit` — both e-process and conformal support improvement
   - `soft_canary` — e-process fires but conformal is borderline → deploy canary
   - `reject` / `continue`

7. **Atomic commit** (only on hard_commit)  
   - version-bump affected harness parts
   - write new posterior sufficient statistics into belief store
   - update live `self.*` objects
   - append full certificate + e-process path to audit log

## Guarantees

| Mechanism              | Protects against                     | Property                    |
|------------------------|--------------------------------------|-----------------------------|
| Interventional mask    | Self-delusion                        | Causal correctness          |
| GRO mixture e-process  | False commits under optional stopping | Anytime-valid Type-I       |
| Harmonic spending      | Lifetime false-commit accumulation   | Family-wise control         |
| Conformal gate         | Over-confident Bayesian intervals    | Finite-sample coverage      |
| Soft canary            | Post-commit distribution shift       | Empirical safety net        |
