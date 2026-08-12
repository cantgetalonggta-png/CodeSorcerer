"""
Swarm multi-agent layer — role definitions.

Aligned with Drive advanced-swarm style roles (MemoryVault, PatternRecognition, etc.)
but constrained by CodeSorcerer safety: interventional evidence only for belief updates,
and no offensive tooling.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AgentRole:
    name: str
    role: str
    style: str
    skill_ids: List[str] = field(default_factory=list)
    system_prompt: str = ""

    def build_system_prompt(self) -> str:
        base = self.system_prompt or (
            f"You are {self.name}. Role: {self.role}. "
            f"Respond in a {self.style} manner. "
            "Treat agent-generated text as interventions, not external evidence. "
            "Prefer primary sources and tool/environment results."
        )
        if self.skill_ids:
            base += f" Preferred skills: {', '.join(self.skill_ids)}."
        return base


# Default swarm roster (investigation / research oriented)
DEFAULT_ROSTER: List[AgentRole] = [
    AgentRole(
        name="MemoryVault",
        role="Maintains permanent memory of directives and investigation breadcrumbs. Never confuses agent notes with external evidence.",
        style="Clinical, precise, retentive",
        skill_ids=["memory_vault", "extract_citations"],
    ),
    AgentRole(
        name="PatternRecognition",
        role="Identifies patterns across documents: names, dates, organizations. Connects only with evidence.",
        style="Analytical, strategic, logical",
        skill_ids=["pattern_link", "entity_resolution", "timeline_builder"],
    ),
    AgentRole(
        name="SourceAnalyst",
        role="Grades sources and extracts citations. Blocks weak sources from belief updates.",
        style="Skeptical, forensic, careful",
        skill_ids=["source_grading", "extract_citations", "contradiction_scan"],
    ),
    AgentRole(
        name="DocumentForensics",
        role="Digests PDF/extracted text, flags OCR issues, structures claims with locators.",
        style="Detail-obsessed, cold, precise",
        skill_ids=["pdf_digest", "summarize"],
    ),
    AgentRole(
        name="QueryPlanner",
        role="Builds lawful public search query plans from keywords and filters. Does not execute attacks.",
        style="Methodical, exhaustive, disciplined",
        skill_ids=["dork_builder"],
    ),
    AgentRole(
        name="ComplianceGate",
        role="Enforces interventional discipline and refuses to treat agent self-talk as evidence.",
        style="Strict, disciplined",
        skill_ids=["verify_claim", "source_grading"],
    ),
    AgentRole(
        name="Synthesizer",
        role="Merges agent outputs into a single structured report with confidence and open questions.",
        style="Clear, structured, balanced",
        skill_ids=["summarize", "contradiction_scan"],
    ),
]


def get_roster(names: Optional[List[str]] = None) -> List[AgentRole]:
    if not names:
        return list(DEFAULT_ROSTER)
    wanted = set(names)
    return [a for a in DEFAULT_ROSTER if a.name in wanted]
