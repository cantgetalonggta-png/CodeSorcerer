"""
CodeSorcerer dashboard — stdlib HTTP server, no extra deps required.

Reads state/belief_store.json, harness.json, audit_log.json and serves
a simple HTML status page + JSON API.

Usage:
  python -m dashboard.app
  # open http://127.0.0.1:8765/
"""

from __future__ import annotations
import json
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
    skill_lis = "".join(f"<li>{s}</li>" for s in skills) or "<li>(none)</li>"

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"/><title>CodeSorcerer Dashboard</title>
<style>
 body {{ font-family: system-ui, sans-serif; margin: 2rem; background: #0b1020; color: #e8ecf7; }}
 h1 {{ color: #7dd3fc; }}
 .card {{ background: #151b2e; padding: 1rem 1.25rem; border-radius: 12px; margin-bottom: 1rem; }}
 table {{ border-collapse: collapse; width: 100%; }}
 td, th {{ border-bottom: 1px solid #2a3350; padding: 0.4rem 0.6rem; text-align: left; }}
 a {{ color: #93c5fd; }}
 code {{ background: #1e293b; padding: 0.1rem 0.35rem; border-radius: 4px; }}
</style></head><body>
<h1>CodeSorcerer Dashboard</h1>
<div class="card">
  <p><b>Harness version:</b> {version}</p>
  <p><b>Belief n_obs:</b> {n_obs}</p>
  <p><b>Last certificate:</b> <code>{cert}</code></p>
</div>
<div class="card">
  <h2>Skills in harness</h2>
  <ul>{skill_lis}</ul>
</div>
<div class="card">
  <h2>Audit decisions</h2>
  <table><tr><th>Decision</th><th>Count</th></tr>{rows}</table>
</div>
<div class="card">
  <h2>API</h2>
  <ul>
    <li><a href="/api/belief">/api/belief</a></li>
    <li><a href="/api/harness">/api/harness</a></li>
    <li><a href="/api/audit">/api/audit</a></li>
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
            html = _html_page().encode("utf-8")
            self._send(200, html, "text/html; charset=utf-8")
            return
        mapping = {
            "/api/belief": "belief_store.json",
            "/api/harness": "harness.json",
            "/api/audit": "audit_log.json",
        }
        if path in mapping:
            data = _load_json(mapping[path])
            body = json.dumps(data if data is not None else {"error": "missing"}, indent=2).encode("utf-8")
            self._send(200, body, "application/json")
            return
        self._send(404, b"{{"error":"not found"}}", "application/json")


def main():
    httpd = HTTPServer((HOST, PORT), Handler)
    print(f"CodeSorcerer dashboard on http://{HOST}:{PORT}/")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
