"""
Hierarchical NumPyro model that jointly tracks:
  - skill / SOP reliability
  - memory-bank entry reliability
  - learning-rate hyper-parameters
  - policy fragment strength
  - confidence / value calibration

Designed to be SVI-friendly and to store only sufficient statistics
in the belief store / self.metrics.
"""

from __future__ import annotations
from typing import Any, Dict, Optional
import jax
import jax.numpy as jnp
import numpyro
import numpyro.distributions as dist
from numpyro.infer import SVI, Trace_ELBO, Predictive
from numpyro.infer.autoguide import AutoDiagonalNormal
from numpyro.optim import Adam


def hierarchical_self_model(
    skill_successes: Optional[jnp.ndarray] = None,
    skill_failures: Optional[jnp.ndarray] = None,
    mem_successes: Optional[jnp.ndarray] = None,
    mem_failures: Optional[jnp.ndarray] = None,
    observed_improvements: Optional[jnp.ndarray] = None,
    task_features: Optional[jnp.ndarray] = None,
    policy_scores: Optional[jnp.ndarray] = None,
    confidence_errors: Optional[jnp.ndarray] = None,
    n_skills: Optional[int] = None,
    n_mem: Optional[int] = None,
):
    """Joint hierarchical generative model."""

    # Global hyper-priors
    mu_skill = numpyro.sample("mu_skill", dist.Normal(0.0, 1.5))
    sigma_skill = numpyro.sample("sigma_skill", dist.HalfNormal(0.8))

    mu_mem = numpyro.sample("mu_mem", dist.Normal(0.0, 1.5))
    sigma_mem = numpyro.sample("sigma_mem", dist.HalfNormal(0.8))

    mu_lr = numpyro.sample("mu_lr", dist.Normal(-3.0, 1.0))
    sigma_lr = numpyro.sample("sigma_lr", dist.HalfNormal(0.6))

    mu_policy = numpyro.sample("mu_policy", dist.Normal(0.0, 1.0))
    sigma_policy = numpyro.sample("sigma_policy", dist.HalfNormal(0.7))

    mu_conf = numpyro.sample("mu_conf", dist.Normal(0.0, 0.5))
    sigma_conf = numpyro.sample("sigma_conf", dist.HalfNormal(0.4))

    # Skill plate
    if skill_successes is not None:
        K = n_skills if n_skills is not None else skill_successes.shape[0]
        with numpyro.plate("skills", K):
            skill_offset = numpyro.sample("skill_offset", dist.Normal(0.0, 1.0))
            logit_theta = mu_skill + sigma_skill * skill_offset
            theta_skill = numpyro.deterministic("theta_skill", jax.nn.sigmoid(logit_theta))

            total = skill_successes + skill_failures
            numpyro.sample(
                "skill_obs",
                dist.BetaBinomial(
                    concentration1=theta_skill * 20.0 + 1e-3,
                    concentration0=(1.0 - theta_skill) * 20.0 + 1e-3,
                    total_count=total,
                ),
                obs=skill_successes,
            )

    # Memory-bank plate
    if mem_successes is not None:
        M = n_mem if n_mem is not None else mem_successes.shape[0]
        with numpyro.plate("memory_entries", M):
            mem_offset = numpyro.sample("mem_offset", dist.Normal(0.0, 1.0))
            logit_theta_m = mu_mem + sigma_mem * mem_offset
            theta_mem = numpyro.deterministic("theta_mem", jax.nn.sigmoid(logit_theta_m))

            total_m = mem_successes + mem_failures
            numpyro.sample(
                "mem_obs",
                dist.BetaBinomial(
                    concentration1=theta_mem * 15.0 + 1e-3,
                    concentration0=(1.0 - theta_mem) * 15.0 + 1e-3,
                    total_count=total_m,
                ),
                obs=mem_successes,
            )

    # Learning-rate + improvement link
    if observed_improvements is not None and task_features is not None:
        T = observed_improvements.shape[0]
        with numpyro.plate("tasks", T):
            log_lr = numpyro.sample("log_lr", dist.Normal(mu_lr, sigma_lr))
            lr = numpyro.deterministic("lr", jnp.exp(log_lr))
            pred = lr * jnp.sum(task_features, axis=-1)
            numpyro.sample(
                "improvement",
                dist.Normal(pred, 0.15),
                obs=observed_improvements,
            )

    # Policy fragments
    if policy_scores is not None:
        P = policy_scores.shape[0]
        with numpyro.plate("policy_fragments", P):
            policy_offset = numpyro.sample("policy_offset", dist.Normal(0.0, 1.0))
            strength = numpyro.deterministic(
                "policy_strength", mu_policy + sigma_policy * policy_offset
            )
            numpyro.sample(
                "policy_obs",
                dist.Normal(strength, 0.3),
                obs=policy_scores,
            )

    # Confidence / value calibration
    if confidence_errors is not None:
        C = confidence_errors.shape[0]
        with numpyro.plate("confidence", C):
            conf_offset = numpyro.sample("conf_offset", dist.Normal(0.0, 1.0))
            conf_scale = numpyro.deterministic(
                "conf_scale", jnp.exp(mu_conf + sigma_conf * conf_offset)
            )
            numpyro.sample(
                "conf_obs",
                dist.HalfNormal(conf_scale),
                obs=jnp.abs(confidence_errors),
            )


def run_svi(
    model,
    data: Dict[str, Any],
    num_steps: int = 2000,
    lr: float = 1e-3,
    rng_key: Optional[jax.Array] = None,
):
    if rng_key is None:
        rng_key = jax.random.PRNGKey(0)

    guide = AutoDiagonalNormal(model)
    optimizer = Adam(lr)
    svi = SVI(model, guide, optimizer, loss=Trace_ELBO())
    svi_state = svi.init(rng_key, **data)

    losses = []
    for step in range(num_steps):
        svi_state, loss = svi.update(svi_state, **data)
        losses.append(float(loss))
        if step % 500 == 0:
            print(f"[SVI] step {step:5d}  loss = {loss:.4f}")

    params = svi.get_params(svi_state)
    return params, guide, losses


def get_posterior_means(
    params,
    guide,
    model,
    data: Dict[str, Any],
    num_samples: int = 200,
    rng_key: Optional[jax.Array] = None,
):
    if rng_key is None:
        rng_key = jax.random.PRNGKey(1)

    predictive = Predictive(model, guide=guide, params=params, num_samples=num_samples)
    samples = predictive(rng_key, **data)

    means = {}
    for k, v in samples.items():
        if k.startswith("theta_") or k in {"lr", "policy_strength", "conf_scale"}:
            means[k] = jnp.mean(v, axis=0)
    return means, samples
