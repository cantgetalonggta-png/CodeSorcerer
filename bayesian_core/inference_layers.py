"""
Bayesian inference layers for CodeSorcerer.

Layer 0 — Conjugate Beta counts in BeliefStore (fast path)
Layer 1 — Hierarchical NumPyro model (population + per-skill/memory)
Layer 2 — Posterior predictive → conformal nonconformity
Layer 3 — E-process / GRO mixture gate (anytime-valid commit)
Layer 4 — Canary empirical check before hard commit

This module documents and wires the stack; heavy lifting stays in
hierarchical_model, eprocess, conformal, canary, orchestrator.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import math


@dataclass
class LayerSummary:
    layer: int
    name: str
    description: str
    status: str


INFERENCE_STACK: List[LayerSummary] = [
    LayerSummary(0, "Conjugate BeliefStore", "Beta alpha/beta counts per skill/memory; O(1) updates", "active"),
    LayerSummary(1, "Hierarchical NumPyro", "Shared hyperpriors + plates for skills/memory/LR/policy/confidence", "active"),
    LayerSummary(2, "Conformal layer", "Split-conformal intervals from residual nonconformity scores", "active"),
    LayerSummary(3, "GRO e-process gate", "Anytime-valid commit/reject under optional stopping + harmonic spend", "active"),
    LayerSummary(4, "Canary empirical", "Extra sessions under candidate harness; promote only if success_rate OK", "active"),
]


def beta_mean(alpha: float, beta: float) -> float:
    return alpha / (alpha + beta) if (alpha + beta) > 0 else 0.5


def beta_variance(alpha: float, beta: float) -> float:
    s = alpha + beta
    if s <= 1:
        return 0.25
    return (alpha * beta) / (s * s * (s + 1))


def soft_confidence_from_beta(alpha: float, beta: float) -> float:
    """Map posterior concentration to a crude confidence in [0,1]."""
    n = alpha + beta - 2.0  # pseudo-counts beyond prior
    return max(0.0, min(1.0, 1.0 - math.exp(-max(n, 0) / 10.0)))


def belief_layer0_snapshot(belief_store) -> Dict[str, Any]:
    """Export layer-0 means/variances for skills."""
    out = {}
    for sid in set(list(belief_store.skill_alpha.keys()) + list(belief_store.skill_beta.keys())):
        a = belief_store.skill_alpha.get(sid, 1.0)
        b = belief_store.skill_beta.get(sid, 1.0)
        out[sid] = {
            "mean": beta_mean(a, b),
            "var": beta_variance(a, b),
            "confidence": soft_confidence_from_beta(a, b),
            "alpha": a,
            "beta": b,
        }
    return out


def describe_stack() -> str:
    lines = ["Bayesian inference stack:"]
    for L in INFERENCE_STACK:
        lines.append(f"  L{L.layer} [{L.status}] {L.name}: {L.description}")
    return "\n".join(lines)
