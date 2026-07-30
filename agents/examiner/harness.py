"""Phase 0b grading harness.

Reads the frozen evaluation set, grades it blind through the pinned examiner, and
measures whether the grader separates understanding from fluent recall well enough
for the rest of the project to be worth building:

  SC-1  ≥90% of matched pairs rank the confidently-wrong answer below the
        hedged-correct one.
  SC-4  ≥80% of right-answer / wrong-mechanism responses recorded as route
        failures.
  κ     Cohen's κ per human-labelled criterion (verdict, route_quality) against
        the held-out sample.

It refuses to emit a gate on an insufficient set. Per the frozen README, the
pilot is 10 matched pairs / 8 route-failures, and the informative floor is ~25
matched pairs — below that you cannot statistically tell 90% from 70%. If the
set is below floor, --report reports BLOCKED and produces no pass/fail — a
number computed on n=2 is not a measurement.

--pilot deliberately bypasses that floor to probe direction on the prescribed
10/8 pilot set with the real pinned model. It reports status "pilot", never
"measured", and cannot pass or fail the gate — a pilot indicates direction
only. It returns 0 whenever it ran, whatever the thresholds say.

Usage:
  python -m agents.examiner.harness --report     # real pinned model (Opus 4.8), gate
  python -m agents.examiner.harness --pilot       # real pinned model on the below-floor pilot set (direction only)
  python -m agents.examiner.harness --dry-run     # offline plumbing check only
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from .client import MODEL_ID, MODEL_VERSION
from .examiner import GradeResult, grade
from .rubric import Rubric

REPO_ROOT = Path(__file__).resolve().parents[2]
FROZEN_DIR = REPO_ROOT / "tests" / "fixtures" / "frozen"
REPORT_PATH = REPO_ROOT / "agents" / "examiner" / "reports" / "phase0-report.json"

# Thresholds (design-spec / test-contract).
SC1_THRESHOLD = 0.90
SC4_THRESHOLD = 0.80
KAPPA_SUBSTANTIAL_BAND = 0.61

# Sufficiency floors (frozen README: pilot 10/8, informative floor ~25 pairs).
FLOOR_MATCHED_PAIRS = 25
FLOOR_ROUTE_FAILURES = 25
FLOOR_KAPPA_ITEMS = 25

# What a below-floor pilot result may and may not be read as.
PILOT_INTERPRETATION = (
    "PILOT — direction only, NOT the phase-0 architecture gate. This is a real "
    "measurement of a small set graded by the pinned model, but below ~25 matched "
    "pairs a 90% separation rate cannot be statistically distinguished from 70%, "
    "so no pass/fail can be read from it. Bands (frozen README): near or above "
    "threshold → build the full set; 50–70% → grader is close, iterate on the "
    "pilot; near chance → stop, the assumption did not hold."
)

_VERDICT_RANK = {"miss": 0, "partial": 1, "hit": 2, "effortless_hit": 3}
_ROUTE_RANK = {"unassessable": 0, "route_failure": 0, "clean": 1}


# --- loading ---------------------------------------------------------------


def _load_yaml(path: Path):
    try:
        import yaml
    except ModuleNotFoundError:  # pragma: no cover - environment guard
        raise SystemExit(
            "PyYAML is required to read the frozen set. Install the examiner "
            "extra:\n    uv sync --extra examiner\n(0a mechanism tests do not need it.)"
        )
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data or []


def load_frozen():
    return {
        "matched_pairs": _load_yaml(FROZEN_DIR / "matched-pairs.yaml"),
        "route_failures": _load_yaml(FROZEN_DIR / "route-failures.yaml"),
        "kappa": _load_yaml(FROZEN_DIR / "kappa-sample.yaml"),
    }


def _rubric_of(entry: dict) -> Rubric:
    return Rubric.from_dict(entry["rubric"])


# --- metrics ---------------------------------------------------------------


def _understanding_score(res: GradeResult) -> int:
    """Rank by what was understood — verdict first, route as tie-break. Never
    by expressed_confidence: that is exactly what SC-1 must NOT reward."""
    return _VERDICT_RANK[res.verdict] * 2 + _ROUTE_RANK[res.route_quality]


def _grade_answer(entry: dict, text: str, client) -> GradeResult:
    return grade(
        concept=entry.get("concept", ""),
        prompt=entry.get("probe", entry.get("prompt", "")),
        response=text,
        rubric=_rubric_of(entry),
        answer_was_onscreen=False,  # frozen answers are cold written recall
        client=client,
    )


def cohen_kappa(a: list[str], b: list[str]) -> float:
    n = len(a)
    if n == 0:
        return 0.0
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum((ca[c] / n) * (cb[c] / n) for c in set(a) | set(b))
    if pe >= 1.0:
        return 1.0 if po >= 1.0 else 0.0
    return (po - pe) / (1 - pe)


def measure_sc1(pairs, client):
    items, separated = [], 0
    for p in pairs:
        wrong = _grade_answer(p, p["confidently_wrong"]["text"], client)
        correct = _grade_answer(p, p["hedged_correct"]["text"], client)
        ok = _understanding_score(correct) > _understanding_score(wrong)
        separated += int(ok)
        items.append(
            {
                "pair_id": p.get("pair_id"),
                "confidently_wrong": {"verdict": wrong.verdict, "route_quality": wrong.route_quality,
                                      "expressed_confidence": wrong.expressed_confidence},
                "hedged_correct": {"verdict": correct.verdict, "route_quality": correct.route_quality,
                                   "expressed_confidence": correct.expressed_confidence},
                "separated": ok,
            }
        )
    n = len(pairs)
    rate = separated / n if n else 0.0
    return {"matched_pairs": n, "separated": separated, "separation_rate": rate,
            "threshold": SC1_THRESHOLD, "pass": rate >= SC1_THRESHOLD, "items": items}


def measure_sc4(route_items, client):
    items, flagged = [], 0
    for r in route_items:
        res = _grade_answer(r, r["response"]["text"], client)
        ok = res.route_quality == "route_failure"
        flagged += int(ok)
        items.append({"item_id": r.get("item_id"), "verdict": res.verdict,
                      "route_quality": res.route_quality, "flagged_as_route_failure": ok})
    n = len(route_items)
    rate = flagged / n if n else 0.0
    return {"route_failures": n, "flagged": flagged, "route_failure_rate": rate,
            "threshold": SC4_THRESHOLD, "pass": rate >= SC4_THRESHOLD, "items": items}


def measure_kappa(kappa_items, client):
    g_verdict, h_verdict, g_route, h_route, items = [], [], [], [], []
    for k in kappa_items:
        res = _grade_answer(k, k["response"]["text"], client)
        human = k["label"]
        g_verdict.append(res.verdict)
        h_verdict.append(human["verdict"])
        g_route.append(res.route_quality)
        h_route.append(human["route_quality"])
        items.append({"item_id": k.get("item_id"),
                      "grader": {"verdict": res.verdict, "route_quality": res.route_quality},
                      "human": {"verdict": human["verdict"], "route_quality": human["route_quality"]}})
    return {
        "verdict": cohen_kappa(g_verdict, h_verdict),
        "route_quality": cohen_kappa(g_route, h_route),
        "n": len(kappa_items),
        "items": items,
    }


# --- orchestration ---------------------------------------------------------


def _counts(frozen):
    return {
        "matched_pairs": len(frozen["matched_pairs"]),
        "route_failures": len(frozen["route_failures"]),
        "kappa_items": len(frozen["kappa"]),
    }


def _floors():
    return {
        "matched_pairs": FLOOR_MATCHED_PAIRS,
        "route_failures": FLOOR_ROUTE_FAILURES,
        "kappa_items": FLOOR_KAPPA_ITEMS,
    }


def _insufficiency_reason(counts):
    gaps = []
    if counts["matched_pairs"] < FLOOR_MATCHED_PAIRS:
        gaps.append(f"matched pairs {counts['matched_pairs']}<{FLOOR_MATCHED_PAIRS}")
    if counts["route_failures"] < FLOOR_ROUTE_FAILURES:
        gaps.append(f"route-failures {counts['route_failures']}<{FLOOR_ROUTE_FAILURES}")
    if counts["kappa_items"] < FLOOR_KAPPA_ITEMS:
        gaps.append(f"κ items {counts['kappa_items']}<{FLOOR_KAPPA_ITEMS}")
    return "; ".join(gaps)


def _write(report: dict) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


def _grader_stamp(dry_run: bool):
    if dry_run:
        from .client import DeterministicClient

        c = DeterministicClient()
        return c, {"model_id": c.model_id, "model_version": c.model_version, "prompt_hash": c.prompt_hash}
    from .client import AnthropicExaminerClient

    c = AnthropicExaminerClient()
    return c, {"model_id": c.model_id, "model_version": c.model_version, "prompt_hash": c.prompt_hash}


def run(dry_run: bool = False, pilot: bool = False) -> int:
    frozen = load_frozen()
    counts = _counts(frozen)
    reason = _insufficiency_reason(counts)

    # Real measurement refuses to run below the informative floor. A pilot is a
    # deliberate below-floor probe, so it bypasses the floor; a dry run never gates.
    if not dry_run and not pilot and reason:
        report = {
            "status": "blocked",
            "reason": f"frozen set below informative floor ({reason})",
            "grader": {"model_id": MODEL_ID, "model_version": MODEL_VERSION},
            "counts": counts,
            "floors": _floors(),
            "kappa_substantial_band": KAPPA_SUBSTANTIAL_BAND,
        }
        _write(report)
        _print(report)
        return 2

    # Pilot grades with the same real pinned client as --report; only --dry-run
    # uses the offline DeterministicClient.
    client, grader = _grader_stamp(dry_run)
    sc1 = measure_sc1(frozen["matched_pairs"], client)
    sc4 = measure_sc4(frozen["route_failures"], client)
    kappa = measure_kappa(frozen["kappa"], client)

    status = "dry_run" if dry_run else "pilot" if pilot else "measured"
    report = {
        "status": status,
        "grader": grader,
        "counts": counts,
        "floors": _floors(),
        "sc1": sc1,
        "sc4": sc4,
        "kappa": {"verdict": kappa["verdict"], "route_quality": kappa["route_quality"], "n": kappa["n"]},
        "kappa_substantial_band": KAPPA_SUBSTANTIAL_BAND,
        "detail": {"sc1_items": sc1["items"], "sc4_items": sc4["items"], "kappa_items": kappa["items"]},
    }
    if dry_run:
        report["warning"] = (
            "DRY RUN — graded by the offline keyword grader (DeterministicClient), "
            "not the pinned model, and over an insufficient seed set. These numbers "
            "prove the pipeline runs; they are NOT the Phase 0b measurement."
        )
    if pilot:
        report["interpretation"] = PILOT_INTERPRETATION
    _write(report)
    _print(report)

    # A dry run proves plumbing; a pilot indicates direction. Neither passes or
    # fails a gate, so both return 0 whenever they actually ran.
    if dry_run or pilot:
        return 0
    return 0 if (sc1["pass"] and sc4["pass"]) else 1


def _print(report: dict) -> None:
    print(f"Phase 0b grading harness — status: {report['status'].upper()}")
    print(f"  frozen set: {report['counts']}  (floors {report['floors']})")
    print(f"  grader: {report['grader']}")
    if report["status"] == "blocked":
        print(f"  BLOCKED: {report['reason']}")
        print("  No SC-1 / SC-4 / κ produced — a number on n<floor is not a measurement.")
        print(f"  Report written to {REPORT_PATH}")
        return
    if "warning" in report:
        print(f"  ⚠ {report['warning']}")
    sc1, sc4, k = report["sc1"], report["sc4"], report["kappa"]
    print(f"  SC-1 separation: {sc1['separated']}/{sc1['matched_pairs']} "
          f"= {sc1['separation_rate']:.0%}  (≥{sc1['threshold']:.0%}) "
          f"{'PASS' if sc1['pass'] else 'FAIL'}")
    print(f"  SC-4 route-failure detection: {sc4['flagged']}/{sc4['route_failures']} "
          f"= {sc4['route_failure_rate']:.0%}  (≥{sc4['threshold']:.0%}) "
          f"{'PASS' if sc4['pass'] else 'FAIL'}")
    print(f"  κ (substantial band ≥{report['kappa_substantial_band']}): "
          f"verdict={k['verdict']:.2f}  route_quality={k['route_quality']:.2f}  (n={k['n']})")
    if "interpretation" in report:
        print(f"  ⓘ {report['interpretation']}")
    print(f"  Report written to {REPORT_PATH}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Phase 0b grading harness")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--report", action="store_true",
                       help="measure with the real pinned model (Opus 4.8)")
    group.add_argument("--pilot", action="store_true",
                       help="real pinned model over the below-floor pilot set; direction only, never a gate")
    group.add_argument("--dry-run", action="store_true",
                       help="offline plumbing check with the deterministic grader (not a measurement)")
    args = parser.parse_args(argv)
    return run(dry_run=args.dry_run, pilot=args.pilot)


if __name__ == "__main__":
    sys.exit(main())
