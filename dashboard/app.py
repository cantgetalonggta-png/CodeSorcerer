"""
CodeSorcerer dashboard — stdlib HTTP server (no extra web deps).

Usage:
  python -m dashboard.app
  open http://127.0.0.1:8765/
"""

from __future__ import annotations
import json
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

STATE = Path("state")
HOST = "127.0.0.1"
PORT = 8765


def _load_json(name: str):
    p = STATE / name
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        return {"error": str(e)}


def _purple_status() -> dict:
    try:
        from security.purple_team import run_purple_suite
        report = run_purple_suite()
        return {
            "ok": report.ok,
            "summary": report.summary(),
            "checks": [{"name": r.name, "passed": r.passed, "detail": r.detail} for r in report.results],
        }
    except Exception as e:
        return {"ok": False, "error": str(e), "checks": []}


def _stack_info() -> dict:
    try:
        from bayesian_core.inference_layers import INFERENCE_STACK
        return {
            "layers": [
                {"layer": L.layer, "name": L.name, "status": L.status, "description": L.description}
                for L in INFERENCE_STACK
            ]
        }
    except Exception as e:
        return {"error": str(e), "layers": []}


def _health() -> dict:
    belief = _load_json("belief_store.json")
    harness = _load_json("harness.json")
    audit = _load_json("audit_log.json")
    return {
        "status": "ok",
        "time": datetime.now(timezone.utc).isoformat(),
        "state_dir": str(STATE.resolve()),
        "files": {
            "belief_store": belief is not None and "error" not in (belief or {}),
            "harness": harness is not None and "error" not in (harness or {}),
            "audit_log": audit is not None,
        },
        "harness_version": (harness or {}).get("version"),
        "n_obs": (belief or {}).get("n_obs_total"),
    }


def _html_page() -> str:
    belief = _load_json("belief_store.json") or {}
    harness = _load_json("harness.json") or {}
    audit = _load_json("audit_log.json") or []
    if isinstance(audit, dict):
        audit = audit.get("records", [])

    skills = list((harness.get("skills") or {}).keys())
    version = harness.get("version", "—")
    n_obs = belief.get("n_obs_total", 0)
    cert = belief.get("last_certificate_id") or harness.get("last_certificate_id") or "—"
    decisions = {}
    if isinstance(audit, list):
        for r in audit:
            d = r.get("decision", "?")
            decisions[d] = decisions.get(d, 0) + 1

    rows = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in decisions.items()) or "<tr><td colspan=2>No audit yet</td></tr>"
    skill_lis = "".join(f"<li><code>{s}</code></li>" for s in skills) or "<li>(none — run an example to populate state)</li>"

    purple = _purple_status()
    purple_badge = "PASS" if purple.get("ok") else "FAIL"
    purple_color = "#4ade80" if purple.get("ok") else "#f87171"
    check_rows = "".join(
        f"<tr><td>{c['name']}</td><td style='color:{"#4ade80" if c["passed"] else "#f87171"}'>{"PASS" if c["passed"] else "FAIL"}</td><td>{c.get('detail','')}</td></tr>"
        for c in purple.get("checks", [])
    ) or "<tr><td colspan=3>unavailable</td></tr>"

    stack = _stack_info()
    stack_rows = "".join(
        f"<tr><td>L{L['layer']}</td><td>{L['name']}</td><td>{L['status']}</td><td>{L['description']}</td></tr>"
        for L in stack.get("layers", [])
    ) or "<tr><td colspan=4>—</td></tr>"

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"/>
<meta http-equiv="refresh" content="30"/>
<title>CodeSorcerer Dashboard</title>
<style>
 body {{ font-family: system-ui, sans-serif; margin: 2rem; background: #0b1020; color: #e8ecf7; }}
 h1 {{ color: #7dd3fc; margin-bottom: 0.25rem; }}
 .sub {{ color: #94a3b8; margin-bottom: 1.5rem; }}
 .card {{ background: #151b2e; padding: 1rem 1.25rem; border-radius: 12px; margin-bottom: 1rem; border: 1px solid #1e293b; }}
 table {{ border-collapse: collapse; width: 100%; font-size: 0.95rem; }}
 td, th {{ border-bottom: 1px solid #2a3350; padding: 0.45rem 0.6rem; text-align: left; vertical-align: top; }}
 a {{ color: #93c5fd; }}
 code {{ background: #1e293b; padding: 0.1rem 0.35rem; border-radius: 4px; font-size: 0.9em; }}
 .badge {{ display: inline-block; padding: 0.15rem 0.55rem; border-radius: 999px; font-weight: 600; background: #1e293b; color: {purple_color}; }}
 .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }}
 @media (max-width: 900px) {{ .grid {{ grid-template-columns: 1fr; }} }}
</style></head><body>
<h1>CodeSorcerer Dashboard</h1>
<p class="sub">Updated {now} · auto-refresh 30s · purple <span class="badge">{purple_badge}</span></p>

<div class="grid">
<div class="card">
  <h2>Runtime state</h2>
  <p><b>Harness version:</b> {version}</p>
  <p><b>Belief n_obs:</b> {n_obs}</p>
  <p><b>Last certificate:</b> <code>{cert}</code></p>
</div>
<div class="card">
  <h2>Skills in harness</h2>
  <ul>{skill_lis}</ul>
</div>
</div>

<div class="card">
  <h2>Audit decisions</h2>
  <table><tr><th>Decision</th><th>Count</th></tr>{rows}</table>
</div>

<div class="card">
  <h2>Purple-team defensive checks</h2>
  <table><tr><th>Check</th><th>Result</th><th>Detail</th></tr>{check_rows}</table>
</div>

<div class="card">
  <h2>Bayesian inference stack</h2>
  <table><tr><th>Layer</th><th>Name</th><th>Status</th><th>Description</th></tr>{stack_rows}</table>
</div>

<div class="card">
  <h2>API</h2>
  <ul>
    <li><a href="/api/health">/api/health</a></li>
    <li><a href="/api/belief">/api/belief</a></li>
    <li><a href="/api/harness">/api/harness</a></li>
    <li><a href="/api/audit">/api/audit</a></li>
    <li><a href="/api/purple">/api/purple</a></li>
    <li><a href="/api/stack">/api/stack</a></li>
  </ul>
</div>
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print("[dashboard]", fmt % args)

    def _send(self, code: int, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            self._send(200, _html_page().encode("utf-8"), "text/html; charset=utf-8")
            return
        apis = {
            "/api/belief": lambda: _load_json("belief_store.json"),
            "/api/harness": lambda: _load_json("harness.json"),
            "/api/audit": lambda: _load_json("audit_log.json"),
            "/api/health": _health,
            "/api/purple": _purple_status,
            "/api/stack": _stack_info,
        }
        if path in apis:
            data = apis[path]()
            body = json.dumps(data if data is not None else {"error": "missing"}, indent=2, default=str).encode("utf-8")
            self._send(200, body, "application/json")
            return
        self._send(404, b'{"error":"not found"}', "application/json")


def main():
    httpd = HTTPServer((HOST, PORT), Handler)
    print(f"CodeSorcerer dashboard on http://{HOST}:{PORT}/")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
