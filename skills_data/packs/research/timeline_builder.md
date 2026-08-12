---
name: Timeline Builder
description: Build chronological timelines from documents, claims, and external observations. Use when ordering events, reconciling dates, or preparing investigation chronologies.
---

# Timeline Builder

## Overview
Construct ordered timelines that separate **verified external observations** from **agent or secondary claims**.

## Workflow
1. Collect candidate events (date, description, source type).
2. Tag each event: `external` | `secondary` | `agent_statement` | `unverified`.
3. Sort by best-available date; note ambiguity ranges.
4. Output a table: Date | Event | Source class | Confidence | Notes.
5. Flag contradictions (same date, conflicting facts).

## Rules
- Prefer primary documents and tool/environment results over narrative summaries.
- Never promote agent-generated text into the "external" class.
- When dates conflict, list all variants; do not silently pick one.
