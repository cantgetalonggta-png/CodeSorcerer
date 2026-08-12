"""
Full improvement cycle using BeliefStore + Harness + Orchestrator.
"""

from __future__ import annotations
import numpy as np
from core.belief_store import BeliefStore
from core.harness import Harness
from core.orchestrator import Orchestrator
from audit.schema import AuditLog


def evaluate_fn(config, instance: int) -> float:
    """Dummy evaluator – higher score for richer candidate patches."""
    if isinstance(config, dict):
        n = len(config.get("skills", {})) + len(config.get("policy_fragments", {}))
        base = 0.55 + 0.05 * min(n, 4)
    else:
        base = 0.50
    return base + abs(np.random.randn() * 0.02)


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
        canary_extra_sessions=5,
        canary_success_threshold=0.5,
        canary_min_sessions=3,
    )

    orch.interventional_update_skill("skill_demo", success=True, is_agent_action=False)
    orch.interventional_update_skill("skill_demo", success=True, is_agent_action=False)
    orch.interventional_update_skill("skill_demo", success=False, is_agent_action=False)

    candidate_patch = {
        "skills": {
            "skill_demo": {"description": "demo skill improved", "version": 2},
            "extra": {"description": "evidence aware helper"},
        },
        "policy_fragments": {"evidence_policy": "Only external observations update beliefs."},
    }
    incumbent = {"skills": harness.skills, "policy_fragments": harness.policy_fragments}

    instances = list(range(30))
    decision = orch.evaluate_candidate(
        candidate_id="cand_v1",
        candidate_patch=candidate_patch,
        incumbent_config=incumbent,
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
