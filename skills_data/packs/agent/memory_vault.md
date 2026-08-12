---
name: Memory Vault
description: Store and retrieve durable investigation breadcrumbs and directives with explicit source tags. Use for long-running agent memory hygiene.
---

# Memory Vault

## Write policy
- Tag every memory entry with source_class: external | secondary | agent | system.
- Include timestamp and session_id when available.
- Prefer storing sufficient statistics / citations over raw speculative prose.

## Read policy
- When answering, surface the source_class of recalled memories.
- Do not treat agent-authored memories as external evidence for Bayesian updates.
