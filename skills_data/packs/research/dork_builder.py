"""
Public web search query builder (legal OSINT-style query construction only).
Does not execute searches; only builds query strings.
"""

NAME = "Dork Builder"
DESCRIPTION = "Build structured public search queries from keywords, site filters, and filetypes. Does not run searches."


def run(
    keywords: list | None = None,
    sites: list | None = None,
    filetypes: list | None = None,
    exclude: list | None = None,
    **kwargs,
):
    keywords = keywords or []
    sites = sites or []
    filetypes = filetypes or []
    exclude = exclude or []

    parts = [str(k) for k in keywords if k]
    for s in sites:
        parts.append(f"site:{s}")
    for ft in filetypes:
        parts.append(f"filetype:{ft}")
    for x in exclude:
        parts.append(f"-{x}")

    query = " ".join(parts).strip()
    return {
        "query": query,
        "keyword_count": len(keywords),
        "skill": NAME,
        "note": "Query only — execute via your own search tools under applicable terms.",
    }


execute = run
