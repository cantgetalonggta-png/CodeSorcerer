"""
Python skill: score how many required keywords appear in a text blob.
Used by evaluators and as a standalone skill.
"""

NAME = "Score Keywords"
DESCRIPTION = "Count how many of the required keywords appear in the given text. Returns a ratio in [0, 1]."


def run(text: str = "", keywords: list | None = None, **kwargs):
    keywords = keywords or []
    text_l = (text or "").lower()
    if not keywords:
        return {"ratio": 0.0, "hits": 0, "total": 0, "skill": NAME}
    hits = sum(1 for kw in keywords if str(kw).lower() in text_l)
    ratio = hits / len(keywords)
    return {
        "ratio": ratio,
        "hits": hits,
        "total": len(keywords),
        "matched": [kw for kw in keywords if str(kw).lower() in text_l],
        "skill": NAME,
    }


execute = run
