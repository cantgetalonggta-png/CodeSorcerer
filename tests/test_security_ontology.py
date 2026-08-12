"""Security + ontology validation tests."""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from security.purple_team import run_purple_suite
from ontology.framework import bootstrap_core_ontology, ontology_health, validate_ontology
from swarm.auto_patch import swarm_to_candidate_patch, should_propose_patch
from swarm.runner import SwarmResult, AgentResult


def test_purple_suite():
    report = run_purple_suite()
    assert report.ok, report.summary()
    print("✓ purple_suite")


def test_ontology_bootstrap():
    o = bootstrap_core_ontology()
    issues = validate_ontology(o)
    assert not any(i.severity == "error" for i in issues)
    h = ontology_health(o)
    assert h["n_nodes"] >= 5
    assert h["errors"] == 0
    print("✓ ontology_bootstrap")


def test_auto_patch_shape():
    sr = SwarmResult(
        task="t",
        results=[
            AgentResult("MemoryVault", "mem findings", ["memory_vault"]),
            AgentResult("PatternRecognition", "patterns", ["pattern_link"]),
            AgentResult("SourceAnalyst", "grades", ["source_grading"]),
            AgentResult("Synthesizer", "final brief", []),
        ],
        synthesis="final brief",
    )
    assert should_propose_patch(sr, min_agents=3)
    patch = swarm_to_candidate_patch(sr)
    assert "skills" in patch and len(patch["skills"]) >= 3
    assert "policy_fragments" in patch
    print("✓ auto_patch_shape")


def run_all():
    test_purple_suite()
    test_ontology_bootstrap()
    test_auto_patch_shape()
    print("\nSecurity/ontology tests passed.")


if __name__ == "__main__":
    run_all()
