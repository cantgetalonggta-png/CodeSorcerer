"""
Swarm runner — sequential or parallel agent passes over a shared task context.

Uses BaseLLM for generation. Outputs are collected; optional Bayesian canary
path can gate promotion of synthesized policy/skill patches.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import concurrent.futures

from swarm.agents import AgentRole, get_roster, DEFAULT_ROSTER
from llm.base import BaseLLM, Message, EchoLLM


@dataclass
class AgentResult:
    agent_name: str
    content: str
    skill_ids: List[str] = field(default_factory=list)
    raw: Any = None


@dataclass
class SwarmResult:
    task: str
    results: List[AgentResult] = field(default_factory=list)
    synthesis: str = ""

    def by_agent(self) -> Dict[str, str]:
        return {r.agent_name: r.content for r in self.results}


class SwarmRunner:
    def __init__(
        self,
        llm: Optional[BaseLLM] = None,
        roster: Optional[List[AgentRole]] = None,
        max_workers: int = 4,
    ):
        self.llm = llm or EchoLLM()
        self.roster = roster or list(DEFAULT_ROSTER)
        self.max_workers = max_workers

    def _run_one(self, agent: AgentRole, task: str, context: str = "") -> AgentResult:
        messages = [
            Message(role="system", content=agent.build_system_prompt()),
            Message(
                role="user",
                content=(
                    f"Task:\n{task}\n\n"
                    f"Shared context (may include document excerpts):\n{context[:12000]}\n\n"
                    "Respond with structured findings. Label evidence as external vs secondary vs agent."
                ),
            ),
        ]
        resp = self.llm.complete(messages, temperature=0.3, max_tokens=1500)
        return AgentResult(
            agent_name=agent.name,
            content=resp.content,
            skill_ids=list(agent.skill_ids),
            raw=resp.raw,
        )

    def run_sequential(self, task: str, context: str = "") -> SwarmResult:
        out = SwarmResult(task=task)
        for agent in self.roster:
            # Skip Synthesizer until the end
            if agent.name == "Synthesizer":
                continue
            out.results.append(self._run_one(agent, task, context))
        # Synthesis pass
        synth_agents = [a for a in self.roster if a.name == "Synthesizer"]
        if synth_agents:
            bundle = "\n\n".join(f"### {r.agent_name}\n{r.content}" for r in out.results)
            syn = self._run_one(synth_agents[0], task, context=bundle)
            out.results.append(syn)
            out.synthesis = syn.content
        else:
            out.synthesis = out.results[-1].content if out.results else ""
        return out

    def run_parallel(self, task: str, context: str = "") -> SwarmResult:
        workers = [a for a in self.roster if a.name != "Synthesizer"]
        out = SwarmResult(task=task)
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as ex:
            futs = {ex.submit(self._run_one, a, task, context): a for a in workers}
            for fut in concurrent.futures.as_completed(futs):
                out.results.append(fut.result())
        # stable order by roster
        order = {a.name: i for i, a in enumerate(self.roster)}
        out.results.sort(key=lambda r: order.get(r.agent_name, 999))
        synth_agents = [a for a in self.roster if a.name == "Synthesizer"]
        if synth_agents:
            bundle = "\n\n".join(f"### {r.agent_name}\n{r.content}" for r in out.results)
            syn = self._run_one(synth_agents[0], task, context=bundle)
            out.results.append(syn)
            out.synthesis = syn.content
        return out
