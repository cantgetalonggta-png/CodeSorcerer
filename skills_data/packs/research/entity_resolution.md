---
name: Entity Resolution
description: Resolve name variants, aliases, and organizations into canonical entities with evidence links. Use for investigation graphs and deduplication.
---

# Entity Resolution

## Overview
Map messy name strings to canonical entities and record supporting evidence.

## Steps
1. List all observed surface forms.
2. Cluster likely matches (spelling, nicknames, org abbreviations).
3. For each cluster, assign a canonical ID and label.
4. Attach evidence: document, date, context snippet, source class.
5. Mark low-confidence links explicitly.

## Output schema
- canonical_id
- display_name
- aliases[]
- entity_type (person|org|place|other)
- evidence[]
- confidence (0-1)
