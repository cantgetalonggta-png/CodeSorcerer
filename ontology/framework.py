"""
Ontology framework for CodeSorcerer autonomous agent.

Extends ontology/sync.py with validation, relation integrity, and
export for harness snapshots.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from ontology.sync import Ontology, OntologyNode, ontology_to_model_config, push_posteriors_to_ontology


ALLOWED_TYPES = {"skill", "memory_entry", "policy_fragment", "value", "entity", "source", "event"}


@dataclass
class OntologyIssue:
    severity: str  # error | warning
    message: str


def validate_ontology(ontology: Ontology) -> List[OntologyIssue]:
    issues: List[OntologyIssue] = []
    ids = set(ontology.nodes.keys())
    for nid, node in ontology.nodes.items():
        if node.node_type not in ALLOWED_TYPES:
            issues.append(OntologyIssue("warning", f"Unknown node_type {node.node_type} on {nid}"))
        if not node.label:
            issues.append(OntologyIssue("warning", f"Empty label on {nid}"))
    for src, rel, dst in ontology.relations:
        if src not in ids:
            issues.append(OntologyIssue("error", f"Relation src missing: {src}"))
        if dst not in ids:
            issues.append(OntologyIssue("error", f"Relation dst missing: {dst}"))
        if not rel:
            issues.append(OntologyIssue("warning", "Empty relation name"))
    return issues


def add_relation(ontology: Ontology, src: str, rel: str, dst: str) -> None:
    if src not in ontology.nodes or dst not in ontology.nodes:
        raise KeyError("Both endpoints must exist before relating")
    ontology.relations.append((src, rel, dst))


def bootstrap_core_ontology() -> Ontology:
    """Minimal autonomous-agent ontology."""
    o = Ontology()
    for nid, ntype, label in [
        ("skill_root", "skill", "Skill root"),
        ("memory_root", "memory_entry", "Memory root"),
        ("policy_root", "policy_fragment", "Policy root"),
        ("evidence_external", "source", "External evidence class"),
        ("evidence_agent", "source", "Agent intervention class"),
    ]:
        o.add_node(OntologyNode(node_id=nid, node_type=ntype, label=label))
    add_relation(o, "skill_root", "constrained_by", "evidence_external")
    add_relation(o, "memory_root", "must_tag", "evidence_external")
    return o


def ontology_health(ontology: Ontology) -> Dict[str, Any]:
    issues = validate_ontology(ontology)
    return {
        "n_nodes": len(ontology.nodes),
        "n_relations": len(ontology.relations),
        "errors": sum(1 for i in issues if i.severity == "error"),
        "warnings": sum(1 for i in issues if i.severity == "warning"),
        "issues": [{"severity": i.severity, "message": i.message} for i in issues],
        "model_config": ontology_to_model_config(ontology),
    }
