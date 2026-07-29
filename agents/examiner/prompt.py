"""Loads the pinned examiner prompt and records its hash (NFR-7, design-spec §7)."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"


@dataclass(frozen=True)
class LoadedPrompt:
    name: str
    text: str
    prompt_hash: str


def load_prompt(name: str = "examiner") -> LoadedPrompt:
    text = (PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return LoadedPrompt(name=name, text=text, prompt_hash=f"sha256:{digest}")
