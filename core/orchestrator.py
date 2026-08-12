"""
Orchestrator – top-level improvement cycle controller.

Coordinates:
  session → verification → interventional update →
  candidate generation (including swarm auto skill patches) →
  e-process + conformal gate → soft/hard commit → audit
"""

from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional
from pathlib import Path
import numpy as np

from core.belief_store import BeliefStore
from core.harness import Harness
from core.canary import CanaryRunner, CanaryResult
from core.commit import apply_candidate_patch
from bayesian_core.eprocess import GROMixtureState, HarmonicSpender, update_gro_mixture
from bayesian_core.conformal import gate_metrics
from commit_gate.soft_hard import soft_commit_decision
from audit.schema import AuditLog, CertificateRecord


class Orchestrator:
    def __init__(
        self,
        belief_store: BeliefStore,
        harness: Harness,
        audit_log: Optional[AuditLog] = None,
        alpha_total: float = 0.03,
        state_dir: str | Path = "state",
        canary_extra_sessions: int = 20,
        canary_success_threshold: float = 0.72,
        canary_min_sessions: int = 8,
        conformal_alpha: float = 0.05,
        max_conformal_width: float = 0.18,
        conformal_method: str = "split",
    ):
        self.belief = belief_store
        self.harness = harness
        self.audit = audit_log or AuditLog()
        self.spender = HarmonicSpender(alpha_total=alpha_total)
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.canary_runner = CanaryRunner(canary_dir=self.state_dir / "canaries")
        self.canary_extra_sessions = canary_extra_sessions
        self.canary_success_threshold = canary_success_threshold
        self.canary_min_sessions = canary_min_sessions
        self.conformal_alpha = conformal_alpha
        self.max_conformal_width = max_conformal_width
        self.conformal_method = conformal_method
        self._pending_canaries: Dict[str, Dict[str, Any]] = {}

    def interventional_update_skill(self, skill_id: str, success: bool, is_agent_action: bool = False):
        if is_agent_action:
            return
        self.belief.update_skill(skill_id, success)

    def evaluate_candidate(
        self,
        candidate_id: str,
        candidate_patch: Dict[str, Any],
        incumbent_config: Any,
        instances: List[Any],
        evaluate_fn: Callable[[Any, Any], float],
        cal_scores: Optional[List[float]] = None,
        session_fn_for_canary: Optional[Callable] = None,
    ) -> str:
        e_state = GROMixtureState()
        cal = np.asarray(cal_scores or [0.08, 0.10, 0.12, 0.14, 0.16, 0.18], dtype=float)

        for inst in instances:
            score_c = evaluate_fn(candidate_patch, inst)
            score_i = evaluate_fn(incumbent_config, inst)
            outcome = 1.0 if score_c > score_i + 1e-6 else 0.0
            e_state = update_gro_mixture(e_state, outcome)

            metrics = gate_metrics(
                cal_scores=cal,
                test_score=0.12,
                theta_mean=0.55,
                alpha=self.conformal_alpha,
                method=self.conformal_method,
            )
            decision = soft_commit_decision(
                e_state=e_state,
                spender=self.spender,
                conformal_p=metrics["p_value"],
                conformal_width=metrics["width"],
                conf_alpha=self.conformal_alpha,
                max_width=self.max_conformal_width,
            )

            if decision != "continue":
                rec = CertificateRecord.create(
                    candidate_id=candidate_id,
                    decision=decision,
                    e_wealth=e_state.wealth,
                    e_n=e_state.n,
                    alpha_spent=self.spender.spent,
                    conformal_p=metrics["p_value"],
                    conformal_width=metrics["width"],
                )
                self.audit.append(rec)
                if decision == "hard_commit":
                    self._hard_commit(candidate_patch, rec)
                elif decision == "soft_canary":
                    self._soft_canary(candidate_id, candidate_patch, rec, session_fn_for_canary)
                return decision
        return "continue"

    def evaluate_swarm_patch(
        self,
        swarm_result,
        instances: List[Any],
        evaluate_fn: Callable[[Any, Any], float],
        session_fn_for_canary: Optional[Callable] = None,
        min_agents: int = 3,
        candidate_id: Optional[str] = None,
    ) -> str:
        """Build auto skill patch from swarm and run evaluate_candidate."""
        from swarm.auto_patch import swarm_to_candidate_patch, should_propose_patch

        if not should_propose_patch(swarm_result, min_agents=min_agents):
            return "reject_insufficient_swarm"
        patch = swarm_to_candidate_patch(swarm_result)
        cid = candidate_id or f"swarm_{len(swarm_result.results)}a"
        incumbent = {
            "skills": self.harness.skills,
            "policy_fragments": self.harness.policy_fragments,
        }
        return self.evaluate_candidate(
            candidate_id=cid,
            candidate_patch=patch,
            incumbent_config=incumbent,
            instances=instances,
            evaluate_fn=evaluate_fn,
            session_fn_for_canary=session_fn_for_canary,
        )

    def _hard_commit(self, candidate_patch: Dict[str, Any], certificate: CertificateRecord):
        apply_candidate_patch(
            harness=self.harness,
            belief=self.belief,
            candidate_patch=candidate_patch,
            certificate=certificate,
        )
        self.persist()

    def _soft_canary(
        self,
        candidate_id: str,
        candidate_patch: Dict[str, Any],
        certificate: CertificateRecord,
        session_fn: Optional[Callable] = None,
    ):
        canary_harness = self.canary_runner.deploy_canary(
            candidate_id=candidate_id,
            base_harness=self.harness,
            candidate_patch=candidate_patch,
            certificate_id=certificate.certificate_id,
        )
        self._pending_canaries[candidate_id] = {
            "patch": candidate_patch,
            "certificate": certificate,
            "canary_harness": canary_harness,
        }
        if session_fn is not None:
            result: CanaryResult = self.canary_runner.run_sessions(
                canary=canary_harness,
                n_sessions=self.canary_extra_sessions,
                session_fn=session_fn,
            )
            if (
                result.success_rate >= self.canary_success_threshold
                and result.n_sessions >= self.canary_min_sessions
            ):
                self._hard_commit(candidate_patch, certificate)
                self._pending_canaries.pop(candidate_id, None)

    def promote_canary(self, candidate_id: str) -> bool:
        pending = self._pending_canaries.get(candidate_id)
        if not pending:
            return False
        self._hard_commit(pending["patch"], pending["certificate"])
        self._pending_canaries.pop(candidate_id, None)
        return True

    def persist(self):
        self.belief.save(self.state_dir / "belief_store.json")
        self.harness.save(self.state_dir / "harness.json")
        self.audit.to_json(str(self.state_dir / "audit_log.json"))
