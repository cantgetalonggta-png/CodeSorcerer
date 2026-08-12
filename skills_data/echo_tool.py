"""
Sample Python skill for CodeSorcerer.

NAME and DESCRIPTION are picked up by the SkillRegistry.
The `run` function is the entrypoint.
"""

NAME = "Echo Tool"
DESCRIPTION = "Simple skill that echoes input and reports whether the content looks like external evidence."


def run(text: str = "", **kwargs):
    text = (text or "").strip()
    looks_external = any(
        k in text.lower()
        for k in ["tool result", "observation", "verified", "environment", "score="]
    )
    return {
        "echo": text[:500],
        "length": len(text),
        "looks_like_external_evidence": looks_external,
        "skill": NAME,
    }


# Alias used by some loaders
execute = run
