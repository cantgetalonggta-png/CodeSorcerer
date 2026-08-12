"""Security package — import submodules explicitly."""

__all__ = ["run_purple_suite", "PurpleReport", "CheckResult"]


def __getattr__(name: str):
    if name in {"run_purple_suite", "PurpleReport", "CheckResult"}:
        from security import purple_team as pt
        return getattr(pt, name)
    raise AttributeError(name)
