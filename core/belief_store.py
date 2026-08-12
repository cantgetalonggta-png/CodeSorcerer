"""
BeliefStore – persistent container for posterior sufficient statistics
and versioned self.* state summaries.

This is the source of truth that the hierarchical model reads from
and that the commit gate writes into after a hard commit.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional
import json
from pathlib import Path
from datetime import datetime, timezone


@dataclass
class BeliefStore:
    skill_alpha: Dict[str, float] = field(default_factory=dict)
    skill_beta: Dict[str, float] = field(default_factory=dict)
    mem_alpha: Dict[str, float] = field(default_factory=dict)
    mem_beta: Dict[str, float] = field(default_factory=dict)
    mu_lr: float = -3.0
    sigma_lr: float = 0.6
    policy_strength: Dict[str, float] = field(default_factory=dict)
    conf_scale: Dict[str, float] = field(default_factory=dict)
    n_obs_total: int = 0
    version: int = 0
    last_certificate_id: Optional[str] = None
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def update_skill(self, skill_id: str, success: bool) -> None:
        if success:
            self.skill_alpha[skill_id] = self.skill_alpha.get(skill_id, 1.0) + 1.0
        else:
            self.skill_beta[skill_id] = self.skill_beta.get(skill_id, 1.0) + 1.0
        self.n_obs_total += 1
        self._touch()

    def update_memory(self, mem_id: str, success: bool) -> None:
        if success:
            self.mem_alpha[mem_id] = self.mem_alpha.get(mem_id, 1.0) + 1.0
        else:
            self.mem_beta[mem_id] = self.mem_beta.get(mem_id, 1.0) + 1.0
        self.n_obs_total += 1
        self._touch()

    def set_certificate(self, cert_id: str) -> None:
        self.last_certificate_id = cert_id
        self.version += 1
        self._touch()

    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str | Path) -> "BeliefStore":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)

    def skill_mean(self, skill_id: str) -> float:
        a = self.skill_alpha.get(skill_id, 1.0)
        b = self.skill_beta.get(skill_id, 1.0)
        return a / (a + b)
