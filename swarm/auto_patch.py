"""
Swarm → Orchestrator auto skill patches.

Turns SwarmResult synthesis / per-agent outputs into a candidate_patch
dict suitable for Orchestrator.evaluate_candidate + hard-commit merge.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from swarm.runner import SwarmResult
from swarm.agents import AgentRole


def _skill_from_agent(agent_name: str, content: str, skill_ids: List[str]) -> Dict[str, Any]:
    primary = skill_ids[0] if skill_ids else agent_name.lower()
    return {
        "description": f"Auto skill from swarm agent {agent_name}",
        "content": content[:4000],
        "source_agent": agent_name,
        "linked_skills": skill_ids,
    }


def swarm_to_candidate_patch(
    swarm_result: SwarmResult,
    roster: Optional[List[AgentRole]] = None,
    include_synthesis_policy: bool = True,
) -> Dict[str, Any]:
    """
    Build candidate_patch:
    {
      "skills": { skill_id: {description, content, ...}, ... },
      "policy_fragments": { ... }
    }
    """
    skills: Dict[str, Any] = {}
    for r in swarm_result.results:
        if r.agent_name == "Synthesizer":
            continue
        sid = (r.skill_ids[0] if r.skill_ids else r.agent_name.lower())
        # namespace per agent to avoid clobbering shared skill ids
        key = f"{sid}__{r.agent_name.lower()}"
        skills[key] = _skill_from_agent(r.agent_name, r.content, r.skill_ids)

    policy: Dict[str, str] = {}
    if include_synthesis_policy and swarm_result.synthesis:
        policy["swarm_synthesis"] = swarm_result.synthesis[:3000]
        policy["evidence_policy"] = (
            "Only external observations update beliefs. "
            "Agent and swarm text are interventions until verified."
        )

    return {
        "skills": skills,
        "policy_fragments": policy,
        "metadata": {
            "task": swarm_result.task,
            "n_agents": len(swarm_result.results),
            "source": "swarm_auto_patch",
        },
    }


def should_propose_patch(swarm_result: SwarmResult, min_agents: int = 3) -> bool:
    usable = [r for r in swarm_result.results if r.content and r.agent_name != "Synthesizer"]
    return len(usable) >= min_agents and bool(swarm_result.synthesis.strip())
