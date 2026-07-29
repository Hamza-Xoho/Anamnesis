# Phase 7 — Trial and evaluation

## Before you paste — setup only

**1. Launch a fresh session** from the repo root:

```bash
claude --model sonnet --effort high
```

**2. Run these in the session, before pasting:**

| Command | Why |
|---|---|
| `/status` | Confirm the model and effort actually took. Effort persists across sessions, so it may not be what you left behind |
| `/context` | This phase reads the whole contract for the coverage audit. Start clean |
| `/clear` | Only if you're reusing a terminal rather than opening a new one. A genuinely fresh session is better |

**Plan mode:** no.
**Auditors:** all three, once, as the closing audit.
**Why this model:** mostly SQL and a coverage sweep, not construction. The interpretation is yours, not the agent's, and the four weeks are calendar time rather than model time. Don't raise effort hoping for better numbers — the numbers are the finding.

---

**▼ Everything below this line is the prompt. Paste from here.**

---

> Paste this into a fresh session. Self-contained: assume no memory of earlier phases.
>
> **This phase is mostly not coding.** It is four weeks of using the thing, then measuring what happened.


## Goal

The system has been the sole learning tool for four consecutive weeks with the prototype disabled, and every KPI has a measured figure from the real log rather than a target.

## Requirements in scope

- **SC-5** — proportion of graded attempts arriving via the ambient channel
- **SC-7** — every milestone from phase 2 onward shipped in a state usable for real study
- **NFR-1** — nothing beyond probe text, learner response and rubric leaves the machine
- **NFR-6** — per-attempt grading cost bounded and cheap enough to run on every ambient probe

## Read first

- `spec/design-spec.md` §8 Observability, §9 Open items
- `tests/test-contract.md`, the Phase 7 table and the Coverage check

## Not in this phase

- **No new features.** Anything discovered during the trial goes in a list, not in the code. A feature added mid-trial invalidates the measurement
- **No target-chasing.** If ambient yield comes in at 14%, that is the finding. The proposal's ≥20% was calibrated against 11–13% reported baselines; the charter's ≥50% exceeded every measured figure and was retired for that reason
- **No FSRS parameter fitting yet.** That needs 2–3 months of history and is a separate exercise (Q-8)

## Work in scope

1. **Run the trial.** Four consecutive weeks, prototype disabled. Log everything.
2. **Build the KPI queries** as documented SQL over `events` — ambient yield, schedule adherence, bypass rate, per-attempt cost.
3. **Audit test coverage**: `test_all_must_requirements_have_passing_tests` must pass.
4. **Verify egress**: `test_nfr1_no_egress_beyond_inference`.
5. **Write it up.** What was measured, against what target, with the mechanism where they differ.

## Definition of done

1. `test_all_must_requirements_have_passing_tests` and `test_nfr1_no_egress_beyond_inference` pass
2. `test_sc5_ambient_yield` and `test_nfr6_per_attempt_cost_bounded` report figures, and those figures are written back into the spec's §9 Open items
3. Four consecutive weeks of sole use, evidenced by the log itself
4. No new features added during the trial window

## Gate

```
pytest tests/contract/ -v && anamnesis status --json > trial-final.json
```

Then confirm by hand: **look at four weeks of your own event log.** Are there gaps where you fell back to the prototype? Did anything sit overdue? Does the confidence map match what you actually know when you test yourself cold on three concepts it calls solid?

That last check is the whole project. If the map is right, it worked.

## Stop

Report the measured figures. Do not adjust the system to improve them.
