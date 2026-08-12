"""
Conformal prediction helpers for soft-commit / canary gates.

Uses posterior predictive residuals from the hierarchical Bayesian model
as nonconformity scores.
"""

from __future__ import annotations
from typing import Optional
import numpy as np


def nonconformity_scores(
    observed_outcomes: np.ndarray,
    predicted_theta: np.ndarray,
) -> np.ndarray:
    """
    Absolute residual nonconformity for Bernoulli reliability estimates.
    Higher score = more nonconforming.
    """
    return np.abs(observed_outcomes.astype(float) - predicted_theta.astype(float))


def split_conformal_interval(
    cal_scores: np.ndarray,
    alpha: float = 0.10,
) -> float:
    """
    Return the (1 - alpha) quantile of calibration nonconformity scores
    (split conformal).
    """
    n = len(cal_scores)
    if n == 0:
        return 1.0
    level = np.ceil((n + 1) * (1 - alpha)) / n
    level = min(level, 1.0)
    return float(np.quantile(cal_scores, level))


def conformal_p_value(
    test_score: float,
    cal_scores: np.ndarray,
) -> float:
    """Simple conformal p-value."""
    if len(cal_scores) == 0:
        return 1.0
    return (np.sum(cal_scores >= test_score) + 1) / (len(cal_scores) + 1)


def conformal_interval_from_mean(
    theta_mean: float,
    q_hat: float,
) -> tuple[float, float]:
    """Form [lower, upper] interval around a point prediction."""
    lower = float(np.clip(theta_mean - q_hat, 0.0, 1.0))
    upper = float(np.clip(theta_mean + q_hat, 0.0, 1.0))
    return lower, upper
