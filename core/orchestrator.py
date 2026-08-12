"""
Orchestrator – top-level improvement cycle controller.

Coordinates:
  session → verification → interventional update →
  candidate generation → e-process + conformal gate →
  soft/hard commit (real canary + real patch merge) → audit
"""

from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional
from pathlib import Path

from core.belief_store import BeliefStore
from core.harness import Harness
from core.canary import CanaryRunner, CanaryResult
from core.commit import apply_candidate_patch
from bayesian_core.eprocess import GROMixtureState, HarmonicSpender, update_gro_mixture
from bayesian_core.conformal import split_conformal_interval, conformal_p_value
from commit_gate.soft_hard import soft_commit_decision
from audit.schema import AuditLog, CertificateRecord


class Orchestrator:
    def __init__(
        self,
        belief_store: BeliefStore,
        harness: Harness,
        audit_log: Optional[AuditLog] = None,
        alpha_total: float = 0.05,
        state_dir: str | Path = "state",
        canary_extra_sessions: int = 10,
    ):
        self.belief = belief_store
        self.harness = harness
        self.audit = audit_log or AuditLog()
        self.spender = HarmonicSpender(alpha_total=alpha_total)
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.canary_runner = CanaryRunner(canary_dir=self.state_dir / "canaries")
        self.canary_extra_sessions = canary_extra_sessions
        # Pending soft-canary state: candidate_id → (patch, certificate)
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
        """
        Run paired evaluation under GRO mixture + conformal gate.
        On hard_commit → apply_candidate_patch.
        On soft_canary → deploy real canary and optionally run extra sessions.
        """
        e_state = GROMixtureState()
        cal_scores = cal_scores or [0.1, 0.12, 0.15, 0.18, 0.20]

        for inst in instances:
            # candidate_patch is treated as the "config" for scoring
            score_c = evaluate_fn(candidate_patch, inst)
            score_i = evaluate_fn(incumbent_config, inst)
            outcome = 1.0 if score_c > score_i + 1e-6 else 0.0
            e_state = update_gro_mixture(e_state, outcome)

            q_hat = split_conformal_interval(cal_scores, alpha=0.10)
            conf_p = conformal_p_value(0.12, cal_scores)
            width = q_hat * 2.0

            decision = soft_commit_decision(
                e_state=e_state,
                spender=self.spender,
                conformal_p=conf_p,
                conformal_width=width,
            )

            if decision != "continue":
                rec = CertificateRecord.create(
                    candidate_id=candidate_id,
                    decision=decision,
                    e_wealth=e_state.wealth,
                    e_n=e_state.n,
                    alpha_spent=self.spender.spent,
                    conformal_p=conf_p,
                    conformal_width=width,
                )
                self.audit.append(rec)

                if decision == "hard_commit":
                    self._hard_commit(candidate_patch, rec)
                elif decision == "soft_canary":
                    self._soft_canary(candidate_id, candidate_patch, rec, session_fn_for_canary)

                return decision

        return "continue"

    def _hard_commit(self, candidate_patch: Dict[str, Any], certificate: CertificateRecord):
        """Actually merge the candidate into the live harness + belief store."""
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
        """Deploy a real canary harness and optionally run extra sessions."""
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
            # Simple promotion rule: if canary success rate looks good, hard-commit
            if result.success_rate >= 0.6 and result.n_sessions >= 5:
                self._hard_commit(candidate_patch, certificate)
                self._pending_canaries.pop(candidate_id, None)

    def promote_canary(self, candidate_id: str) -> bool:
        """Manually promote a pending canary to hard commit."""
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
