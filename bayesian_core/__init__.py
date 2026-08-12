"""Bayesian core for CodeSorcerer autonomous agent."""

from .eprocess import GROMixtureState, update_gro_mixture, HarmonicSpender, production_commit_gate
from .conformal import (
    nonconformity_scores,
    split_conformal_interval,
    conformal_p_value,
    gate_metrics,
    jackknife_plus_quantile,
    weighted_nonconformity,
)
from .inference_layers import INFERENCE_STACK, describe_stack, belief_layer0_snapshot

# Optional heavy deps (jax/numpyro, torch)
try:
    from .hierarchical_model import hierarchical_self_model, run_svi, get_posterior_means
except Exception:  # pragma: no cover
    hierarchical_self_model = None  # type: ignore
    run_svi = None  # type: ignore
    get_posterior_means = None  # type: ignore

try:
    from .interventional import interventional_loss, interventional_bayes_update
except Exception:  # pragma: no cover
    interventional_loss = None  # type: ignore

    def interventional_bayes_update(posterior, outcome_success, is_agent_action, log_intervention=True):
        if is_agent_action:
            if log_intervention:
                posterior.setdefault("interventions", 0)
                posterior["interventions"] += 1
            return posterior
        if outcome_success:
            posterior["alpha"] = posterior.get("alpha", 1.0) + 1.0
        else:
            posterior["beta"] = posterior.get("beta", 1.0) + 1.0
        posterior["n_obs"] = posterior.get("n_obs", 0) + 1
        return posterior


__all__ = [
    "hierarchical_self_model",
    "run_svi",
    "get_posterior_means",
    "interventional_loss",
    "interventional_bayes_update",
    "GROMixtureState",
    "update_gro_mixture",
    "HarmonicSpender",
    "production_commit_gate",
    "nonconformity_scores",
    "split_conformal_interval",
    "conformal_p_value",
    "gate_metrics",
    "jackknife_plus_quantile",
    "weighted_nonconformity",
    "INFERENCE_STACK",
    "describe_stack",
    "belief_layer0_snapshot",
]
