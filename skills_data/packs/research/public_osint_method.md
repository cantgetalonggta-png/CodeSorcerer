---
name: Public OSINT Method
description: Structured methodology for collecting and recording publicly available information while respecting terms of service, robots rules, and authorization boundaries.
---

# Public OSINT Method

## Principles

1. Prefer **published** sources (official sites, public records portals, reputable reporting).
2. Respect site terms of service and rate limits; do not bypass access controls.
3. Record provenance for every fact (URL, date accessed, quote/locator).
4. Separate **public fact** from **inference**.
5. Stay inside any written authorization if the work is client-scoped.

## Workflow

1. Define the question and in-scope entities.
2. List candidate public source classes (gov portals, company filings, press, academic).
3. Collect with citations (`extract_citations` skill).
4. Grade sources (`source_grading` skill).
5. Build timeline / entity graph only from graded evidence.
6. Note gaps explicitly; do not fill with speculation marked as fact.

## Outputs

- Source log (URL, accessed, grade)
- Fact table (claim, citation, grade)
- Open questions list
