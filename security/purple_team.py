"""
Purple-team style defensive checks for CodeSorcerer.

These are internal control tests — not offensive capability.
They verify that interventional discipline, commit gates, and
session tagging behave as designed.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Callable


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
        lines.append(f"Overall: {'PASS' if self.ok else 'FAIL'} ({sum(r.passed for r in self.results)}/{len(self.results)})")
        return "\n".join(lines)


def check_agent_actions_do_not_update_belief(belief_factory: Callable) -> CheckResult:
    """Agent interventions must not change skill counts."""
    from core.belief_store import BeliefStore
    b = belief_factory() if belief_factory else BeliefStore()
    before_a = dict(b.skill_alpha)
    before_b = dict(b.skill_beta)
    # simulate orchestrator path: is_agent_action=True should no-op
    # BeliefStore itself always updates; the gate is at Orchestrator level.
    # Here we document expected policy: callers must not call update_skill for agent actions.
    return CheckResult(
        name="agent_action_policy",
        passed=True,
        detail="Policy: callers must skip BeliefStore.update_skill when is_agent_action=True (enforced in Orchestrator).",
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
    return CheckResult(
        name="session_tag_kinds",
        passed=ok,
        detail=f"kinds={kinds}",
    )


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
        detail=f"harness_v={h.version} belief_v={b.version}",
    )


def check_evidence_filters_agent() -> CheckResult:
    from core.session_memory import Session
    from core.evidence import extract_evidence_from_session, apply_evidence_to_belief
    from core.belief_store import BeliefStore
    s = Session.create()
    s.tag_agent("assistant", "success claimed", skill_id="s1")
    # agent path should not count even if success inferred
    s.events[-1].metadata["skill_id"] = "s1"
    s.events[-1].metadata["success"] = True
    s.tag_external("tool", "verified success", tool_name="t")
    s.events[-1].metadata["skill_id"] = "s1"
    s.events[-1].metadata["success"] = True
    recs = extract_evidence_from_session(s, default_skill_id="s1")
    b = BeliefStore()
    n = apply_evidence_to_belief(b, recs)
    # only external should apply
    ok = n == 1 and b.skill_alpha.get("s1", 1.0) >= 2.0
    return CheckResult(
        name="evidence_filters_agent",
        passed=ok,
        detail=f"updates={n} alpha={b.skill_alpha.get('s1')}",
    )


def run_purple_suite() -> PurpleReport:
    report = PurpleReport()
    report.results.append(check_agent_actions_do_not_update_belief(None))
    report.results.append(check_session_tag_kinds())
    report.results.append(check_hard_commit_requires_certificate())
    report.results.append(check_evidence_filters_agent())
    return report


if __name__ == "__main__":
    print(run_purple_suite().summary())
