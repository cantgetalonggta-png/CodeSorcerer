# CodeSorcerer

**Custom Agent Framework & Persistent Workspace — Orchestrated by Grok**

A production-oriented **Bayesian autonomous agent** system. The agent improves its own skills, memory, policy, and learning dynamics under **causal** (interventional) updates and **anytime-valid statistical certificates**. Every live change to the agent’s state is gated; self-delusion is structurally prevented.

---

## Core Principles

1. **Frozen base model + mutable harness** — weights stay fixed; skills, memory, policy, and beliefs evolve.
2. **Interventional discipline** — agent-generated tokens/actions are *interventions*, not ordinary evidence. Only external observations update posteriors.
3. **Anytime-valid certificates** — GRO mixture e-processes + harmonic family-wise spending control false commits under optional stopping.
4. **Soft canary → hard commit** — candidates first run extra live sessions under a canary harness; only then can they be merged.
5. **Auditability** — every certificate, e-process path, and commit is logged and replayable.

---

## Architecture (Layers)

```
L3  Loop Controllers + Gates     (GRO e-process, conformal, soft/hard commit)
L2  Versioned Harness            (skills, memory refs, policy, ontology snapshot)
L1  Steering / retrieval         (future adapter hooks)
L0  Frozen Base LLM              (EchoLLM / OpenAI / Anthropic / local)
```

Cross-cutting:
- **BeliefStore** — sufficient statistics for all `self.*` posteriors
- **SessionMemory** — trajectory tagging (`agent_intervention` vs `external_observation`)
- **SkillRegistry** — loadable Markdown + Python skills
- **Evaluator** — scores candidates on instances
- **AuditLog** — certificates and replay

---

## Module Map (what each service does)

### `core/` — Runtime spine

| Module | Role |
|--------|------|
| `belief_store.py` | Persistent Beta-style counts + hyper-parameters for skills, memory, LR, policy, confidence. Source of truth for posteriors. |
| `harness.py` | Versioned container for skills, policy fragments, memory refs, ontology snapshot. Only mutated under a valid certificate. |
| `orchestrator.py` | Full improvement cycle: evaluate candidate → e-process + conformal gate → soft canary (real extra sessions) or hard commit (real patch merge) → persist. |
| `session_memory.py` | Creates sessions, tags every event as agent vs external, persists trajectories. |
| `canary.py` | Deploys a canary harness and **actually runs** extra evaluation sessions; returns success rate. |
| `commit.py` | **Hard-commit path**: merges candidate skills/policy/memory into the live harness and bumps versions under a certificate. |
| `evidence.py` | Walks a session trajectory and extracts only *external* evidence records safe for Bayesian updates. |
| `evaluator.py` | `Evaluator` interface + `KeywordMatchEvaluator` + `ThresholdSuccessEvaluator` + helper to build canary `session_fn`. |

### `bayesian_core/` — Statistical engine

| Module | Role |
|--------|------|
| `hierarchical_model.py` | Joint NumPyro hierarchical model over skills, memory, learning-rate, policy strength, confidence. SVI-friendly. |
| `interventional.py` | Interventional loss mask (PyTorch) + interventional Bayesian count update (no gradient/count from agent tokens). |
| `eprocess.py` | GRO mixture e-variable + `HarmonicSpender` + `production_commit_gate`. Anytime-valid Type-I control. |
| `conformal.py` | Nonconformity scores, split-conformal intervals, conformal p-values for soft-commit conservatism. |

### `commit_gate/`

| Module | Role |
|--------|------|
| `soft_hard.py` | Combines e-process decision with conformal p-value/width into `hard_commit` / `soft_canary` / `reject` / `continue`. |

### `skills/` + `skills_data/`

| Piece | Role |
|--------|------|
| `skills/registry.py` | Loads **Markdown** skills (YAML-like front-matter) and **Python** skills (`run` / `execute` entrypoints). |
| `skills_data/summarize.md` | Concise summary skill; prefers external evidence. |
| `skills_data/verify_claim.md` | Claim verification skill; separates agent statements from external observations. |
| `skills_data/echo_tool.py` | Sample Python skill — echoes input and flags external-looking content. |
| `skills_data/score_keywords.py` | Python skill that returns keyword-coverage ratio (used by evaluators). |

### `llm/`

| Module | Role |
|--------|------|
| `base.py` | `BaseLLM` ABC, `EchoLLM` (local testing), `ToolSpec`, `Message`, `LLMResponse`, `ToolRouter`. |
| `adapters.py` | Thin **OpenAI**, **Anthropic**, and **local OpenAI-compatible** (Ollama/vLLM/llama.cpp) adapters. |

### `audit/`

| Module | Role |
|--------|------|
| `schema.py` | `CertificateRecord` + `AuditLog` with JSON persistence and replay summary. |

### `ontology/` + `federation/`

| Module | Role |
|--------|------|
| `ontology/sync.py` | Bidirectional stubs: ontology nodes ↔ posterior keys; push posteriors back into ontology metadata. |
| `federation/posterior_share.py` | Multi-agent belief packets + Beta-count merge + certificate aggregation. |

### `architecture/`

| Doc | Content |
|-----|---------| 
| `reference_architecture.md` | Layer diagram and safety invariants. |
| `combined_protocol.md` | Full cycle protocol and guarantee table. |

### `config/`

| File | Role |
|------|------|
| `default.yaml` | Default alpha, conformal settings, paths, canary session count. |

### `examples/`

| Script | What it demonstrates |
|--------|----------------------|
| `basic_loop.py` | Minimal e-process + soft-commit decision + audit. |
| `full_cycle.py` | BeliefStore + Harness + Orchestrator smoke run. |
| `orchestrated_canary.py` | **Tight end-to-end**: SkillRegistry + KeywordMatchEvaluator + Orchestrator with real canary sessions and hard-commit merge. |

### `tests/` + CI

| Piece | Role |
|--------|------|
| `tests/test_core.py` | Validates belief updates, harness versioning, e-process growth, session tagging, hard-commit merge, skill loading. |
| `.github/workflows/ci.yml` | GitHub Actions: install deps, run validation script, smoke example, on push/PR to `main`. |

---

## End-to-end flow (one improvement cycle)

1. **Session** — `SessionMemory` records events tagged `agent_intervention` or `external_observation`.
2. **Evidence extraction** — `extract_evidence_from_session` keeps only external records.
3. **Interventional update** — `apply_evidence_to_belief` / `BeliefStore.update_skill` (agent actions never increment counts).
4. **Candidate generation** — propose skill/policy patches (from failures, low posterior reliability, etc.).
5. **Evaluation** — `Evaluator.score` on paired instances; outcomes feed the GRO mixture e-process.
6. **Gate** — e-process + conformal → `hard_commit` | `soft_canary` | `reject` | `continue`.
7. **Soft canary** — `CanaryRunner` deploys a canary harness and runs extra sessions; may auto-promote.
8. **Hard commit** — `apply_candidate_patch` merges skills/policy into the live `Harness` and bumps versions under the certificate.
9. **Audit + persist** — certificate logged; BeliefStore, Harness, AuditLog written under `state/`.

---

## Quick Start

```bash
git clone https://github.com/cantgetalonggta-png/CodeSorcerer.git
cd CodeSorcerer
pip install -r requirements.txt

# Validation
python tests/test_core.py

# Examples
python -m examples.basic_loop
python -m examples.full_cycle
python -m examples.orchestrated_canary
```

State (belief store, harness, audit log, canaries, sessions) is written under `./state/`.

### Optional LLM backends

```bash
# OpenAI
export OPENAI_API_KEY=...
# Anthropic
export ANTHROPIC_API_KEY=...
# Local (Ollama example)
# run ollama serve, then use LocalOpenAICompatibleAdapter(base_url="http://localhost:11434/v1", model="llama3.2")
```

---

## Skills currently shipped

| Skill ID | Type | Purpose |
|----------|------|---------|
| `summarize` | Markdown | Concise summaries that privilege external evidence |
| `verify_claim` | Markdown | Claim checking with agent vs external separation |
| `echo_tool` | Python | Echo + external-evidence heuristic |
| `score_keywords` | Python | Keyword coverage ratio for evaluators |

Add more by dropping `.md` or `.py` files into `skills_data/` and calling `SkillRegistry.load_directory()`.

---

## Status

- Statistical core (interventional updates, GRO e-process, conformal, hierarchical NumPyro model) — **in place**
- Persistence (BeliefStore, Harness, Session, Audit) — **in place**
- Real canary runner + hardened hard-commit — **in place**
- Skill registry + sample skills — **in place**
- Evaluator + orchestrated example — **in place**
- LLM adapters (Echo / OpenAI / Anthropic / local) — **in place**
- CI on GitHub Actions — **in place**

Ready for real task evaluators, production LLM wiring, and larger skill libraries.
