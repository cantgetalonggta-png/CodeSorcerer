"""Commit gate package – soft/hard commit logic."""

from .soft_hard import soft_commit_decision, run_paired_evaluation

__all__ = ["soft_commit_decision", "run_paired_evaluation"]
