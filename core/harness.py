"""
Versioned Harness – mutable container for skills, memory references,
tools, ontology, and policy fragments.

Only mutated under a valid certificate (hard commit).
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
import json
from pathlib import Path
from datetime import datetime, timezone
import copy


@dataclass
class Harness:
    version: int = 0
    skills: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    memory_refs: List[str] = field(default_factory=list)
    tools: Dict[str, Any] = field(default_factory=dict)
    policy_fragments: Dict[str, str] = field(default_factory=dict)
    ontology_snapshot: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_certificate_id: Optional[str] = None

    def bump(self, certificate_id: str) -> None:
        self.version += 1
        self.last_certificate_id = certificate_id
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def add_skill(self, skill_id: str, content: Dict[str, Any]) -> None:
        self.skills[skill_id] = content

    def set_policy(self, name: str, text: str) -> None:
        self.policy_fragments[name] = text

    def snapshot(self) -> "Harness":
        return copy.deepcopy(self)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str | Path) -> "Harness":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)
