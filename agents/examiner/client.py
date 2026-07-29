"""Examiner clients — the thing that turns an ExaminerInput into a raw grade.

Two implementations:

- `DeterministicClient` — hermetic, offline, keyword-matching. It is the grader
  the Phase 0a *mechanism* tests run against, and the `--dry-run` plumbing check.
  It matches keywords; it does NOT understand. It must never stand in for the
  Phase 0b measurement.

- `AnthropicExaminerClient` — the real, pinned frontier grader (Opus 4.8) used by
  `harness --report` for the Phase 0b measurement. Imports `anthropic` lazily so
  Phase 0a runs with no network dependency installed.

Both are pure functions of the ExaminerInput plus the pinned prompt: verdict and
route_quality are derived from claim/route-marker coverage, expressed_confidence
from register alone. There is no path from register into verdict (FR-5).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .examiner import ExaminerInput
from .prompt import load_prompt

# --- pinned model identity (design-spec §7, NFR-7) -------------------------
# Changing either of these requires re-baselining against the phase-0 set.
MODEL_ID = "claude-opus-4-8"
MODEL_VERSION = "2026-07-29"  # pinned snapshot date for this examiner baseline


@dataclass(frozen=True)
class RawGrade:
    verdict: str
    route_quality: str
    expressed_confidence: float


# --- deterministic offline grader (mechanism tests + dry runs) -------------

_STOPWORDS = frozenset(
    "a an the of to is are from and or by up can each its that this with for on "
    "in as it than not into out via so".split()
)
_HEDGES = frozenset(
    "maybe perhaps probably think might possibly guess unsure seems could "
    "apparently roughly somewhat".split()
)
_ASSERTIONS = frozenset(
    "definitely certainly clearly obviously undoubtedly certain surely "
    "confident absolutely".split()
)


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _significant(phrase: str) -> list[str]:
    return [t for t in _tokens(phrase) if t not in _STOPWORDS]


def _covered(phrase: str, response_tokens: set[str], threshold: float = 0.6) -> bool:
    sig = _significant(phrase)
    if not sig:
        return False
    hits = sum(1 for t in sig if t in response_tokens)
    return hits / len(sig) >= threshold


class DeterministicClient:
    """Hermetic keyword grader. NOT the 0b measurement grader."""

    model_id = "deterministic-examiner"
    model_version = "0a"

    def __init__(self) -> None:
        # Even the offline grader records the real pinned prompt hash (NFR-7).
        self.prompt_hash = load_prompt().prompt_hash

    def grade(self, x: ExaminerInput) -> RawGrade:
        response_tokens = set(_tokens(x.response))

        # verdict — from claim coverage only. Never reads register.
        claims = x.rubric.claims
        covered = sum(1 for c in claims if _covered(c, response_tokens))
        coverage = covered / len(claims) if claims else 0.0
        if coverage <= 0.0:
            verdict = "miss"
        elif coverage < 1.0:
            verdict = "partial"
        else:
            verdict = "hit"

        # route_quality — from route-marker coverage only, independent of verdict.
        markers = x.rubric.route_markers
        route_clean = bool(markers) and all(_covered(m, response_tokens) for m in markers)
        route_quality = "clean" if route_clean else "route_failure"

        # expressed_confidence — from register only. No claim content, no verdict.
        toks = _tokens(x.response)
        hedges = sum(1 for t in toks if t in _HEDGES)
        assertions = sum(1 for t in toks if t in _ASSERTIONS)
        conf = 0.5 + 0.1 * assertions - 0.1 * hedges
        conf = round(max(0.0, min(1.0, conf)), 2)

        return RawGrade(verdict=verdict, route_quality=route_quality, expressed_confidence=conf)


# --- real pinned grader (Phase 0b measurement) -----------------------------

_GRADE_SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": ["miss", "partial", "hit", "effortless_hit"]},
        "route_quality": {
            "type": "string",
            "enum": ["clean", "route_failure", "unassessable"],
        },
        "expressed_confidence": {"type": "number"},
    },
    "required": ["verdict", "route_quality", "expressed_confidence"],
    "additionalProperties": False,
}


class AnthropicExaminerClient:
    """The real examiner: the pinned frontier model, one blind call per attempt.

    Used only by `harness --report` for the Phase 0b measurement. Not exercised
    by the Phase 0a mechanism tests. `anthropic` is imported lazily so 0a needs
    neither the package nor an API key.
    """

    model_id = MODEL_ID
    model_version = MODEL_VERSION

    def __init__(self, model_id: str = MODEL_ID, model_version: str = MODEL_VERSION):
        import anthropic  # lazy: only needed for the real measurement

        self.model_id = model_id
        self.model_version = model_version
        self._prompt = load_prompt()
        self.prompt_hash = self._prompt.prompt_hash
        self._client = anthropic.Anthropic()

    def _render(self, x: ExaminerInput) -> str:
        claims = "\n".join(f"  - {c}" for c in x.rubric.claims)
        markers = "\n".join(f"  - {m}" for m in x.rubric.route_markers)
        return (
            f"concept: {x.concept}\n"
            f"prompt: {x.prompt}\n"
            f"answer_was_onscreen: {str(x.answer_was_onscreen).lower()}\n"
            f"rubric:\n  required_claims:\n{claims}\n  route_markers:\n{markers}\n"
            f"response (verbatim):\n{x.response}\n"
        )

    def grade(self, x: ExaminerInput) -> RawGrade:
        message = self._client.messages.create(
            model=self.model_id,
            max_tokens=1024,
            thinking={"type": "adaptive"},
            system=self._prompt.text,
            output_config={"format": {"type": "json_schema", "schema": _GRADE_SCHEMA}},
            messages=[{"role": "user", "content": self._render(x)}],
        )
        if message.stop_reason == "refusal":
            raise RuntimeError(
                "examiner model refused to grade "
                f"(category={getattr(message.stop_details, 'category', None)})"
            )
        import json

        text = next(b.text for b in message.content if b.type == "text")
        data = json.loads(text)
        return RawGrade(
            verdict=data["verdict"],
            route_quality=data["route_quality"],
            expressed_confidence=float(data["expressed_confidence"]),
        )
