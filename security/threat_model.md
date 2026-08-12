# Threat Model — CodeSorcerer Agent Stack

## Assets

- BeliefStore posteriors (skill/memory reliability)
- Versioned Harness (skills, policy fragments)
- Session trajectories and audit certificates
- LLM API keys / env credentials
- Canary and production harness snapshots under `state/`

## Trust boundaries

| Boundary | Trust |
|----------|--------|
| Frozen base LLM | Untrusted output (always agent_intervention) |
| Tools / PDF extract / evaluators | External observations if verified |
| User prompts | Untrusted |
| Commit gate + canary | Trusted control plane |
| Audit log | Append-oriented integrity target |

## Key threats

1. **Prompt injection** — malicious text in PDFs or web context steers swarm agents.
2. **Self-delusion** — model treats its own claims as evidence (mitigated by interventional mask + evidence filter).
3. **False skill promotion** — weak candidate merges into harness (mitigated by GRO + conformal + strict canary).
4. **Credential leakage** — keys in logs or Drive env files (operational control; never commit secrets).
5. **Audit tampering** — local file rewrite without certificate chain (future: signed append-only log).
6. **Scope creep in automation** — scripts run outside authorized targets (ROE + ComplianceGate skill).

## Mitigations mapped to code

| Threat | Control |
|--------|---------|
| Self-delusion | `interventional.py`, `evidence.py`, session tags |
| False promotion | `eprocess.py`, `conformal.py`, `canary.py`, strict config |
| Injection via docs | Source grading skill, ComplianceGate agent role |
| Silent mutation | `commit.py` + certificate id on harness/belief |
| Regression of controls | `security/purple_team.py` suite |

## Residual risk

- EchoLLM / weak evaluators can pass toy patches; production needs real task metrics.
- Dashboard is local-only by default; do not expose without auth.
- Swarm synthesis is still model text — must pass the same gates before harness merge.
