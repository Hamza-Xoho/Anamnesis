"""Shared helpers for the Phase 0 contract tests.

Frozen with the tests (INV-6): a contract test's support code is part of the
contract. These helpers load the clearly-labelled SYNTHETIC fixtures used by the
0a mechanism tests, and provide a recording client double that captures exactly
what `grade()` hands to the examiner.
"""

from __future__ import annotations

import json
from pathlib import Path

from agents.examiner.client import DeterministicClient, RawGrade

REPO_ROOT = Path(__file__).resolve().parents[3]
SYN_DIR = REPO_ROOT / "tests" / "fixtures" / "synthetic"


def synthetic_rubric_data() -> dict:
    return json.loads((SYN_DIR / "rubrics.json").read_text())["rubrics"][0]


def synthetic_attempts() -> dict:
    return json.loads((SYN_DIR / "attempts.json").read_text())


class RecordingClient:
    """A real client double that records the ExaminerInput it was handed, then
    delegates to the deterministic grader. Used to prove `grade()` constructs
    the examiner call from exactly the five FR-4 fields and nothing else."""

    def __init__(self) -> None:
        self._inner = DeterministicClient()
        self.model_id = self._inner.model_id
        self.model_version = self._inner.model_version
        self.prompt_hash = self._inner.prompt_hash
        self.last = None

    def grade(self, examiner_input) -> RawGrade:
        self.last = examiner_input
        return self._inner.grade(examiner_input)
