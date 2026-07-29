---
name: event-conventions
description: How events, the append path and the reducer work in Anamnesis, and what to do when you need a new event type or a schema change. Use when adding an event type, changing a payload, touching core/store.py or core/reducer.py, or when replay verification fails.
---

# Event and reducer conventions

The event log is the only irreplaceable artifact in this project. Everything else regenerates by replay. Every rule below exists because the prototype had an LLM writing its own state and reading its prose back as truth.

## The three rules

1. **`core/store.append` is the only function that inserts into `events`.** Not "should be" — the boundary hooks block anything else.
2. **`core/reducer.py` is the only module that writes derived tables.** Status has no field to overwrite. That is the trust model, not a style preference.
3. **Events are never edited or deleted.** Supersede by appending. There is no correction path, because a correction path is an assertion path.

## Adding an event type

1. Add it to `spec/design-spec.md` §3.2 with its payload fields. The spec is the source; the code follows it.
2. Add the type constant in `core/events.py` with `schema_version: 1`.
3. Handle it in the reducer. **An unhandled event type must raise on replay, not be skipped** — a silently ignored event is derived state that cannot be reproduced, which is NFR-3 broken in the quietest possible way.
4. Add a contract test that appends one and asserts the derived effect.
5. Run `anamnesis replay --verify`.

## Changing a payload

Never change an existing type's payload shape in place. Bump `schema_version` and handle both versions in the reducer, permanently. Old events must be interpretable exactly as they were written, years later — that is what makes a confidence claim from 2027 comparable to one from 2026.

If handling two versions feels like too much bookkeeping, that is the correct amount of friction. It is what stops the schema drifting under a record nobody can re-derive.

## Actors

`teaching` · `examiner` · `dispatcher` · `cli` · `system`. Set it honestly — the bypass-rate query (DR-6) partitions on it, and a mislabelled actor makes the project's own measurement wrong.

## When replay verification fails

Replay is deterministic by construction, so a failure means one of four things, in order of likelihood:

1. Something outside the reducer wrote a derived table. Run the `writer-audit` subagent.
2. The reducer reads wall-clock time, a random seed, or dict iteration order. All three are non-determinism; none announces itself.
3. An event type is handled inconsistently across schema versions.
4. The log was edited. This should be impossible — if it happened, find out how before fixing anything else.

Do not "fix" a replay mismatch by regenerating the expected state. That converts a real failure into a passing test and voids NFR-3.
