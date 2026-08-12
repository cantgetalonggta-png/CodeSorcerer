"""
Persistent session memory + trajectory tagging.

Every event is tagged as:
  - agent_intervention  (produced by the agent)
  - external_observation (environment / user / tool result)
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Literal
from datetime import datetime, timezone
from pathlib import Path
import json
import uuid

EventKind = Literal["agent_intervention", "external_observation", "system"]


@dataclass
class TrajectoryEvent:
    event_id: str
    timestamp: str
    kind: EventKind
    role: str                          # user | assistant | tool | system
    content: str
    tool_name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def create(
        kind: EventKind,
        role: str,
        content: str,
        tool_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "TrajectoryEvent":
        return TrajectoryEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            kind=kind,
            role=role,
            content=content,
            tool_name=tool_name,
            metadata=metadata or {},
        )


@dataclass
class Session:
    session_id: str
    started_at: str
    events: List[TrajectoryEvent] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    ended_at: Optional[str] = None

    def add(self, event: TrajectoryEvent) -> None:
        self.events.append(event)

    def tag_agent(self, role: str, content: str, **meta) -> TrajectoryEvent:
        ev = TrajectoryEvent.create("agent_intervention", role, content, metadata=meta)
        self.add(ev)
        return ev

    def tag_external(self, role: str, content: str, tool_name: Optional[str] = None, **meta) -> TrajectoryEvent:
        ev = TrajectoryEvent.create("external_observation", role, content, tool_name=tool_name, metadata=meta)
        self.add(ev)
        return ev

    def close(self) -> None:
        self.ended_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "metadata": self.metadata,
            "events": [asdict(e) for e in self.events],
        }

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def create(cls, metadata: Optional[Dict[str, Any]] = None) -> "Session":
        return cls(
            session_id=str(uuid.uuid4()),
            started_at=datetime.now(timezone.utc).isoformat(),
            metadata=metadata or {},
        )


class SessionMemory:
    def __init__(self, root: str | Path = "state/sessions"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.current: Optional[Session] = None

    def start(self, metadata: Optional[Dict[str, Any]] = None) -> Session:
        self.current = Session.create(metadata=metadata)
        return self.current

    def end(self) -> Optional[Session]:
        if self.current is None:
            return None
        self.current.close()
        path = self.root / f"{self.current.session_id}.json"
        self.current.save(path)
        finished = self.current
        self.current = None
        return finished
