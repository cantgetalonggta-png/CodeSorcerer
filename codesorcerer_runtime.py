#!/usr/bin/env python3
"""
CodeSorcerer universal runtime
==============================
Single entrypoint to connect and deploy the stack for investigation workflows
that stay within authorized / public-source scope.

Usage examples
--------------
  # Health + purple controls
  python codesorcerer_runtime.py health

  # Load skills, start session, optional PDF context, run swarm, optional gate
  python codesorcerer_runtime.py investigate --task "Build evidence brief" --pdf doc.pdf

  # Persist state then serve dashboard
  python codesorcerer_runtime.py dashboard

Environment
-----------
  CODESORCERER_LLM_PROVIDER=echo|openai|anthropic|local
  OPENAI_API_KEY / ANTHROPIC_API_KEY / LOCAL_LLM_BASE_URL as needed
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def build_runtime(state_dir: str = "state") -> Dict[str, Any]:
    """Wire every major subsystem into one handle."""
    from core.belief_store import BeliefStore
    from core.harness import Harness
    from core.orchestrator import Orchestrator
    from core.session_memory import SessionMemory
    from core.evaluator import KeywordMatchEvaluator, ThresholdSuccessEvaluator, make_canary_session_fn
    from audit.schema import AuditLog
    from skills.registry import SkillRegistry
    from llm.factory import create_llm
    from swarm.runner import SwarmRunner
    from swarm.agents import get_roster
    from ontology.framework import bootstrap_core_ontology, ontology_health

    state = Path(state_dir)
    state.mkdir(parents=True, exist_ok=True)

    belief_path = state / "belief_store.json"
    harness_path = state / "harness.json"

    belief = BeliefStore.load(belief_path) if belief_path.exists() else BeliefStore()
    harness = Harness.load(harness_path) if harness_path.exists() else Harness()
    audit = AuditLog.from_json(str(state / "audit_log.json")) if (state / "audit_log.json").exists() else AuditLog()

    orch = Orchestrator(
        belief_store=belief,
        harness=harness,
        audit_log=audit,
        alpha_total=0.03,
        state_dir=state_dir,
        canary_extra_sessions=20,
        canary_success_threshold=0.72,
        canary_min_sessions=8,
        conformal_alpha=0.05,
        max_conformal_width=0.18,
    )

    skills = SkillRegistry(skills_dir=str(ROOT / "skills_data"))
    skills.load_directory()

    llm = create_llm()
    swarm = SwarmRunner(llm=llm, roster=get_roster())
    sessions = SessionMemory(root=str(state / "sessions"))
    ontology = bootstrap_core_ontology()

    return {
        "belief": belief,
        "harness": harness,
        "audit": audit,
        "orch": orch,
        "skills": skills,
        "llm": llm,
        "swarm": swarm,
        "sessions": sessions,
        "ontology": ontology,
        "ontology_health": ontology_health(ontology),
        "state_dir": state,
        "evaluator": KeywordMatchEvaluator(),
        "threshold_eval": ThresholdSuccessEvaluator(KeywordMatchEvaluator(), threshold=0.4),
    }


def cmd_health(rt: Dict[str, Any]) -> int:
    from security.purple_team import run_purple_suite
    from bayesian_core.inference_layers import describe_stack

    print(describe_stack())
    print()
    print("Skills loaded:", rt["skills"].list_skills())
    print("Ontology:", rt["ontology_health"])
    print()
    report = run_purple_suite()
    print(report.summary())
    rt["orch"].persist()
    return 0 if report.ok else 1


def cmd_investigate(
    rt: Dict[str, Any],
    task: str,
    pdfs: List[str],
    run_gate: bool,
) -> int:
    from tools.pdf_tools import extract_many
    from swarm.auto_patch import swarm_to_candidate_patch, should_propose_patch
    from core.evaluator import make_canary_session_fn

    context = ""
    if pdfs:
        context = extract_many(pdfs)
        print(f"Loaded {len(pdfs)} PDF(s), context chars={len(context)}")

    session = rt["sessions"].start(metadata={"task": task, "pdfs": pdfs})
    session.tag_external("system", f"Investigation start: {task}")

    result = rt["swarm"].run_sequential(task, context=context)
    session.tag_agent("swarm", result.synthesis[:2000] if result.synthesis else "(empty synthesis)")

    print("\n=== Swarm synthesis ===")
    print(result.synthesis[:3000] if result.synthesis else "(none)")

    out_dir = rt["state_dir"] / "investigations"
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "task": task,
        "synthesis": result.synthesis,
        "by_agent": result.by_agent(),
        "skills_loaded": rt["skills"].list_skills(),
    }
    out_path = out_dir / "last_investigation.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")

    if run_gate and should_propose_patch(result, min_agents=3):
        patch = swarm_to_candidate_patch(result)
        instances = [
            {"keywords": ["evidence", "external", "source"], "text": "evidence review"},
            {"keywords": ["claim", "verify", "citation"], "text": "claim check"},
            {"keywords": ["timeline", "entity", "pattern"], "text": "pattern link"},
        ] * 6

        def evaluate_fn(config, instance):
            return rt["evaluator"].score(config, instance)

        session_fn = make_canary_session_fn(rt["threshold_eval"], instances)
        decision = rt["orch"].evaluate_swarm_patch(
            result,
            instances=instances,
            evaluate_fn=evaluate_fn,
            session_fn_for_canary=session_fn,
            min_agents=3,
            candidate_id="investigate_auto",
        )
        print(f"Gate decision: {decision}")
        session.tag_external("gate", f"decision={decision}")
    else:
        print("Gate skipped (use --gate to propose swarm skill patch under canary rules).")

    rt["sessions"].end()
    rt["orch"].persist()
    return 0


def cmd_dashboard() -> int:
    from dashboard.app import main as dash_main

    print("Starting dashboard at http://127.0.0.1:8765/")
    dash_main()
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="CodeSorcerer universal runtime")
    parser.add_argument("command", choices=["health", "investigate", "dashboard", "persist"])
    parser.add_argument("--task", default="Produce an evidence-aware investigation brief.")
    parser.add_argument("--pdf", action="append", default=[], help="PDF path (repeatable)")
    parser.add_argument("--gate", action="store_true", help="Run swarm→Orchestrator canary gate")
    parser.add_argument("--state-dir", default="state")
    args = parser.parse_args(argv)

    if args.command == "dashboard":
        return cmd_dashboard()

    rt = build_runtime(state_dir=args.state_dir)

    if args.command == "health":
        return cmd_health(rt)
    if args.command == "persist":
        rt["orch"].persist()
        print(f"Persisted to {rt['state_dir']}")
        return 0
    if args.command == "investigate":
        return cmd_investigate(rt, task=args.task, pdfs=args.pdf, run_gate=args.gate)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
