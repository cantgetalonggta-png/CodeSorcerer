"""
GRO mixture e-process + family-wise harmonic spending schedule.

Provides anytime-valid Type-I error control under optional stopping
and lifetime false-commit control.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple
import numpy as np


@dataclass
class GROMixtureState:
    wealth: float = 1.0
    n: int = 0
    history: List[float] = field(default_factory=list)
    # (pi1, weight) mixture components
    components: List[Tuple[float, float]] = field(
        default_factory=lambda: [
            (0.55, 0.25),
            (0.65, 0.35),
            (0.75, 0.25),
            (0.85, 0.15),
        ]
    )
    pi0: float = 0.50  # null probability that candidate is better


def gro_mixture_e(outcome: float, state: GROMixtureState) -> float:
    """Mixture growth-rate optimal e-variable."""
    e = 0.0
    for pi1, w in state.components:
        if outcome >= 0.5:  # candidate won
            e_i = pi1 / state.pi0
        else:
            e_i = (1.0 - pi1) / (1.0 - state.pi0)
        e += w * e_i
    return max(e, 1e-12)


def update_gro_mixture(state: GROMixtureState, outcome: float) -> GROMixtureState:
    e = gro_mixture_e(outcome, state)
    state.wealth *= e
    state.n += 1
    state.history.append(float(outcome))
    return state


class HarmonicSpender:
    """Lifetime-wise error spending using a harmonic-style schedule."""

    def __init__(self, alpha_total: float = 0.05, max_tests: int = 10_000):
        self.alpha_total = alpha_total
        self.max_tests = max_tests
        self.tests_done = 0
        self.spent = 0.0

    def next_alpha(self) -> float:
        self.tests_done += 1
        remaining = self.alpha_total - self.spent
        if remaining <= 0:
            return 1e-12
        portion = remaining / (2.0 * (1.0 + np.log1p(self.tests_done)))
        alpha_t = min(portion, remaining * 0.5)
        self.spent += alpha_t
        return float(alpha_t)

    def threshold(self) -> float:
        return 1.0 / max(self.next_alpha(), 1e-12)


def production_commit_gate(
    state: GROMixtureState,
    spender: HarmonicSpender,
    min_n: int = 8,
    wealth_floor: float = 0.15,
) -> str:
    """
    Returns: "commit" | "reject" | "continue"
    """
    if state.n < min_n:
        return "continue"

    thresh = spender.threshold()

    if state.wealth >= thresh:
        return "commit"
    if state.wealth < wealth_floor and state.n > 25:
        return "reject"
    return "continue"
