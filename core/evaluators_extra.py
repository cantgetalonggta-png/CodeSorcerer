"""
Additional evaluators beyond KeywordMatchEvaluator.
"""

from __future__ import annotations
from typing import Any, List
from core.evaluator import Evaluator


class LengthPenaltyEvaluator(Evaluator):
    """Prefer configs whose text length falls in a target band (avoid empty or huge dumps)."""

    def __init__(self, ideal_min: int = 40, ideal_max: int = 4000):
        self.ideal_min = ideal_min
        self.ideal_max = ideal_max

    def _text(self, config: Any) -> str:
        if isinstance(config, dict):
            parts = []
            for v in config.get("skills", {}).values():
                parts.append(str(v))
            for v in config.get("policy_fragments", {}).values():
                parts.append(str(v))
            return " ".join(parts)
        return str(config)

    def score(self, config: Any, instance: Any) -> float:
        n = len(self._text(config))
        if n < self.ideal_min:
            return max(0.0, n / max(self.ideal_min, 1))
        if n > self.ideal_max:
            return max(0.0, 1.0 - (n - self.ideal_max) / max(self.ideal_max, 1))
        return 1.0


class ExternalTagEvaluator(Evaluator):
    """
    Scores how often policy/skill text emphasizes external evidence discipline.
    """

    KEYS = [
        "external",
        "interventional",
        "evidence",
        "verified",
        "observation",
        "source",
        "citation",
    ]

    def score(self, config: Any, instance: Any) -> float:
        text = ""
        if isinstance(config, dict):
            text = str(config).lower()
        else:
            text = str(config).lower()
        hits = sum(1 for k in self.KEYS if k in text)
        return hits / len(self.KEYS)


class CompositeEvaluator(Evaluator):
    """Weighted average of multiple evaluators."""

    def __init__(self, evaluators: List[tuple]):
        """evaluators: list of (Evaluator, weight)."""
        self.evaluators = evaluators
        total = sum(w for _, w in evaluators) or 1.0
        self.evaluators = [(e, w / total) for e, w in evaluators]

    def score(self, config: Any, instance: Any) -> float:
        return sum(e.score(config, instance) * w for e, w in self.evaluators)
