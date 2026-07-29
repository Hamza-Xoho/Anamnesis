"""Blind grading: exactly five inputs in, three separate outputs out.

FR-4: the examiner call is constructed from exactly concept, prompt, verbatim
response, rubric, and `answer_was_onscreen` — and nothing else. Surrounding
conversation is not a parameter, so it cannot enter.

FR-5: verdict, route_quality and expressed_confidence are three distinct fields.
They are never merged, and `grade` contains no path from expressed_confidence to
verdict.

NFR-7: every result records model identity, version and prompt hash.
"""

from __future__ import annotations

from dataclasses import dataclass

from .rubric import Rubric

# design-spec §5 Enums
VERDICTS = ("miss", "partial", "hit", "effortless_hit")
ROUTE_QUALITIES = ("clean", "route_failure", "unassessable")


@dataclass(frozen=True)
class ExaminerInput:
    """The five — and only five — fields the examiner ever sees (FR-4)."""

    concept: str
    prompt: str
    response: str
    rubric: Rubric
    answer_was_onscreen: bool


@dataclass(frozen=True)
class GradeResult:
    # Three separate outputs (FR-5), never merged.
    verdict: str
    route_quality: str
    expressed_confidence: float
    # Provenance (NFR-7).
    model_id: str
    model_version: str
    prompt_hash: str
    rubric_hash: str


def grade(
    *,
    concept: str,
    prompt: str,
    response: str,
    rubric: Rubric,
    answer_was_onscreen: bool,
    client,
) -> GradeResult:
    """Construct the examiner input from exactly the five FR-4 fields, grade it
    with the injected client, and stamp provenance.

    The signature is keyword-only and takes those five fields plus the client to
    call. There is no parameter through which surrounding text — or a caller's
    preferred verdict — could reach the grade.
    """
    examiner_input = ExaminerInput(
        concept=concept,
        prompt=prompt,
        response=response,
        rubric=rubric,
        answer_was_onscreen=answer_was_onscreen,
    )
    raw = client.grade(examiner_input)

    if raw.verdict not in VERDICTS:
        raise ValueError(f"examiner returned unknown verdict: {raw.verdict!r}")
    if raw.route_quality not in ROUTE_QUALITIES:
        raise ValueError(f"examiner returned unknown route_quality: {raw.route_quality!r}")

    return GradeResult(
        verdict=raw.verdict,
        route_quality=raw.route_quality,
        expressed_confidence=float(raw.expressed_confidence),
        model_id=client.model_id,
        model_version=client.model_version,
        prompt_hash=client.prompt_hash,
        rubric_hash=rubric.rubric_hash,
    )
