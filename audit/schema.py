"""
Concrete audit-log schema + simple replay tooling.

Every certificate, e-process path, interventional update, and commit
is recorded for later inspection and replay.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import json
import uuid


@dataclass
class CertificateRecord:
    certificate_id: str
    timestamp: str
    candidate_id: str
    decision: str                     # hard_commit | soft_canary | reject | continue
    e_wealth: float
    e_n: int
    alpha_spent: float
    conformal_p: Optional[float] = None
    conformal_width: Optional[float] = None
    notes: str = ""

    @staticmethod
    def create(
        candidate_id: str,
        decision: str,
        e_wealth: float,
        e_n: int,
        alpha_spent: float,
        conformal_p: Optional[float] = None,
        conformal_width: Optional[float] = None,
        notes: str = "",
    ) -> "CertificateRecord":
        return CertificateRecord(
            certificate_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            candidate_id=candidate_id,
            decision=decision,
            e_wealth=e_wealth,
            e_n=e_n,
            alpha_spent=alpha_spent,
            conformal_p=conformal_p,
            conformal_width=conformal_width,
            notes=notes,
        )


@dataclass
class AuditLog:
    records: List[CertificateRecord] = field(default_factory=list)

    def append(self, record: CertificateRecord) -> None:
        self.records.append(record)

    def to_json(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump([asdict(r) for r in self.records], f, indent=2)

    @classmethod
    def from_json(cls, path: str) -> "AuditLog":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        log = cls()
        for item in data:
            log.records.append(CertificateRecord(**item))
        return log

    def filter_by_decision(self, decision: str) -> List[CertificateRecord]:
        return [r for r in self.records if r.decision == decision]

    def replay_summary(self) -> Dict[str, int]:
        summary: Dict[str, int] = {}
        for r in self.records:
            summary[r.decision] = summary.get(r.decision, 0) + 1
        return summary
