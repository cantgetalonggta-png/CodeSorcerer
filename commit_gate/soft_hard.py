"""
Soft vs Hard commit gate.

- Hard commit: atomic write into live self.* and versioned harness
- Soft commit: promote to canary first, then re-evaluate with conformal + e-process
"""

from __future__ import annotations
from typing import Any, Dict, Optional
from bayesian_core.eprocess import GROMixtureState, HarmonicSpender, production_commit_gate, update_gro_mixture
from bayesian_core.conformal import conformal_p_value, split_conformal_interval


def soft_commit_decision(
    e_state: GROMixtureState,
    spender: HarmonicSpender,
    conformal_p: float,
    conformal_width: float,
    conf_alpha: float = 0.10,
    max_width: float = 0.25,
) -> str:
    """
    Returns one of:
      "hard_commit" | "soft_canary" | "reject" | "continue"
    """
    e_decision = production_commit_gate(e_state, spender)

    if e_decision == "reject":
        return "reject"

    conformal_ok = (conformal_p > conf_alpha) and (conformal_width < max_width)

    if e_decision == "commit" and conformal_ok:
        return "hard_commit"
    if e_decision == "commit":
        return "soft_canary"
    return "continue"


def run_paired_evaluation(
    candidate: Any,
    incumbent: Any,
    instances: list,
    evaluate_fn,
    spender: Optional[HarmonicSpender] = None,
    alpha_total: float = 0.05,
) -> tuple[str, GROMixtureState]:
    """
    Simple streaming evaluation that feeds the GRO mixture.
    evaluate_fn(config, instance) -> float (higher is better)
    """
    if spender is None:
        spender = HarmonicSpender(alpha_total=alpha_total)

    state = GROMixtureState()
    for inst in instances:
        score_c = evaluate_fn(candidate, inst)
        score_i = evaluate_fn(incumbent, inst)
        outcome = 1.0 if score_c > score_i + 1e-6 else 0.0
        state = update_gro_mixture(state, outcome)

        decision = production_commit_gate(state, spender)
        if decision != "continue":
            return decision, state

    return "continue", state
