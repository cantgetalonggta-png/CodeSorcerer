"""
Multi-agent federated posterior sharing + certificate aggregation (stubs).

Agents can share sufficient statistics (not raw trajectories) and
aggregate certificates under a common family-wise spending budget.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import copy


@dataclass
class AgentBeliefPacket:
    agent_id: str
    skill_alpha: Dict[str, float] = field(default_factory=dict)
    skill_beta: Dict[str, float] = field(default_factory=dict)
    mem_alpha: Dict[str, float] = field(default_factory=dict)
    mem_beta: Dict[str, float] = field(default_factory=dict)
    certificates: List[Dict[str, Any]] = field(default_factory=list)
    n_obs: int = 0


def merge_beta_counts(
    global_alpha: Dict[str, float],
    global_beta: Dict[str, float],
    packet: AgentBeliefPacket,
) -> tuple[Dict[str, float], Dict[str, float]]:
    """Simple federated update of Beta sufficient statistics."""
    alpha = copy.deepcopy(global_alpha)
    beta = copy.deepcopy(global_beta)

    for k, v in packet.skill_alpha.items():
        alpha[k] = alpha.get(k, 1.0) + v
    for k, v in packet.skill_beta.items():
        beta[k] = beta.get(k, 1.0) + v

    return alpha, beta


def aggregate_certificates(
    packets: List[AgentBeliefPacket],
) -> List[Dict[str, Any]]:
    """Collect all certificates for joint audit / spending accounting."""
    all_certs = []
    for p in packets:
        for c in p.certificates:
            c = dict(c)
            c["source_agent"] = p.agent_id
            all_certs.append(c)
    return all_certs


def federated_belief_update(
    global_belief: Dict[str, Any],
    packets: List[AgentBeliefPacket],
) -> Dict[str, Any]:
    """
    Merge multiple agent packets into a global belief store.
    This is intentionally simple and can be replaced by more
    sophisticated hierarchical or robust aggregation later.
    """
    alpha = global_belief.get("skill_alpha", {})
    beta = global_belief.get("skill_beta", {})

    for packet in packets:
        alpha, beta = merge_beta_counts(alpha, beta, packet)

    global_belief["skill_alpha"] = alpha
    global_belief["skill_beta"] = beta
    global_belief["federated_certs"] = aggregate_certificates(packets)
    global_belief["n_agents"] = len(packets)
    return global_belief
