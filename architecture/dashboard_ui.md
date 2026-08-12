# Dashboard UI Implementation Details

## Goals

- Zero required web framework (stdlib `http.server`)
- Read live agent state from `state/`
- HTML overview + JSON API for automation

## Entry point

```bash
python -m dashboard.app
# http://127.0.0.1:8765/
```

Configurable conceptually via `config/default.yaml` (`dashboard_host`, `dashboard_port`); current app uses 127.0.0.1:8765 constants (wire config loader next if needed).

## Pages / routes

| Path | Content |
|------|--------|
| `/` | HTML cards: harness version, n_obs, last certificate, skill list, audit decision counts |
| `/api/belief` | Raw `belief_store.json` |
| `/api/harness` | Raw `harness.json` |
| `/api/audit` | Raw `audit_log.json` |

## Data flow

1. Orchestrator / examples call `persist()` → writes JSON under `state/`.
2. Dashboard reads files on each request (no cache) so refresh shows latest commits.
3. Missing files → empty/error JSON; HTML shows placeholders.

## Styling

Inline dark theme CSS for a single-file deploy. No build step.

## Future extensions

- WebSocket live tail of audit log
- Promote-canary button (POST → Orchestrator.promote_canary)
- Skill pack browser from `skills_data/`
- Chart of e-process wealth over time from audit records
