# Phase 1 — The log

## Before you paste — setup only

**1. Launch a fresh session** from the repo root:

```bash
claude --model sonnet --effort high
```

**2. Run these in the session, before pasting:**

| Command | Why |
|---|---|
| `/status` | Confirm the model and effort actually took. Effort persists across sessions, so it may not be what you left behind |
| `/context` | Confirm you're starting near-empty. This phase generates a lot of test output and you want the headroom |
| `/event-conventions` | Preload the event and reducer rules — you'll be inside them for the whole phase, so paying the context cost up front is cheaper than three lookups |
| `/clear` | Only if you're reusing a terminal rather than opening a new one. A genuinely fresh session is better |

**Plan mode:** no — the spec is tight enough here that planning is pure latency.
**Auditors:** `writer-audit` before the gate.
**Why this model:** tightly specified and mechanical, well inside Sonnet's range. Raise with `/effort xhigh` mid-session if replay determinism or the crash-safety test fights back; those are the two places subtlety hides.

---

**▼ Everything below this line is the prompt. Paste from here.**

---

> Paste this into a fresh session. Self-contained: assume no memory of earlier phases.


## Goal

An append-only event log and a deterministic reducer, such that dropping every derived table and replaying reproduces the state exactly.

## Requirements in scope

- **FR-6** — append all activity to an immutable log; compute all state by reducer
- **NFR-3** — replay reproduces derived state byte-identically
- **NFR-4** — the log is append-only and survives process crash mid-write
- **CON-1** — status and confidence are derived. No component writes them; there is no field to overwrite
- **SC-2** — no code path exists by which an assertion can raise a status

## Read first

- `spec/design-spec.md` §2 Module boundaries, §3.1 Event envelope, §3.2 Event types, §3.3 Derived tables
- `tests/test-contract.md`, the Phase 1 table

## Not in this phase

- **No FSRS, no scheduling, no due dates.** `probe_state` exists as a table; phase 2 fills its memory fields
- **No MCP server, no tools.** Phase 3
- **No candidate generation.** Phase 4 — the `candidate_generated` event type exists; nothing produces one yet
- **No caching, no snapshots, no incremental replay.** Materialised tables rebuilt by full replay is the decision (D-5). An optimisation added here breaks the invariant inside a large diff
- **No user or tenant column anywhere.** v1 has exactly one user, no accounts, no auth, no sync (CON-11, D-18). Adding one now is dead weight for the whole of v1
- **No model calls anywhere in `core/`.** This is hook-enforced

## Definition of done

1. These tests pass, and were failing before the implementation:
   `test_fr6_replay_reproduces_derived_state`, `test_nfr3_replay_is_byte_identical`,
   `test_nfr4_log_survives_crash_mid_write`, `test_con1_no_write_path_to_derived_state`,
   `test_sc2_status_is_pure_function_of_log`, `test_events_are_append_only`,
   `test_seq_is_monotonic_and_gapless`, `test_replay_honours_old_schema_versions`
2. `anamnesis replay --verify` exists and exits 0 on a populated log, 1 on a tampered one
3. `core/store.append` is the only function in the repo that inserts into `events`
4. No change to files outside `core/`, `cli/`, `tests/contract/`

## Gate

```
pytest tests/contract/phase1/ -v && anamnesis replay --verify
```

Then confirm by hand: seed a log with a few dozen events, note the derived table row counts, **delete the derived tables**, run `anamnesis replay --verify`, and confirm the counts come back identical. Then hand-edit one byte in an event payload and confirm the verify exits 1.

## Stop

When the definition of done is met, stop and report. Do not begin the next phase.
