"""
Minimal end-to-end improvement cycle example.

Demonstrates:
- interventional belief update
- GRO mixture + harmonic spender
- conformal gate
- soft / hard commit decision
- audit logging
"""

from __future__ import annotations
import numpy as np
from bayesian_core.eprocess import GROMixtureState, HarmonicSpender, update_gro_mixture
from bayesian_core.conformal import nonconformity_scores, split_conformal_interval, conformal_p_value
from commit_gate.soft_hard import soft_commit_decision
from audit.schema import AuditLog, CertificateRecord


def fake_evaluate(config, instance) -> float:
    """Placeholder evaluator. Replace with real task metric."""
    # Higher is better
    base = 0.6 if config == "candidate" else 0.55
    noise = np.random.randn() * 0.05
    return base + noise


def run_example_cycle(n_instances: int = 30):
    print("=== CodeSorcerer basic improvement cycle ===")

    spender = HarmonicSpender(alpha_total=0.05)
    e_state = GROMixtureState()
    audit = AuditLog()

    # Simulate streaming paired evaluation
    for i in range(n_instances):
        score_c = fake_evaluate("candidate", i)
        score_i = fake_evaluate("incumbent", i)
        outcome = 1.0 if score_c > score_i else 0.0
        e_state = update_gro_mixture(e_state, outcome)

        # Fake conformal numbers for demonstration
        cal_scores = np.random.uniform(0.05, 0.25, size=40)
        q_hat = split_conformal_interval(cal_scores, alpha=0.10)
        test_score = 0.12
        conf_p = conformal_p_value(test_score, cal_scores)
        width = q_hat * 2

        decision = soft_commit_decision(
            e_state=e_state,
            spender=spender,
            conformal_p=conf_p,
            conformal_width=width,
        )

        print(f"[{i:02d}] wealth={e_state.wealth:.3f}  decision={decision}")

        if decision in {"hard_commit", "soft_canary", "reject"}:
            rec = CertificateRecord.create(
                candidate_id="demo_candidate_v1",
                decision=decision,
                e_wealth=e_state.wealth,
                e_n=e_state.n,
                alpha_spent=spender.spent,
                conformal_p=conf_p,
                conformal_width=width,
                notes="example cycle",
            )
            audit.append(rec)
            break

    print("\nAudit summary:", audit.replay_summary())
    return audit


if __name__ == "__main__":
    run_example_cycle()
