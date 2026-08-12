"""
Real evaluator interface + concrete evaluators.

An Evaluator scores a configuration (harness patch, skill set, policy)
on a given instance and returns a numeric score (higher = better).
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import re
import hashlib


class Evaluator(ABC):
    @abstractmethod
    def score(self, config: Any, instance: Any) -> float:
        """Return a score in [0, 1] or any comparable numeric range."""
        ...

    def batch_score(self, config: Any, instances: List[Any]) -> List[float]:
        return [self.score(config, inst) for inst in instances]


class KeywordMatchEvaluator(Evaluator):
    """
    Scores how well a config's skill/policy text covers required keywords
    for a given instance. Useful for testing skill quality without an LLM.
    """

    def __init__(self, keyword_field: str = "keywords"):
        self.keyword_field = keyword_field

    def score(self, config: Any, instance: Any) -> float:
        if isinstance(instance, dict):
            keywords = instance.get(self.keyword_field, [])
            text_blob = instance.get("text", "")
        else:
            keywords = []
            text_blob = str(instance)

        # Gather text from config (patch or harness-like dict)
        config_text = ""
        if isinstance(config, dict):
            for skill in config.get("skills", {}).values():
                if isinstance(skill, dict):
                    config_text += " " + str(skill.get("description", "")) + " " + str(skill.get("content", ""))
                else:
                    config_text += " " + str(skill)
            for pol in config.get("policy_fragments", {}).values():
                config_text += " " + str(pol)
            config_text += " " + str(config.get("content", ""))
        else:
            config_text = str(config)

        config_text = config_text.lower()
        if not keywords:
            # Fallback: hash-based stable score so tests are deterministic-ish
            h = hashlib.md5((config_text + text_blob).encode()).hexdigest()
            return (int(h[:8], 16) % 1000) / 1000.0

        hits = sum(1 for kw in keywords if kw.lower() in config_text)
        return hits / max(len(keywords), 1)


class ThresholdSuccessEvaluator(Evaluator):
    """
    Wraps another evaluator and also exposes a binary success
    when score >= threshold. Useful for canary session_fn.
    """

    def __init__(self, base: Evaluator, threshold: float = 0.5):
        self.base = base
        self.threshold = threshold

    def score(self, config: Any, instance: Any) -> float:
        return self.base.score(config, instance)

    def success(self, config: Any, instance: Any) -> bool:
        return self.score(config, instance) >= self.threshold


def make_canary_session_fn(evaluator: ThresholdSuccessEvaluator, instances: List[Any]):
    """
    Build a session_fn(harness, idx) -> (success, score) for CanaryRunner.
    Cycles through the provided instances.
    """
    def session_fn(harness, idx: int):
        inst = instances[idx % len(instances)] if instances else {}
        # Treat harness skills/policy as config
        config = {
            "skills": harness.skills,
            "policy_fragments": harness.policy_fragments,
        }
        sc = evaluator.score(config, inst)
        ok = sc >= evaluator.threshold
        return ok, sc
    return session_fn
