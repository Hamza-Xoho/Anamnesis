"""NFR-7 — every grade records model identity, version and prompt hash (and the
rubric hash it graded against, design-spec §3.4)."""

from agents.examiner.client import DeterministicClient
from agents.examiner.examiner import grade
from agents.examiner.rubric import Rubric

from conftest import synthetic_attempts, synthetic_rubric_data


def test_nfr7_grade_records_model_identity():
    g = grade(
        concept="c",
        prompt="p",
        response=synthetic_attempts()["base_attempt"]["response"],
        rubric=Rubric.from_dict(synthetic_rubric_data()["rubric"]),
        answer_was_onscreen=False,
        client=DeterministicClient(),
    )
    assert isinstance(g.model_id, str) and g.model_id
    assert isinstance(g.model_version, str) and g.model_version
    assert g.prompt_hash.startswith("sha256:")
    assert g.rubric_hash.startswith("sha256:")
