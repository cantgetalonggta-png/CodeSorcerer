---
name: Pattern Link
description: Connect recurring names, dates, organizations, and pipelines across documents without inventing links.
---

# Pattern Link

1. List recurring tokens (names, orgs, places, dates).
2. Build candidate edges only when co-occurrence or explicit reference exists.
3. Score each edge: explicit mention | strong co-occurrence | weak association.
4. Output graph edges with evidence pointers; never invent bridges.
