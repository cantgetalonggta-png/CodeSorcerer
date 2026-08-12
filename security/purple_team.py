"""
Purple-team defensive checks for CodeSorcerer.

Internal control tests only — verify interventional discipline,
commit certificates, session tagging, and evidence filtering.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str


@dataclass
class PurpleReport:
    results: List[CheckResult] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return all(r.passed for r in self.results)

    def summary(self) -> str:
        lines = [f"[{'PASS' if r.passed else 'FAIL'}] {r.name}: {r.detail}" for r in self.results]
        lines.append(
            f"Overall: {'PASS' if self.ok else 'FAIL'} "
            f"({sum(r.passed for r in self.results)}/{len(self.results)})"
        )
        return "\n".join(lines)


def check_orchestrator_skips_agent_updates() -> CheckResult:
    """Orchestrator.interventional_update_skill must no-op when is_agent_action=True."""
    from core.belief_store import BeliefStore
    from core.harness import Harness
    from core.orchestrator import Orchestrator

    b = BeliefStore()
    h = Harness()
    orch = Orchestrator(belief_store=b, harness=h, state_dir="state/purple_orch")
    orch.interventional_update_skill("s_purple", success=True, is_agent_action=True)
    agent_blocked = "s_purple" not in b.skill_alpha and "s_purple" not in b.skill_beta
    orch.interventional_update_skill("s_purple", success=True, is_agent_action=False)
    external_ok = b.skill_alpha.get("s_purple", 0) >= 2.0
    ok = agent_blocked and external_ok
    return CheckResult(
        name="orchestrator_skips_agent_updates",
        passed=ok,
        detail=f"agent_blocked={agent_blocked} external_alpha={b.skill_alpha.get('s_purple')}",
    )


def check_session_tag_kinds() -> CheckResult:
    from core.session_memory import SessionMemory

    sm = SessionMemory(root="state/purple_sessions")
    s = sm.start()
    s.tag_agent("assistant", "I propose X")
    s.tag_external("tool", "score=0.9", tool_name="eval")
    kinds = {e.kind for e in s.events}
    ok = kinds == {"agent_intervention", "external_observation"}
    sm.end()
    return CheckResult(name="session_tag_kinds", passed=ok, detail=f"kinds={kinds}")


def check_hard_commit_requires_certificate() -> CheckResult:
    from core.harness import Harness
    from core.belief_store import BeliefStore
    from core.commit import apply_candidate_patch
    from audit.schema import CertificateRecord

    h = Harness()
    b = BeliefStore()
    cert = CertificateRecord.create(
        candidate_id="purple",
        decision="hard_commit",
        e_wealth=10.0,
        e_n=12,
        alpha_spent=0.01,
    )
    apply_candidate_patch(h, b, {"skills": {"p": {"description": "purple"}}}, cert)
    ok = h.version == 1 and b.version == 1 and h.last_certificate_id == cert.certificate_id
    return CheckResult(
        name="hard_commit_certificate",
        passed=ok,
        detail=f"harness_v={h.version} belief_v={b.version} cert_set={bool(h.last_certificate_id)}",
    )


def check_evidence_filters_agent() -> CheckResult:
    from core.session_memory import Session
    from core.evidence import extract_evidence_from_session, apply_evidence_to_belief
    from core.belief_store import BeliefStore

    s = Session.create()
    s.tag_agent("assistant", "success claimed")
    s.events[-1].metadata["skill_id"] = "s1"
    s.events[-1].metadata["success"] = True
    s.tag_external("tool", "verified success", tool_name="t")
    s.events[-1].metadata["skill_id"] = "s1"
    s.events[-1].metadata["success"] = True
    recs = extract_evidence_from_session(s, default_skill_id="s1")
    b = BeliefStore()
    n = apply_evidence_to_belief(b, recs)
    ok = n == 1 and b.skill_alpha.get("s1", 1.0) >= 2.0
    return CheckResult(
        name="evidence_filters_agent",
        passed=ok,
        detail=f"updates={n} alpha={b.skill_alpha.get('s1')}",
    )


def check_conformal_gate_metrics() -> CheckResult:
    import numpy as np
    from bayesian_core.conformal import gate_metrics

    m = gate_metrics(np.array([0.05, 0.1, 0.12, 0.2]), test_score=0.1, alpha=0.05, method="split")
    ok = "width" in m and "p_value" in m and m["width"] >= 0
    return CheckResult(name="conformal_gate_metrics", passed=ok, detail=str({k: m[k] for k in ("width", "p_value", "method")}))


def run_purple_suite() -> PurpleReport:
    report = PurpleReport()
    report.results.append(check_orchestrator_skips_agent_updates())
    report.results.append(check_session_tag_kinds())
    report.results.append(check_hard_commit_requires_certificate())
    report.results.append(check_evidence_filters_agent())
    report.results.append(check_conformal_gate_metrics())
    return report


def main() -> None:
    print(run_purple_suite().summary())


if __name__ == "__main__":
    main()
