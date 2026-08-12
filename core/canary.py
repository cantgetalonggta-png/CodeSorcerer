"""
Canary runner

When the soft-commit gate fires, a candidate is promoted to a canary harness.
This module actually runs extra evaluation sessions under that canary
and reports aggregated outcomes back to the orchestrator.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from pathlib import Path
import json
from datetime import datetime, timezone

from core.harness import Harness


@dataclass
class CanaryResult:
    canary_id: str
    candidate_id: str
    n_sessions: int
    successes: int
    failures: int
    scores: List[float] = field(default_factory=list)
    started_at: str = ""
    finished_at: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        if self.n_sessions == 0:
            return 0.0
        return self.successes / self.n_sessions


class CanaryRunner:
    def __init__(self, canary_dir: str | Path = "state/canaries"):
        self.canary_dir = Path(canary_dir)
        self.canary_dir.mkdir(parents=True, exist_ok=True)

    def deploy_canary(
        self,
        candidate_id: str,
        base_harness: Harness,
        candidate_patch: Dict[str, Any],
        certificate_id: str,
    ) -> Harness:
        """Create a canary harness by applying the candidate patch."""
        canary = base_harness.snapshot()
        # Apply patch (skills / policy fragments)
        for skill_id, content in candidate_patch.get("skills", {}).items():
            canary.add_skill(skill_id, content)
        for name, text in candidate_patch.get("policy_fragments", {}).items():
            canary.set_policy(name, text)
        canary.metadata["canary_for"] = candidate_id
        canary.metadata["certificate_id"] = certificate_id
        canary.metadata["canary_created_at"] = datetime.now(timezone.utc).isoformat()

        path = self.canary_dir / f"canary_{candidate_id}_{certificate_id[:8]}.json"
        canary.save(path)
        return canary

    def run_sessions(
        self,
        canary: Harness,
        n_sessions: int,
        session_fn: Callable[[Harness, int], tuple[bool, float]],
    ) -> CanaryResult:
        """
        Execute extra sessions under the canary harness.

        session_fn(harness, session_idx) -> (success: bool, score: float)
        """
        canary_id = canary.metadata.get("certificate_id", "unknown")[:8]
        candidate_id = canary.metadata.get("canary_for", "unknown")
        result = CanaryResult(
            canary_id=canary_id,
            candidate_id=candidate_id,
            n_sessions=0,
            successes=0,
            failures=0,
            started_at=datetime.now(timezone.utc).isoformat(),
        )

        for i in range(n_sessions):
            success, score = session_fn(canary, i)
            result.n_sessions += 1
            result.scores.append(score)
            if success:
                result.successes += 1
            else:
                result.failures += 1

        result.finished_at = datetime.now(timezone.utc).isoformat()
        # Persist result
        out = self.canary_dir / f"result_{candidate_id}_{canary_id}.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump({
                "canary_id": result.canary_id,
                "candidate_id": result.candidate_id,
                "n_sessions": result.n_sessions,
                "successes": result.successes,
                "failures": result.failures,
                "success_rate": result.success_rate,
                "scores": result.scores,
                "started_at": result.started_at,
                "finished_at": result.finished_at,
                "metadata": result.metadata,
            }, f, indent=2)
        return result
