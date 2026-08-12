"""
Interventional update utilities.

Agent-generated tokens / actions are interventions, not observations.
They stay in context but must not contribute gradient or posterior count updates.
"""

from __future__ import annotations
from typing import Any, Dict, Optional
import torch
import torch.nn as nn


def interventional_loss(
    logits: torch.Tensor,
    labels: torch.Tensor,
    agent_token_mask: torch.Tensor,
    ignore_index: int = -100,
) -> torch.Tensor:
    """
    Cross-entropy loss that ignores agent-generated tokens.

    Parameters
    ----------
    logits : [batch, seq, vocab]
    labels : [batch, seq]
    agent_token_mask : [batch, seq] bool — True where the token was produced by the agent
    """
    loss_fct = nn.CrossEntropyLoss(reduction="none", ignore_index=ignore_index)

    shift_logits = logits[..., :-1, :].contiguous()
    shift_labels = labels[..., 1:].contiguous()
    shift_mask = agent_token_mask[..., 1:].contiguous()

    flat_logits = shift_logits.view(-1, shift_logits.size(-1))
    flat_labels = shift_labels.view(-1)
    flat_mask = shift_mask.view(-1)

    per_token_loss = loss_fct(flat_logits, flat_labels)
    per_token_loss = per_token_loss * (~flat_mask).float()

    valid = (flat_labels != ignore_index) & (~flat_mask)
    if valid.sum() == 0:
        return torch.tensor(0.0, device=logits.device, requires_grad=True)
    return per_token_loss[valid].mean()


def interventional_bayes_update(
    posterior: Dict[str, Any],
    outcome_success: bool,
    is_agent_action: bool,
    *,
    log_intervention: bool = True,
) -> Dict[str, Any]:
    """
    Update a simple Beta / count-based posterior only with external evidence.

    Agent actions may be logged but never increment success/failure counts.
    """
    if is_agent_action:
        if log_intervention:
            posterior.setdefault("interventions", 0)
            posterior["interventions"] += 1
        return posterior

    # External evidence only
    if outcome_success:
        posterior["alpha"] = posterior.get("alpha", 1.0) + 1.0
    else:
        posterior["beta"] = posterior.get("beta", 1.0) + 1.0

    posterior["n_obs"] = posterior.get("n_obs", 0) + 1
    return posterior
