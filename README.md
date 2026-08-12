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

Cross-cutting: **BeliefStore**, **SessionMemory**, **SkillRegistry**, **Evaluator**, **AuditLog**.

See also: `architecture/reference_architecture.md`, `architecture/combined_protocol.md`, `architecture/drive_inventory.md`.

---

## Module Map

### `core/` — Runtime spine

| Module | Role |
|--------|------|
| `belief_store.py` | Posterior sufficient statistics for skills, memory, LR, policy, confidence |
| `harness.py` | Versioned skills / policy / memory container |
| `orchestrator.py` | Evaluate → gate → canary or hard-commit → persist |
| `session_memory.py` | Trajectory tagging (agent vs external) |
| `canary.py` | Real extra-session canary runner |
| `commit.py` | Merge candidate patches under certificate |
| `evidence.py` | Trajectory → external-only evidence records |
| `evaluator.py` | Scoring interface + keyword/threshold evaluators |

### `bayesian_core/`

Hierarchical NumPyro model, interventional mask, GRO e-process + harmonic spender, conformal helpers.

### `commit_gate/` · `audit/` · `ontology/` · `federation/` · `llm/`

Soft/hard decisions, certificates, ontology↔posterior stubs, multi-agent belief packets, BaseLLM + OpenAI/Anthropic/local adapters.

### `skills/` + `skills_data/`

Recursive loader for Markdown (front-matter) and Python (`run`/`execute`) skills. Full pack list in `skills_data/PACKS.md`.

---

## Skill packs (larger library)

### Root skills

| ID | Type | Purpose |
|----|------|--------|
| summarize | md | Summaries preferring external evidence |
| verify_claim | md | Agent vs external separation |
| echo_tool | py | Echo + external heuristic |
| score_keywords | py | Keyword coverage ratio |

### `packs/research/`

| ID | Type | Purpose |
|----|------|--------|
| timeline_builder | md | Chronologies with source-class tags |
| entity_resolution | md | Canonical entities + aliases |
| source_grading | md | A/B/C/D/X source grades |
| dork_builder | py | Build public search queries (no execution) |

### `packs/evidence/`

| ID | Type | Purpose |
|----|------|--------|
| extract_citations | md | Structured citations |
| contradiction_scan | md | Conflict detection |

### `packs/agent/`

| ID | Type | Purpose |
|----|------|--------|
| memory_vault | md | Tagged durable memory hygiene |
| pattern_link | md | Evidence-based entity linking |

### `packs/documents/`

| ID | Type | Purpose |
|----|------|--------|
| pdf_digest | md | Structured PDF text digests |

### `packs/recovery/`

| ID | Type | Purpose |
|----|------|--------|
| relapse_education | md | Non-clinical educational recovery framing |

Load all packs:

```python
from skills.registry import SkillRegistry
reg = SkillRegistry(skills_dir="skills_data")
reg.load_directory()  # recursive **/*.md and **/*.py
print(reg.list_skills())
```

---

## Google Drive alignment

Connected Drive was inventoried (`architecture/drive_inventory.md`):

- **AGENT_ROLE / Skills** — upstream SKILL.txt templates, init_skill scaffold, skill-seeker docs → CodeSorcerer uses the same front-matter skill pattern.
- **advanced-swarm / Project Structure** — MemoryVault, PatternRecognition-style roles → mapped to memory_vault + pattern_link + research packs.
- **Braeden Drake certificates / Choices For Change** — recovery education domain → non-clinical `relapse_education` skill only.
- **Epstein investigation** — public-records research theme → timeline, entity resolution, source grading, citations (no offensive tooling).

CodeSorcerer does **not** import unbound/offensive directive scripts from Drive; safety remains interventional Bayesian gates + audit certificates.

---

## End-to-end flow

Session (tagged) → external evidence only → interventional Bayesian update → candidate skills/policy → Evaluator + GRO e-process + conformal → soft canary (real sessions) or hard commit (patch merge) → audit + persist under `state/`.

---

## Quick Start

```bash
git clone https://github.com/cantgetalonggta-png/CodeSorcerer.git
cd CodeSorcerer
pip install -r requirements.txt
python tests/test_core.py
python -m examples.basic_loop
python -m examples.full_cycle
python -m examples.orchestrated_canary
```

Optional: `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` or local OpenAI-compatible server for LLM adapters.

CI: `.github/workflows/ci.yml` on push/PR to `main`.

---

## Status

| Area | State |
|------|--------|
| Interventional Bayesian core + GRO/conformal gates | in place |
| BeliefStore, Harness, Orchestrator, Canary, hard-commit | in place |
| Session memory + evidence extraction | in place |
| Skill registry + **multi-domain skill packs** | in place |
| Evaluator + orchestrated example | in place |
| LLM adapters | in place |
| Drive inventory alignment doc | in place |
| CI | in place |
