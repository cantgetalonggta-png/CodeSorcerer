"""Bayesian core for CodeSorcerer autonomous agent."""

from .hierarchical_model import hierarchical_self_model, run_svi, get_posterior_means
from .interventional import interventional_loss, interventional_bayes_update
from .eprocess import GROMixtureState, update_gro_mixture, HarmonicSpender, production_commit_gate
from .conformal import nonconformity_scores, split_conformal_interval, conformal_p_value
from .inference_layers import INFERENCE_STACK, describe_stack, belief_layer0_snapshot

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
    "INFERENCE_STACK",
    "describe_stack",
    "belief_layer0_snapshot",
]
