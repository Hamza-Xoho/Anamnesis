# Phase 4 — Candidates, export, instrumentation

## Before you paste — setup only

**1. Launch a fresh session** from the repo root:

```bash
claude --model opusplan
```

**2. Run these in the session, before pasting:**

| Command | Why |
|---|---|
| `/status` | Confirm the model and effort actually took. Effort persists across sessions, so it may not be what you left behind |
| `/plan` | **Required, not optional.** `opusplan` only uses Opus *while plan mode is active*, then drops to Sonnet to execute. Skip this and you get Sonnet for the whole phase — the wrong half of the trade |
| `/clear` | Only if you're reusing a terminal rather than opening a new one. A genuinely fresh session is better |

**Auditors:** `boundary-audit` before the gate.
**Why this model:** wide design space at the front — six generators, and the ranking weights are yours to choose under D-29 — then a long tail of straightforward implementation. Paying Opus rates for the render loop is waste; planning the ranking on Sonnet is worse. `opusplan` splits it at exactly the right seam.

---

**▼ Everything below this line is the prompt. Paste from here.**

---

> Paste this into a fresh session. Self-contained: assume no memory of earlier phases.


## Goal

The app answers "what should I do now" from the log alone — ranked candidates with visible evidence, notes rendered into Obsidian, refusals measurable, and a CLI that shows you system state without opening a session.

## Requirements in scope

- **FR-10** — generate candidates from the event log: unstudied prerequisites, route failures, untested angles, untested cross-links, calibration gaps, avoided items
- **FR-11** — rank candidates, weighting solid concepts resting on unstudied prerequisites highest
- **FR-15** — render concept notes as views over the log, export to Obsidian
- **FR-18** — parse a supplied source spec into a topic tree with weights and dependencies, for planning only
- **DR-6** — refusals are instrumented so residual bypass is measurable
- **CON-5** — the knowledge graph and notes are an export target, never the source of truth
- **NFR-2** — every status traceable to the attempts that produced it, in one query

## Read first

- `spec/design-spec.md` §3.3 Derived tables, §8 Observability, §2 (the `candidates/`, `export/`, `cli/` rows), §1 row D-29 (ranking weights and their bound)
- `tests/test-contract.md`, the Phase 4 table

## Not in this phase

- **No dispatcher.** Phase 5. Candidates are shown, not sent
- **No reading from the vault, ever.** Export is write-only. This is hook-enforced, and it is the bug class the prototype died of
- **No retrieval from source content during teaching.** FR-18 parses structure — headings, weights, dependencies. Storing body text turns this into the corpus-RAG product the charter names as a non-goal
- **No interactive graph visualisation.** Cut from scope (charter FR-20)
- **No note authored from anything but retrieval.** Nothing enters the export that was not earned by a graded attempt. A note that looks like knowledge and isn't is the failure the whole system exists to prevent
- **Do not let a candidate become dispatchable.** The two lanes never merge (CON-8)

## Definition of done

1. These tests pass, and were failing before the implementation:
   `test_fr10_candidate_names_generator_and_evidence`, `test_fr10_all_six_generators_produce_candidates`,
   `test_fr11_ranking_is_reproducible_from_log`, `test_fr11_prereq_gap_outranks_others`,
   `test_fr15_export_is_deterministic`, `test_con5_vault_is_never_read`,
   `test_fr18_source_parsed_for_structure_only`, `test_dr6_every_refusal_is_an_event`,
   `test_dr6_bypass_rate_computable_from_log`, `test_nfr2_status_traces_to_attempts_in_one_query`
2. `anamnesis status` prints the digest legibly, including dispatcher status (which will read `unknown` until phase 5)
3. The bypass-rate query is a single documented SQL statement over `events`
4. No change to files outside `candidates/`, `export/`, `cli/`, `tests/contract/`

## Gate

```
pytest tests/contract/phase4/ -v && anamnesis status && anamnesis export obsidian
```

Then confirm by hand: run `anamnesis export obsidian` twice and diff the output directory — it must be empty. Open the vault and confirm the notes are readable and every claim links to attempts. Then **edit a note in the vault by hand**, re-export, and confirm your edit is overwritten without complaint — the vault is downstream, and if the system flinched, something is reading it.

## Stop

When the definition of done is met, stop and report. Do not begin the next phase.
