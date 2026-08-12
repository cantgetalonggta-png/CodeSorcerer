"""
Full improvement cycle using BeliefStore + Harness + Orchestrator.
"""

from __future__ import annotations
import numpy as np
from core.belief_store import BeliefStore
from core.harness import Harness
from core.orchestrator import Orchestrator
from audit.schema import AuditLog


def evaluate_fn(config: str, instance: int) -> float:
    """Dummy evaluator – replace with real task metric."""
    base = 0.62 if config == "candidate" else 0.55
    return base + np.random.randn() * 0.04


def main():
    print("=== CodeSorcerer full improvement cycle ===")

    belief = BeliefStore()
    harness = Harness()
    harness.add_skill("skill_demo", {"description": "demo skill", "version": 1})
    audit = AuditLog()

    orch = Orchestrator(
        belief_store=belief,
        harness=harness,
        audit_log=audit,
        alpha_total=0.05,
        state_dir="state",
    )

    # Simulate some external evidence first
    orch.interventional_update_skill("skill_demo", success=True, is_agent_action=False)
    orch.interventional_update_skill("skill_demo", success=True, is_agent_action=False)
    orch.interventional_update_skill("skill_demo", success=False, is_agent_action=False)

    instances = list(range(25))
    decision = orch.evaluate_candidate(
        candidate_id="cand_v1",
        candidate_config="candidate",
        incumbent_config="incumbent",
        instances=instances,
        evaluate_fn=evaluate_fn,
    )

    print(f"Final decision: {decision}")
    print(f"Belief version: {belief.version}")
    print(f"Harness version: {harness.version}")
    print(f"Audit summary: {audit.replay_summary()}")
    print(f"Skill mean (demo): {belief.skill_mean('skill_demo'):.3f}")

    orch.persist()
    print("State persisted to ./state/")


if __name__ == "__main__":
    main()
