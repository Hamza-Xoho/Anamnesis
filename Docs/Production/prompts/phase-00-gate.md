# Phase 0 — The gate

## Before you paste — setup only

**1. Launch a fresh session** from the repo root:

```bash
claude --model opus --effort xhigh
```

**2. Run these in the session, before pasting:**

| Command | Why |
|---|---|
| `/status` | Confirm the model and effort actually took. Effort persists across sessions, so it may not be what you left behind |
| `/doctor` | First run only — flags a broken hook install or a subagent name collision, both of which are otherwise silent |
| `/config` | Turn **off** *"switch models when a message is flagged"*. This phase feeds physiology and pharmacology to a grader; you want to be asked, not silently moved |
| `/plan` | Plan mode on. Approve the harness design before it writes anything |
| `/clear` | Only if you're reusing a terminal rather than opening a new one. A genuinely fresh session is better |

**Auditors:** none yet — there's no code for them to sweep.
**Why this model:** short, narrow and high-stakes rather than long. The code is small; a wrong call here invalidates every later phase, so buy reasoning depth. Deliberately not Fable — this isn't a long autonomous task, it's a brief one that must be right.
**Watch for:** Opus 5 has no fallback beneath its biology classifier, so a flag ends in a refusal rather than a re-route. If that starts happening, move this phase to `--model fable` and accept being routed up to Opus 5 mid-session. `Docs/README.md` §5 has the detail.

---

**▼ Everything below this line is the prompt. Paste from here.**

---

> Paste this into a fresh session. It is self-contained on purpose: assume no memory of earlier phases.
>
> **This phase can invalidate the whole design.** If its gate fails, stop. The architecture changes and no further phase runs.


## Goal

A grading harness that grades seeded answers blind against frozen rubrics, and a measurement of whether it separates understanding from fluent recall well enough for the rest of the project to be worth building.

## Requirements in scope

- **FR-3** — every rubric carries required claims *and* route markers; a rubric with no route markers is rejected at authoring
- **FR-4** — grade blind: examiner input is exactly concept, prompt, verbatim response, rubric, `answer_was_onscreen`
- **FR-5** — three separate outputs per attempt: verdict, route quality, expressed confidence. Never merged
- **NFR-7** — every grade records model identity, version and prompt hash
- **SC-1** — ≥90% of matched pairs rank the confidently-wrong answer below the hedged-correct one
- **SC-4** — ≥80% of right-answer-wrong-mechanism responses recorded as route failures

## Read first

- `spec/design-spec.md` §3.4 Rubric, §4.1 (the `grade_attempt` row only), §7 Configuration and pinning
- `tests/test-contract.md`, the Phase 0 table

## Not in this phase

- **No event log, no reducer, no database.** The harness reads fixtures and writes results to a file. Phase 1 builds the store
- **No MCP server, no tools, no refusals.** Phase 3
- **No FSRS, no scheduling.** Phase 2
- **No teaching.** Teaching is not reimplemented anywhere in this project
- **No fine-tuned or specialised models.** Frontier models throughout, logging everything, so the logs become the training set later (ADR-9). Shrinking the examiner before you have its data is premature
- Do not author the evaluation set's content yourself. It must come from real material — ask for it

## What you need from the human before starting

This phase splits in two. **0a needs nothing from anyone; 0b is blocked without real data.** Do 0a first — do not stop the whole phase because 0b's inputs are missing.

### 0a — mechanism. Build this now.

These ask *does the code path exist and hold?*, not *how good is the grader?* Synthetic fixtures are fine here, because a leak in a code path leaks regardless of who wrote the text. Keep them in `tests/fixtures/synthetic/`, never mixed with the frozen set.

`test_fr3_rubric_carries_claims_and_route_markers`, `test_fr3_rejects_rubric_with_no_route_markers`,
`test_fr4_examiner_input_is_exactly_five_fields`, `test_fr4_verdict_invariant_to_surrounding_conversation`,
`test_fr5_three_distinct_outputs`, `test_fr5_expressed_confidence_has_no_path_to_verdict`,
`test_nfr7_grade_records_model_identity`

### 0b — measurement. Blocked until the human delivers.

These ask *how good is the grader on real answers?* A model-written answer set makes the harness measure itself, so these cannot proceed without material drawn from real work. Frozen set lives in `tests/fixtures/frozen/`:

1. **Matched pairs** — for each concept, a confidently-wrong answer and a hedged-correct one, with a rubric
2. **Right-answer-wrong-mechanism responses** — correct conclusions reached without the route marker
3. **A held-out human-labelled sample** for the κ comparison

`test_sc1_grading_separation_on_seeded_set`, `test_sc4_route_detection_on_seeded_set`, `test_gate_kappa_against_human_labels`

If the frozen set does not exist: build 0a, report that 0b is blocked, name what's missing, and stop there. Do not author the frozen set yourself, and do not fill it from a model — including as a "placeholder" or "example" the human will replace later. A placeholder that survives into the gate silently converts the measurement into a self-assessment.

**The repo must be a git repository** before 0b can complete, since freezing the set means committing it. If `git init` hasn't happened, say so.

## Definition of done

**0a:**

1. These tests pass, and were failing before the implementation:
   `test_fr3_rubric_carries_claims_and_route_markers`, `test_fr3_rejects_rubric_with_no_route_markers`,
   `test_fr4_examiner_input_is_exactly_five_fields`, `test_fr4_verdict_invariant_to_surrounding_conversation`,
   `test_fr5_three_distinct_outputs`, `test_fr5_expressed_confidence_has_no_path_to_verdict`,
   `test_nfr7_grade_records_model_identity`
2. Synthetic fixtures are under `tests/fixtures/synthetic/` and are obviously labelled as such

**0b:**

3. `test_sc1_grading_separation_on_seeded_set` and `test_sc4_route_detection_on_seeded_set` pass
4. `test_gate_kappa_against_human_labels` runs and reports κ per criterion, against the substantial band
5. The evaluation set is frozen — committed to git, and any later change invalidates the gate
6. No change to files outside `agents/examiner/`, `tests/contract/`, `tests/fixtures/`

## Gate

Run this yourself before accepting the phase. Do not accept a report that it passed.

```
pytest tests/contract/phase0/ -v && python -m agents.examiner.harness --report
```

Then confirm by hand: **read the report.** Take three pairs the harness got right and check you agree with its reasoning, and take every pair it got wrong and check whether the failure is the grader or the rubric. If the misses cluster on one rubric, the problem is RISK-2 (rubric quality), not RISK-1 (grading) — and that is a different decision.

**If SC-1 or SC-4 misses its threshold: stop.** Do not proceed to phase 1. The charter's fallback is to restrict v1 to domains with checkable answers and treat open-domain grading as a research track. That is a decision for the human, not a patch.

## Stop

When the definition of done is met, stop and report. Do not begin the next phase.
