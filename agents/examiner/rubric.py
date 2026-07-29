"""The rubric (design-spec §3.4). Frozen at authoring, immutable.

FR-3: a rubric carries a non-empty `claims` list AND a non-empty `route_markers`
list. A rubric with zero route markers is rejected at construction — never
silently accepted.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field


class RubricError(ValueError):
    """Raised when a rubric violates FR-3 (missing claims or route markers)."""


@dataclass(frozen=True)
class Rubric:
    claims: tuple[str, ...] = field(default=())
    route_markers: tuple[str, ...] = field(default=())

    def __post_init__(self) -> None:
        # Accept lists at the call site; store as immutable tuples.
        object.__setattr__(self, "claims", tuple(self.claims))
        object.__setattr__(self, "route_markers", tuple(self.route_markers))
        if not self.claims:
            raise RubricError("a rubric requires at least one required claim (FR-3)")
        if not self.route_markers:
            raise RubricError("a rubric requires at least one route marker (FR-3)")

    @classmethod
    def from_dict(cls, data: dict) -> "Rubric":
        return cls(
            claims=tuple(data.get("claims") or ()),
            route_markers=tuple(data.get("route_markers") or ()),
        )

    def canonical_json(self) -> str:
        # Sorted keys, no whitespace (design-spec §3.4).
        return json.dumps(
            {"claims": list(self.claims), "route_markers": list(self.route_markers)},
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

    @property
    def rubric_hash(self) -> str:
        digest = hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()
        return f"sha256:{digest}"
