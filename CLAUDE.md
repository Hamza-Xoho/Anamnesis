# Anamnesis

A local MCP service holding one learner's knowledge state — readable by a teaching conversation, not writable by it. Teaching is **not** implemented here; it stays in the external model driven by `teaching/`.

## Commands

```
uv sync                                  # install
pytest tests/contract/ -v                # the contract — frozen, must stay green
pytest tests/ -v                         # everything
ruff check . && mypy .                   # lint + types
anamnesis status                         # the digest, human-readable
anamnesis replay --verify                # drop derived state, replay, diff. Exit 1 on mismatch
anamnesis dispatcher run                 # the always-on process
```

## Invariants

Enforced by hooks, not by your goodwill. If a hook blocks you, the code is wrong — do not work around it.

- **INV-1** `core/` makes no model or network calls. It is the pure replayable layer.
- **INV-2** `agents/examiner/` never imports `server/`, `dispatcher/`, `cli/` or `channels/`.
- **INV-3** Only `core/reducer.py` writes derived tables. Status has no field to overwrite.
- **INV-4** The Obsidian vault is an export target and is never read back as state.
- **INV-5** `memory/` never references route quality. The rating derives from verdict alone.
- **INV-6** `tests/contract/` is frozen. New files may be created; existing ones may not be modified or deleted.
- **INV-7** The event log is append-only. Supersede by appending, never by editing.

## Boundaries

- `core/` depends on nothing in this project. Everything else may depend on it.
- `server/`, `dispatcher/`, `candidates/` append through `core/store.append` — never a raw cursor.
- `export/` reads `core/`, is imported only by `cli/`, and reads the vault never.
- A refusal is a **successful** result carrying `refused`/`reason_code`/`message`/`remedy`/`blocking`, and appends a `refused` event. Never a protocol error.
- `grade_attempt` takes `attempt_id` and nothing else.

## Where things are

- Decisions, interfaces, schemas: `spec/design-spec.md`
- What must be tested and why: `tests/test-contract.md`
- Current phase brief: `prompts/`
- Conventions, on demand: `.claude/skills/`

## Compact instructions

When summarising this conversation, preserve: interface changes and their rationale, the list of modified files, and any error messages with their resolutions. Summarise exploration briefly.

> A backstop, not a guarantee — nothing enforces it. The invariants above are re-stated deterministically by the session-start hook, which is what actually survives a long session. Do not move anything load-bearing here.
