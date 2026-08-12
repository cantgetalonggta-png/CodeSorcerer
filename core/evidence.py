"""
Trajectory → interventional evidence extraction.

Walks a Session / list of TrajectoryEvents and produces
structured evidence records that can safely update the BeliefStore
(only external_observation events contribute success/failure counts).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from core.session_memory import Session, TrajectoryEvent


@dataclass
class EvidenceRecord:
    skill_id: Optional[str]
    success: Optional[bool]
    is_agent_action: bool
    source_event_id: str
    content_preview: str
    metadata: Dict[str, Any] = field(default_factory=dict)


def _infer_success(content: str, metadata: Dict[str, Any]) -> Optional[bool]:
    """Heuristic success detection from content / metadata."""
    if "success" in metadata:
        return bool(metadata["success"])
    if "score" in metadata:
        try:
            return float(metadata["score"]) >= 0.5
        except Exception:
            pass
    lower = content.lower()
    if any(w in lower for w in ["success", "passed", "verified", "ok", "completed"]):
        return True
    if any(w in lower for w in ["fail", "error", "exception", "rejected"]):
        return False
    return None


def extract_evidence_from_session(
    session: Session,
    default_skill_id: Optional[str] = None,
) -> List[EvidenceRecord]:
    """
    Extract evidence records from a finished session.

    - agent_intervention events → is_agent_action=True (do not update posteriors)
    - external_observation events → is_agent_action=False (safe for Bayesian update)
    """
    records: List[EvidenceRecord] = []
    for ev in session.events:
        is_agent = ev.kind == "agent_intervention"
        skill_id = ev.metadata.get("skill_id", default_skill_id)
        success = _infer_success(ev.content, ev.metadata)

        records.append(
            EvidenceRecord(
                skill_id=skill_id,
                success=success,
                is_agent_action=is_agent,
                source_event_id=ev.event_id,
                content_preview=ev.content[:200],
                metadata=dict(ev.metadata),
            )
        )
    return records


def apply_evidence_to_belief(
    belief,
    records: List[EvidenceRecord],
) -> int:
    """
    Apply only external evidence records to the BeliefStore.
    Returns number of updates performed.
    """
    updates = 0
    for rec in records:
        if rec.is_agent_action:
            continue
        if rec.skill_id is None or rec.success is None:
            continue
        belief.update_skill(rec.skill_id, success=rec.success)
        updates += 1
    return updates
