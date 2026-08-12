# Conformal Prediction Methods

Implemented in `bayesian_core/conformal.py`.

## Split conformal

1. Hold out calibration residuals (absolute error vs predicted θ).
2. Take the inflated (1−α) quantile: `ceil((n+1)(1−α))/n`.
3. Interval: `[θ̂ − q, θ̂ + q]` clipped to [0,1] for reliability parameters.

## Jackknife+ approximate

Uses residual quantiles with `(1−α)(1+1/n)` inflation. True Jackknife+ refits the model leaving one out each time; our approx is appropriate when residuals are already exchangeable and refits are expensive (LLM/harness loops).

## Weighted nonconformity

`weighted_nonconformity(y, θ̂, weights)` scales residuals (e.g. recent sessions or high-stakes tasks). Feed the weighted scores into split/J+ quantiles.

## Conformal p-value

`(# calibration scores ≥ test score + 1) / (n + 1)` — used in soft_commit_decision as `conformal_p`.

## Gate bundle

`gate_metrics(...)` returns `q_hat`, `width`, `lower`, `upper`, `p_value`, `method`, `alpha` for the Orchestrator.

## Config (`config/default.yaml`)

```yaml
conformal_alpha: 0.05
max_conformal_width: 0.18
conformal_method: split  # or jackknife_plus_approx
```

Stricter α and smaller max width force more candidates into **soft_canary** instead of immediate **hard_commit**.
