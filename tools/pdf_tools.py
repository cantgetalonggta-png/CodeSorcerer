"""
PDF tool wiring for CodeSorcerer.

Uses pypdf when installed; degrades gracefully with a clear message otherwise.
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Optional


def extract_pdf_text(path: str | Path, max_chars: int = 50000) -> Dict[str, Any]:
    path = Path(path)
    if not path.exists():
        return {"ok": False, "error": f"File not found: {path}", "text": ""}
    try:
        from pypdf import PdfReader
    except ImportError:
        return {
            "ok": False,
            "error": "pypdf not installed. pip install pypdf",
            "text": "",
        }
    try:
        reader = PdfReader(str(path))
        pages: List[str] = []
        for i, page in enumerate(reader.pages):
            t = page.extract_text() or ""
            pages.append(t)
        full = "\n\n".join(pages)
        truncated = len(full) > max_chars
        return {
            "ok": True,
            "path": str(path),
            "n_pages": len(reader.pages),
            "text": full[:max_chars],
            "truncated": truncated,
            "chars": len(full),
        }
    except Exception as e:
        return {"ok": False, "error": str(e), "text": ""}


def extract_many(paths: List[str | Path], max_chars_each: int = 15000) -> str:
    """Concatenate digests for swarm context."""
    chunks = []
    for p in paths:
        r = extract_pdf_text(p, max_chars=max_chars_each)
        name = Path(p).name
        if not r["ok"]:
            chunks.append(f"--- FILE: {name} ERROR: {r.get('error')} ---")
        else:
            chunks.append(
                f"--- FILE: {name} pages={r['n_pages']} ---\n{r['text']}"
            )
    return "\n\n".join(chunks)


def register_pdf_tools(router) -> None:
    """Register on llm.base.ToolRouter."""
    router.register("extract_pdf_text", lambda path, max_chars=50000: extract_pdf_text(path, max_chars))
