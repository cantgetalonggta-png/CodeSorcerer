"""
Ontology ↔ Bayesian network bidirectional sync protocol (stubs).

The ontology defines the entities and relations the agent reasons about.
The Bayesian network (hierarchical model) maintains posteriors over the
reliability / strength of those entities.

This module provides the mapping and update hooks so that:
- Ontology changes can trigger re-parameterization of the Bayesian model
- Posterior updates can be reflected back into ontology annotations
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class OntologyNode:
    node_id: str
    node_type: str          # skill | memory_entry | policy_fragment | value
    label: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    posterior_key: Optional[str] = None   # key into the belief store


@dataclass
class Ontology:
    nodes: Dict[str, OntologyNode] = field(default_factory=dict)
    relations: List[tuple] = field(default_factory=list)  # (src, rel, dst)

    def add_node(self, node: OntologyNode) -> None:
        self.nodes[node.node_id] = node

    def link_to_posterior(self, node_id: str, posterior_key: str) -> None:
        if node_id in self.nodes:
            self.nodes[node_id].posterior_key = posterior_key


def ontology_to_model_config(ontology: Ontology) -> Dict[str, Any]:
    """
    Derive hierarchical model plate sizes and names from the ontology.
    """
    skills = [n for n in ontology.nodes.values() if n.node_type == "skill"]
    memories = [n for n in ontology.nodes.values() if n.node_type == "memory_entry"]
    policies = [n for n in ontology.nodes.values() if n.node_type == "policy_fragment"]

    return {
        "n_skills": len(skills),
        "n_mem": len(memories),
        "n_policy": len(policies),
        "skill_ids": [s.node_id for s in skills],
        "mem_ids": [m.node_id for m in memories],
        "policy_ids": [p.node_id for p in policies],
    }


def push_posteriors_to_ontology(
    ontology: Ontology,
    belief_store: Dict[str, Any],
) -> Ontology:
    """
    Write current posterior summaries back into ontology node metadata.
    """
    for node in ontology.nodes.values():
        if node.posterior_key and node.posterior_key in belief_store:
            node.metadata["posterior"] = belief_store[node.posterior_key]
    return ontology
