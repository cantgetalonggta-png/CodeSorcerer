# CI pipeline automation

Workflow: `.github/workflows/ci.yml`

## Triggers

- `push` to `main`
- `pull_request` targeting `main`

## Matrix

- Python 3.11 and 3.12 on `ubuntu-latest`

## Steps

1. Checkout
2. Setup Python
3. `pip install -r requirements-min.txt` (+ pytest)
4. `python tests/test_core.py`
5. `python tests/test_security_ontology.py`
6. `python -m security.purple_team`
7. `python -m examples.basic_loop`
8. `python -m examples.swarm_demo`

## Why requirements-min.txt

Full `requirements.txt` pulls jax/numpyro/torch (heavy, optional for unit gates).
Light CI validates control-plane logic without GPU/ML stacks.

Hierarchical NumPyro remains available when full requirements are installed; imports are optional so min CI stays green.

## Local parity

```bash
pip install -r requirements-min.txt
python tests/test_core.py
python tests/test_security_ontology.py
python -m security.purple_team
python -m examples.basic_loop
python -m examples.swarm_demo
```

## Dashboard after examples

```bash
python -m examples.full_cycle   # writes state/
python -m dashboard.app         # http://127.0.0.1:8765/
```
