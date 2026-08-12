# Bayesian Canary Safety

## Why canaries exist

E-process certificates control **false commit rate** under optional stopping, but the evaluation distribution can still shift after deploy. The canary stage is an **empirical second lock**:

1. Candidate wins the GRO + conformal gate → **soft_canary**
2. `CanaryRunner` clones harness + applies patch
3. Extra sessions run under the canary
4. Only if success_rate ≥ threshold (default 0.6, n ≥ 5) → **hard_commit** via `apply_candidate_patch`

## Layered guarantees

| Layer | Mechanism | Failure mode blocked |
|-------|-----------|----------------------|
| Interventional mask | Agent tokens ≠ evidence | Self-delusion in posteriors |
| BeliefStore / hierarchical model | Calibrated skill reliability | Overfitting single anecdotes |
| Conformal | Distribution-free interval width | Overconfident Bayesian intervals |
| GRO mixture e-process | Anytime-valid wealth | Peeking / early stop false commits |
| Harmonic spending | Lifetime budget | Many sequential false commits |
| Canary sessions | Live empirical check | Train/eval distribution shift |
| Audit log | Replay | Silent mutations |

## Orchestrator behavior

- `evaluate_candidate(..., session_fn_for_canary=...)` enables automatic canary runs.
- `promote_canary(candidate_id)` allows manual promotion after human review.
- Hard commit always goes through `core/commit.py` (single mutation path).

## Tuning

- `alpha_total` — family-wise error spend (config/default.yaml)
- `canary_extra_sessions` — Orchestrator constructor
- Canary success threshold — currently 0.6 in Orchestrator._soft_canary (raise for stricter prod)
