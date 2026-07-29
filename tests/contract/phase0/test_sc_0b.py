"""Phase 0b — the measurement gate (SC-1, SC-4, κ).

These read the report produced by `python -m agents.examiner.harness --report`.
They assert on that report rather than calling the model, so pytest stays
hermetic. Until a *sufficient* frozen set exists and a real measurement has been
produced, they skip with the reason — a number computed on n<floor is not a
measurement, so there is nothing to assert yet.
"""

import json

import pytest

from agents.examiner.harness import (
    KAPPA_SUBSTANTIAL_BAND,
    REPORT_PATH,
    SC1_THRESHOLD,
    SC4_THRESHOLD,
)


def _measured_report():
    if not REPORT_PATH.exists():
        pytest.skip(
            "No Phase 0b report yet. Run `python -m agents.examiner.harness --report`."
        )
    report = json.loads(REPORT_PATH.read_text())
    if report.get("status") != "measured":
        pytest.skip(
            f"Phase 0b not measured (status={report.get('status')!r}): "
            f"{report.get('reason', 'frozen set below the informative floor')}"
        )
    return report


def test_sc1_grading_separation_on_seeded_set():
    report = _measured_report()
    sc1 = report["sc1"]
    assert sc1["matched_pairs"] >= report["floors"]["matched_pairs"]
    assert sc1["separation_rate"] >= SC1_THRESHOLD


def test_sc4_route_detection_on_seeded_set():
    report = _measured_report()
    sc4 = report["sc4"]
    assert sc4["route_failures"] >= report["floors"]["route_failures"]
    assert sc4["route_failure_rate"] >= SC4_THRESHOLD


def test_gate_kappa_against_human_labels():
    report = _measured_report()
    kappa = report["kappa"]
    # κ reported per human-labelled criterion (verdict, route_quality), compared
    # against the substantial band. Characterisation: it must run and report.
    assert "verdict" in kappa and "route_quality" in kappa
    for criterion in ("verdict", "route_quality"):
        assert -1.0 <= kappa[criterion] <= 1.0
    assert report["kappa_substantial_band"] == KAPPA_SUBSTANTIAL_BAND
