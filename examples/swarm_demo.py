"""
Swarm multi-agent demo using EchoLLM (swap create_llm() for production).
"""

from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from llm.factory import create_llm
from swarm.runner import SwarmRunner
from swarm.agents import get_roster
from bayesian_core.inference_layers import describe_stack


def main():
    print(describe_stack())
    print()
    llm = create_llm(provider="echo")
    roster = get_roster(["MemoryVault", "PatternRecognition", "SourceAnalyst", "Synthesizer"])
    swarm = SwarmRunner(llm=llm, roster=roster)
    task = "Build an evidence-aware brief on the provided context. Separate external vs agent claims."
    context = (
        "External observation: tool score=0.82 on keyword coverage. "
        "Secondary report claims event on 2024-06-01. "
        "Agent earlier guessed a different date without source."
    )
    result = swarm.run_sequential(task, context=context)
    print("=== Per-agent outputs ===")
    for r in result.results:
        print(f"\n## {r.agent_name}\n{r.content[:500]}")
    print("\n=== Synthesis ===")
    print(result.synthesis[:1000])


if __name__ == "__main__":
    main()
