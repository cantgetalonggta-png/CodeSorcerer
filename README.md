# CodeSorcerer

**Custom Agent Framework & Persistent Workspace — Orchestrated by Grok**

Bayesian autonomous agent with interventional updates, anytime-valid commit gates, swarm multi-agent layer, skill packs, PDF tools, and a local dashboard.

---

## Core principles

1. Frozen base model + mutable harness  
2. Only **external** observations update posteriors  
3. GRO e-process + conformal + **strict canary** before hard commit  
4. Full audit trail  

---

## Bayesian + canary safety (stricter defaults)

`config/default.yaml`:

- `alpha_total: 0.03`
- `conformal_alpha: 0.05`, `max_conformal_width: 0.18`
- `canary_success_threshold: 0.72`, `canary_min_sessions: 8`, `canary_extra_sessions: 20`

Inference stack L0–L4: `bayesian_core/inference_layers.py`  
Methods: `architecture/conformal_methods.md`, `architecture/bayesian_canary_safety.md`

Conformal API: split, jackknife+ approx, weighted residuals, `gate_metrics()`.

---

## Swarm → Orchestrator auto skill patches

```python
from swarm import SwarmRunner, swarm_to_candidate_patch
from core import Orchestrator, BeliefStore, Harness

swarm = SwarmRunner(llm=create_llm())
result = swarm.run_sequential(task, context=pdf_text)
# Orchestrator.evaluate_swarm_patch(result, instances, evaluate_fn, session_fn_for_canary=...)
```

`swarm/auto_patch.py` builds `candidate_patch` from agent outputs; Orchestrator runs e-process → canary → hard-commit merge.

---

## PDF tools

```python
from tools.pdf_tools import extract_pdf_text, extract_many
r = extract_pdf_text("doc.pdf")
ctx = extract_many(["a.pdf", "b.pdf"])  # swarm context
```

Requires `pypdf` (in requirements.txt).

---

## Dashboard UI

```bash
python -m examples.full_cycle   # populate state/
python -m dashboard.app         # http://127.0.0.1:8765/
```

Stdlib HTTP server: HTML status + `/api/belief`, `/api/harness`, `/api/audit`.  
Details: `architecture/dashboard_ui.md`

---

## Production LLM

`llm.factory.create_llm()` — env `CODESORCERER_LLM_PROVIDER=echo|openai|anthropic|local`  
Guide: `architecture/production_llm_wiring.md`

---

## Quick start

```bash
pip install -r requirements.txt
python tests/test_core.py
python -m examples.swarm_demo
python -m examples.orchestrated_canary
python -m dashboard.app
```

Repo: https://github.com/cantgetalonggta-png/CodeSorcerer
