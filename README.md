# CodeSorcerer

**Custom Agent Framework & Persistent Workspace — Orchestrated by Grok**

Bayesian autonomous agent: interventional updates, anytime-valid gates, strict canary, swarm multi-agent layer, skill packs, PDF tools, ontology framework, local dashboard, and **scoped security tooling** (ROE / threat model / purple-team).

---

## Security (authorized & defensive only)

| Asset | Path |
|-------|------|
| Red-team **ROE template** | `security/roe_template.md` |
| **Threat model** | `security/threat_model.md` |
| **Purple-team checks** | `security/purple_team.py` |
| Public OSINT method skill | `skills_data/packs/research/public_osint_method.md` |

These do **not** assert unrestricted internet access. ROE requires written authorization and explicit scope.

```bash
python -m security.purple_team
python tests/test_security_ontology.py
```

---

## Ontology & autonomy

- `ontology/sync.py` — nodes ↔ posterior keys
- `ontology/framework.py` — bootstrap, validate, health, relations
- Bayesian L0–L4 stack + Orchestrator canary/hard-commit remain the authority for live `self.*` changes

---

## Test status (verified locally)

- `tests/test_core.py` — PASS
- `tests/test_security_ontology.py` — PASS
- `security.purple_team` — PASS 4/4
- Examples: `basic_loop`, `swarm_demo` smoke OK
- Fixed: optional jax/torch imports; `BaseLLM.complete` indentation

```bash
pip install -r requirements-min.txt   # CI / light
# or: pip install -r requirements.txt  # full numpyro/torch
python tests/test_core.py
python tests/test_security_ontology.py
python -m dashboard.app
```

---

## Quick map

| Area | Location |
|------|----------|
| Orchestrator / canary / commit | `core/` |
| GRO / conformal / inference layers | `bayesian_core/` |
| Swarm + auto skill patches | `swarm/` |
| Skills | `skills_data/` (+ packs) |
| PDF tools | `tools/pdf_tools.py` |
| Dashboard | `python -m dashboard.app` |
| LLM factory | `llm.factory.create_llm` |

Repo: https://github.com/cantgetalonggta-png/CodeSorcerer
