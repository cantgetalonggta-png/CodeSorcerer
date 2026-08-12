"""
Orchestrator – top-level improvement cycle controller.

Coordinates:
  session → verification → interventional update →
  candidate generation → e-process + conformal gate →
  soft/hard commit → audit
"""

from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional
from pathlib import Path

from core.belief_store import BeliefStore
from core.harness import Harness
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
    ):
        self.belief = belief_store
        self.harness = harness
        self.audit = audit_log or AuditLog()
        self.spender = HarmonicSpender(alpha_total=alpha_total)
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def interventional_update_skill(self, skill_id: str, success: bool, is_agent_action: bool = False):
        if is_agent_action:
            return  # interventions do not update counts
        self.belief.update_skill(skill_id, success)

    def evaluate_candidate(
        self,
        candidate_id: str,
        candidate_config: Any,
        incumbent_config: Any,
        instances: List[Any],
        evaluate_fn: Callable[[Any, Any], float],
        cal_scores: Optional[List[float]] = None,
    ) -> str:
        """
        Run paired evaluation under GRO mixture + conformal gate.
        Returns final decision string.
        """
        e_state = GROMixtureState()
        cal_scores = cal_scores or [0.1, 0.12, 0.15, 0.18, 0.20]

        for inst in instances:
            score_c = evaluate_fn(candidate_config, inst)
            score_i = evaluate_fn(incumbent_config, inst)
            outcome = 1.0 if score_c > score_i + 1e-6 else 0.0
            e_state = update_gro_mixture(e_state, outcome)

            q_hat = split_conformal_interval(cal_scores, alpha=0.10)
            conf_p = conformal_p_value(0.12, cal_scores)  # placeholder test score
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
                    self._hard_commit(candidate_id, candidate_config, rec.certificate_id)
                elif decision == "soft_canary":
                    self._soft_canary(candidate_id, candidate_config, rec.certificate_id)

                return decision

        return "continue"

    def _hard_commit(self, candidate_id: str, config: Any, cert_id: str):
        # Placeholder: real implementation would merge config into harness
        self.harness.bump(cert_id)
        self.belief.set_certificate(cert_id)
        self.persist()

    def _soft_canary(self, candidate_id: str, config: Any, cert_id: str):
        # Placeholder: write canary harness snapshot
        canary_path = self.state_dir / f"canary_{candidate_id}_{cert_id[:8]}.json"
        snap = self.harness.snapshot()
        snap.metadata["canary_for"] = candidate_id
        snap.metadata["certificate_id"] = cert_id
        snap.save(canary_path)

    def persist(self):
        self.belief.save(self.state_dir / "belief_store.json")
        self.harness.save(self.state_dir / "harness.json")
        self.audit.to_json(str(self.state_dir / "audit_log.json"))
