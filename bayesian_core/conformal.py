"""
Conformal prediction helpers for soft-commit / canary gates.

Methods:
- Split conformal (calibration quantile)
- Jackknife+ style leave-one-out residual quantiles (approx, without refits)
- Weighted residual nonconformity
- Conformal p-values
"""

from __future__ import annotations
from typing import Optional, Tuple
import numpy as np


def nonconformity_scores(
    observed_outcomes: np.ndarray,
    predicted_theta: np.ndarray,
) -> np.ndarray:
    """Absolute residual nonconformity for Bernoulli reliability estimates."""
    return np.abs(observed_outcomes.astype(float) - predicted_theta.astype(float))


def weighted_nonconformity(
    observed_outcomes: np.ndarray,
    predicted_theta: np.ndarray,
    weights: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Weighted absolute residuals (e.g. upweight recent or high-stakes points)."""
    base = nonconformity_scores(observed_outcomes, predicted_theta)
    if weights is None:
        return base
w = np.asarray(weights, dtype=float)
    w = w / (w.mean() + 1e-12)
    return base * w


def split_conformal_interval(
    cal_scores: np.ndarray,
    alpha: float = 0.10,
) -> float:
    """(1 - alpha) quantile of calibration scores (split conformal)."""
    n = len(cal_scores)
    if n == 0:
        return 1.0
    level = np.ceil((n + 1) * (1 - alpha)) / n
    level = min(level, 1.0)
    return float(np.quantile(cal_scores, level))


def jackknife_plus_quantile(
    residuals: np.ndarray,
    alpha: float = 0.10,
) -> float:
    """
    Approximate Jackknife+ radius: quantile of leave-one-out style residuals.
    Here residuals are precomputed; true J+ would refit each fold.
    Still useful as a slightly more conservative width than plain split when
    residuals are exchangeable.
    """
    n = len(residuals)
    if n < 2:
        return split_conformal_interval(residuals, alpha)
    # Use (1-alpha)(1+1/n) quantile inflation
    level = min(1.0, (1 - alpha) * (1.0 + 1.0 / n))
    return float(np.quantile(np.abs(residuals), level))


def conformal_p_value(
    test_score: float,
    cal_scores: np.ndarray,
) -> float:
    if len(cal_scores) == 0:
        return 1.0
    return (np.sum(cal_scores >= test_score) + 1) / (len(cal_scores) + 1)


def conformal_interval_from_mean(
    theta_mean: float,
    q_hat: float,
) -> Tuple[float, float]:
    lower = float(np.clip(theta_mean - q_hat, 0.0, 1.0))
    upper = float(np.clip(theta_mean + q_hat, 0.0, 1.0))
    return lower, upper


def gate_metrics(
    cal_scores: np.ndarray,
    test_score: float,
    theta_mean: float = 0.5,
    alpha: float = 0.05,
    method: str = "split",
) -> dict:
    """Bundle width + p-value for soft_commit_decision."""
    if method == "jackknife_plus_approx":
        q = jackknife_plus_quantile(cal_scores, alpha)
    else:
        q = split_conformal_interval(cal_scores, alpha)
    lo, hi = conformal_interval_from_mean(theta_mean, q)
    return {
        "q_hat": q,
        "width": hi - lo,
        "lower": lo,
        "upper": hi,
        "p_value": conformal_p_value(test_score, cal_scores),
        "method": method,
        "alpha": alpha,
    }
