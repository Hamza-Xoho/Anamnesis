# Phase 2 — Memory and the two lanes

## Before you paste — setup only

**1. Launch a fresh session** from the repo root:

```bash
claude --model sonnet --effort xhigh
```

**2. Run these in the session, before pasting:**

| Command | Why |
|---|---|
| `/status` | Confirm the model and effort actually took. Effort persists across sessions, so it may not be what you left behind |
| `/event-conventions` | The reducer changes here too — the route-failure seam is reducer work |
| `/clear` | Only if you're reusing a terminal rather than opening a new one. A genuinely fresh session is better |

**Plan mode:** no.
**Auditors:** `writer-audit` and `boundary-audit` before the gate.
**Why this model:** well specified, but the probe state machine has one edge an agent will try to simplify away — `seeded → retained` requires a cold attempt. `xhigh` buys the care to keep it. The CON-12 half is hook-enforced regardless.

---

**▼ Everything below this line is the prompt. Paste from here.**

---

> Paste this into a fresh session. Self-contained: assume no memory of earlier phases.


## Goal

Per-probe scheduling through FSRS-6, a concept rollup that refuses to be a single number, and two queues that cannot merge — with route failure emitting a candidate rather than corrupting a rating.

## Requirements in scope

- **FR-7** — per-probe memory state and next review date
- **FR-8** — roll probe states up into a concept-level view, per probe class
- **FR-9** — two separate queues: due (dispatched, non-negotiable) and candidates (ranked, chosen)
- **FR-22** — a route failure spawns a new probe target on the same concept; route quality never folds into the current probe's rating
- **CON-9** — an in-session pass may seed a memory model but never establish retention
- **CON-12** — the scheduler's rating input derives from verdict only

## Read first

- `spec/design-spec.md` §5.1 Probe state transitions, §5.3 Route failure, §1 rows D-10 and D-19, §2 (the `memory/` row)
- `tests/test-contract.md`, the Phase 2 table

## Not in this phase

- **No candidate *generators*.** FR-22 emits one candidate type; the other five generators are phase 4
- **No ranking function.** Route-failure candidates are rank-forced to the top; general ranking is phase 4
- **No dispatch.** The due lane exists and is queryable. Nothing sends anything until phase 5
- **No bulk review queue.** This is not a flashcard trainer. Rote reps live in Anki (D-11); Anamnesis runs targeted probes only
- **No parameter optimisation.** Default pretrained FSRS parameters. Personal fitting needs 2–3 months of real history and is not a build task
- **`memory/` must not reference `route_quality` in any form** — not in a comment, not in a variable name. This is hook-enforced, and it is the mechanical form of CON-12

## Definition of done

1. These tests pass, and were failing before the implementation:
   `test_fr7_probe_carries_retrievability_and_due_date`, `test_fr8_concept_rolls_up_per_probe_class`,
   `test_fr8_concept_has_no_status_column`, `test_fr9_due_item_cannot_be_dismissed_by_omission`,
   `test_fr9_candidate_cannot_be_auto_dispatched`, `test_fr22_route_failure_emits_candidate`,
   `test_fr22_route_failure_rates_verdict_only`, `test_con12_no_rating_path_from_route_quality`,
   `test_con9_onscreen_attempt_cannot_establish_retention`, `test_d19_verdict_to_rating_mapping`
2. `py-fsrs` is pinned to 6.3.1 and vendored
3. `anamnesis replay --verify` still passes — memory state is derived, not stored independently
4. No change to files outside `memory/`, `core/reducer.py`, `tests/contract/`

## Gate

```
pytest tests/contract/phase2/ -v && anamnesis replay --verify
```

Then confirm by hand: grade a probe with `route_quality = route_failure` and a **passing** verdict. Confirm three things — the probe's due date advanced as a pass, a top-ranked candidate appeared naming the missed route marker, and nothing anywhere recorded a lower rating. Then grep `memory/` for `route` and confirm it returns nothing.

## Stop

When the definition of done is met, stop and report. Do not begin the next phase.
