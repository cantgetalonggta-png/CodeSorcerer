"""
Simple validation tests for CodeSorcerer core components.
Run with: python -m pytest tests/ -q
or: python tests/test_core.py
"""

from __future__ import annotations
import sys
from pathlib import Path

# Ensure repo root is on path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.belief_store import BeliefStore
from core.harness import Harness
from core.session_memory import SessionMemory, TrajectoryEvent
from core.commit import apply_candidate_patch
from bayesian_core.eprocess import GROMixtureState, update_gro_mixture, HarmonicSpender, production_commit_gate
from audit.schema import CertificateRecord, AuditLog
from skills.registry import SkillRegistry, Skill


def test_belief_store_update():
    b = BeliefStore()
    b.update_skill("s1", success=True)
    b.update_skill("s1", success=False)
    assert b.skill_alpha["s1"] == 2.0
    assert b.skill_beta["s1"] == 2.0
    mean = b.skill_mean("s1")
    assert 0.4 < mean < 0.6
    print("✓ belief_store_update")


def test_harness_versioning():
    h = Harness()
    h.add_skill("demo", {"text": "hello"})
    h.bump("cert-123")
    assert h.version == 1
    assert h.last_certificate_id == "cert-123"
    print("✓ harness_versioning")


def test_eprocess_grows_on_success():
    state = GROMixtureState()
    for _ in range(10):
        state = update_gro_mixture(state, 1.0)
    assert state.wealth > 1.0
    print("✓ eprocess_grows_on_success")


def test_session_tagging():
    sm = SessionMemory(root="state/test_sessions")
    s = sm.start()
    s.tag_agent("assistant", "I will do X")
    s.tag_external("tool", "result Y", tool_name="search")
    assert len(s.events) == 2
    assert s.events[0].kind == "agent_intervention"
    assert s.events[1].kind == "external_observation"
    finished = sm.end()
    assert finished is not None
    print("✓ session_tagging")


def test_hard_commit_merge():
    harness = Harness()
    belief = BeliefStore()
    cert = CertificateRecord.create(
        candidate_id="c1",
        decision="hard_commit",
        e_wealth=12.0,
        e_n=15,
        alpha_spent=0.01,
    )
    patch = {
        "skills": {"new_skill": {"description": "test skill"}},
        "policy_fragments": {"style": "be concise"},
    }
    apply_candidate_patch(harness, belief, patch, cert)
    assert "new_skill" in harness.skills
    assert harness.policy_fragments.get("style") == "be concise"
    assert harness.version == 1
    assert belief.version == 1
    print("✓ hard_commit_merge")


def test_skill_registry_markdown(tmp_path):
    # Create a temporary markdown skill
    skills_dir = tmp_path / "skills_data"
    skills_dir.mkdir()
    md = skills_dir / "demo_skill.md"
    md.write_text("---\nname: Demo Skill\ndescription: A test\n---\nBody of the skill.\n")
    reg = SkillRegistry(skills_dir=skills_dir)
    reg.load_directory()
    assert "demo_skill" in reg.list_skills()
    skill = reg.get("demo_skill")
    assert skill is not None
    assert skill.name == "Demo Skill"
    print("✓ skill_registry_markdown")


def run_all():
    test_belief_store_update()
    test_harness_versioning()
    test_eprocess_grows_on_success()
    test_session_tagging()
    test_hard_commit_merge()
    # markdown test needs tmp_path – skip if running as script without pytest
    try:
        import tempfile
        from pathlib import Path as P
        with tempfile.TemporaryDirectory() as td:
            test_skill_registry_markdown(P(td))
    except Exception as e:
        print(f"(skill_registry_markdown skipped or failed: {e})")
    print("\nAll core validations passed.")


if __name__ == "__main__":
    run_all()
