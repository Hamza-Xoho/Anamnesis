"""FR-5 — three separate outputs per attempt (verdict, route quality, expressed
confidence), never merged; and expressed confidence has no path to the verdict."""

import dataclasses

from agents.examiner.client import DeterministicClient
from agents.examiner.examiner import GradeResult, grade
from agents.examiner.rubric import Rubric

from conftest import synthetic_attempts, synthetic_rubric_data


def _syn_rubric() -> Rubric:
    return Rubric.from_dict(synthetic_rubric_data()["rubric"])


def test_fr5_three_distinct_outputs():
    names = {f.name for f in dataclasses.fields(GradeResult)}
    # three distinct fields present, not one merged score
    assert {"verdict", "route_quality", "expressed_confidence"} <= names

    g = grade(
        concept="c",
        prompt="p",
        response=synthetic_attempts()["base_attempt"]["response"],
        rubric=_syn_rubric(),
        answer_was_onscreen=False,
        client=DeterministicClient(),
    )
    assert isinstance(g.verdict, str)
    assert isinstance(g.route_quality, str)
    assert isinstance(g.expressed_confidence, float)


def test_fr5_expressed_confidence_has_no_path_to_verdict():
    pair = synthetic_attempts()["hedging_pair"]
    rubric = _syn_rubric()

    def _grade(text):
        return grade(
            concept="c",
            prompt="p",
            response=text,
            rubric=rubric,
            answer_was_onscreen=False,
            client=DeterministicClient(),
        )

    assertive = _grade(pair["assertive"]["response"])
    hedged = _grade(pair["hedged"]["response"])

    # Two responses differing ONLY in hedging register → identical verdict and
    # identical route_quality.
    assert assertive.verdict == hedged.verdict
    assert assertive.route_quality == hedged.route_quality
    # The register WAS different and was read — but only into expressed_confidence.
    assert assertive.expressed_confidence != hedged.expressed_confidence
