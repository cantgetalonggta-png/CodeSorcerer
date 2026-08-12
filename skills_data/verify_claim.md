---
name: Verify Claim
description: Check a factual claim against available external evidence and tool results. Prefer interventional evidence.
---

# Verify Claim Skill

When asked to verify a claim:

1. Restate the claim clearly.
2. Separate **agent statements** from **external observations** (tool outputs, verified scores, environment results).
3. Only treat external observations as evidence that can update beliefs.
4. Output:
   - Verdict: supported / contradicted / insufficient evidence
   - Key external evidence (bullet list)
   - Remaining uncertainty

Never promote the agent's own prior words into evidence.
