"""
Tighter end-to-end example:
  BeliefStore + Harness + SkillRegistry + Evaluator +
  Orchestrator (hard-commit + real canary sessions)
"""

from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.belief_store import BeliefStore
from core.harness import Harness
from core.orchestrator import Orchestrator
from core.evaluator import KeywordMatchEvaluator, ThresholdSuccessEvaluator, make_canary_session_fn
from skills.registry import SkillRegistry
from audit.schema import AuditLog


def main():
    print("=== CodeSorcerer orchestrated canary example ===")

    # Load skills
    reg = SkillRegistry(skills_dir="skills_data")
    reg.load_directory()
    print("Loaded skills:", reg.list_skills())

    belief = BeliefStore()
    harness = Harness()
    # Seed harness with a baseline skill description
    harness.add_skill("baseline", {
        "description": "generic helper",
        "content": "answer questions",
    })

    audit = AuditLog()
    orch = Orchestrator(
        belief_store=belief,
        harness=harness,
        audit_log=audit,
        alpha_total=0.05,
        state_dir="state",
        canary_extra_sessions=8,
    )

    # Candidate patch that should score better on keyword instances
    candidate_patch = {
        "skills": {
            "summarize": {
                "description": "Produce a concise summary preserving key facts and causal claims",
                "content": "identify main claim, list external evidence, note uncertainty",
            },
            "verify_claim": {
                "description": "Check a factual claim against external evidence and tool results",
                "content": "prefer interventional evidence over agent statements",
            },
        },
        "policy_fragments": {
            "evidence_policy": "Only external observations update beliefs."
        },
    }

    # Evaluation instances (keyword coverage tasks)
    instances = [
        {"keywords": ["summary", "evidence", "claim"], "text": "need a good summary of evidence"},
        {"keywords": ["verify", "external", "interventional"], "text": "verify the claim carefully"},
        {"keywords": ["causal", "facts", "uncertainty"], "text": "preserve causal facts"},
        {"keywords": ["summary", "claim", "external"], "text": "another summary task"},
        {"keywords": ["evidence", "tool", "verified"], "text": "use tool results"},
    ] * 4  # repeat so we have enough for the e-process

    evaluator = KeywordMatchEvaluator()
    threshold_eval = ThresholdSuccessEvaluator(evaluator, threshold=0.4)
    session_fn = make_canary_session_fn(threshold_eval, instances)

    def evaluate_fn(config, instance):
        return evaluator.score(config, instance)

    decision = orch.evaluate_candidate(
        candidate_id="evidence_skills_v1",
        candidate_patch=candidate_patch,
        incumbent_config={"skills": harness.skills, "policy_fragments": harness.policy_fragments},
        instances=instances,
        evaluate_fn=evaluate_fn,
        session_fn_for_canary=session_fn,
    )

    print(f"Decision: {decision}")
    print(f"Harness version: {harness.version}")
    print(f"Belief version: {belief.version}")
    print(f"Skills now in harness: {list(harness.skills.keys())}")
    print(f"Audit summary: {audit.replay_summary()}")
    orch.persist()
    print("State written to ./state/")


if __name__ == "__main__":
    main()
