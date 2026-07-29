"""FR-3 — every rubric carries required claims AND route markers; a rubric with
no route markers is rejected at authoring, not accepted silently."""

import pytest

from agents.examiner.rubric import Rubric, RubricError


def test_fr3_rubric_carries_claims_and_route_markers():
    r = Rubric(claims=["low CO2 raises pH"], route_markers=["names it as alkalosis, not acidosis"])
    assert len(r.claims) >= 1
    assert len(r.route_markers) >= 1
    assert r.claims == ("low CO2 raises pH",)
    assert r.route_markers == ("names it as alkalosis, not acidosis",)
    # requires BOTH lists non-empty: empty claims is also rejected
    with pytest.raises(RubricError):
        Rubric(claims=[], route_markers=["m"])


def test_fr3_rejects_rubric_with_no_route_markers():
    # Rejected with an error — asserting the raise, never merely "no effect".
    with pytest.raises(RubricError):
        Rubric(claims=["a claim"], route_markers=[])
    with pytest.raises(RubricError):
        Rubric.from_dict({"claims": ["a claim"], "route_markers": []})
