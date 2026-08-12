# Skill Packs Inventory

Skills live under `skills_data/` and nested `skills_data/packs/<domain>/`.
`SkillRegistry.load_directory()` recursively loads `*.md` and `*.py`.

## Core (root `skills_data/`)

| ID | Type | Purpose |
|----|------|--------|
| summarize | md | Concise summaries preferring external evidence |
| verify_claim | md | Claim checking with agent vs external separation |
| echo_tool | py | Echo + external-evidence heuristic |
| score_keywords | py | Keyword coverage ratio |

## Pack: research/

| ID | Type | Purpose |
|----|------|--------|
| timeline_builder | md | Chronologies with source-class tags |
| entity_resolution | md | Canonical entities + aliases + evidence |
| source_grading | md | A/B/C/D/X source grades |
| dork_builder | py | Build public search query strings (no execution) |

## Pack: evidence/

| ID | Type | Purpose |
|----|------|--------|
| extract_citations | md | Structured citation extraction |
| contradiction_scan | md | Conflict detection across sources |

## Pack: agent/

| ID | Type | Purpose |
|----|------|--------|
| memory_vault | md | Durable memory write/read with source tags |
| pattern_link | md | Evidence-based entity/event linking |

## Pack: documents/

| ID | Type | Purpose |
|----|------|--------|
| pdf_digest | md | Structured digests of extracted PDF text |

## Pack: recovery/

| ID | Type | Purpose |
|----|------|--------|
| relapse_education | md | Non-clinical educational recovery support framing |

## Drive-aligned notes

Google Drive `AGENT_ROLE/Skills` contains many upstream SKILL.txt templates and skill-seeker docs. CodeSorcerer packs follow the same front-matter `name` / `description` pattern and focus on **investigation hygiene, evidence discipline, and agent memory** — not offensive tooling.
