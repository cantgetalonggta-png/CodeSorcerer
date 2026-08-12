# Security package

Scoped, authorized, defensive materials only.

| File | Purpose |
|------|--------|
| `roe_template.md` | Written Rules of Engagement for tests **you own or are authorized** to perform |
| `threat_model.md` | Threat model for the CodeSorcerer agent stack |
| `purple_team.py` | Automated defensive control checks (session tags, evidence filter, certificate commits) |

Run purple suite:

```bash
python -m security.purple_team
# or
python tests/test_security_ontology.py
```

These modules do **not** claim unrestricted access to the internet or third-party systems.
