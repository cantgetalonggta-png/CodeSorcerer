"""
Hard-commit path

Applies a candidate patch into the live harness and belief store
under a valid certificate. This is the only place that mutates
the production harness.
"""

from __future__ import annotations
from typing import Any, Dict, Optional
from core.harness import Harness
from core.belief_store import BeliefStore
from audit.schema import CertificateRecord


def apply_candidate_patch(
    harness: Harness,
    belief: BeliefStore,
    candidate_patch: Dict[str, Any],
    certificate: CertificateRecord,
) -> Harness:
    """
    Merge candidate_patch into the live harness and bump versions.

    Expected patch shape:
    {
      "skills": {skill_id: { ... content ... }, ...},
      "policy_fragments": {name: text, ...},
      "memory_refs": [id, ...],          # optional
      "belief_updates": {                # optional direct posterior tweaks
          "skill_alpha": {...},
          ...
      }
    }
    """
    # Skills
    for skill_id, content in candidate_patch.get("skills", {}).items():
        harness.add_skill(skill_id, content)

    # Policy fragments
    for name, text in candidate_patch.get("policy_fragments", {}).items():
        harness.set_policy(name, text)

    # Memory refs
    for ref in candidate_patch.get("memory_refs", []):
        if ref not in harness.memory_refs:
            harness.memory_refs.append(ref)

    # Optional direct belief updates (use sparingly)
    bu = candidate_patch.get("belief_updates", {})
    for k, v in bu.get("skill_alpha", {}).items():
        belief.skill_alpha[k] = belief.skill_alpha.get(k, 1.0) + float(v)
    for k, v in bu.get("skill_beta", {}).items():
        belief.skill_beta[k] = belief.skill_beta.get(k, 1.0) + float(v)

    # Version bumps
    harness.bump(certificate.certificate_id)
    belief.set_certificate(certificate.certificate_id)

    return harness
