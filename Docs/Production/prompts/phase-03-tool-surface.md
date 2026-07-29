# Phase 3 — The tool surface

## Before you paste — setup only

**1. Launch a fresh session** from the repo root:

```bash
claude --model fable --effort high
```

**2. Run these in the session, before pasting:**

| Command | Why |
|---|---|
| `/status` | Confirm Fable actually took. It needs Claude Code v2.1.170+; older builds don't show it and fall through silently. `claude update` if it didn't |
| `/tool-surface-conventions` | Preload the refusal shape and naming rules before any tool gets written |
| `/plan` | Plan first, approve, then execute. This is the phase where a wrong shape is most expensive to undo |
| `/goal one topic taught end to end through the connector, with every §6.1 reason code refusing and tested` | Fable holds a goal across a long session and keeps working until it holds. This is the phase that's worth one |
| `/clear` | Only if you're reusing a terminal rather than opening a new one. A genuinely fresh session is better |

**Auditors:** `refusal-audit` before the gate. Non-negotiable — it audits the contribution claim itself.
**Why this model:** the largest phase and the one the whole claim rests on — thirteen tools, nine reason codes, a size-bounded digest and the teaching instruction files, all interacting. This is Fable's documented case: ambiguous, architecture-shaped, larger than a single sitting. Describe the outcome and let it plan the path, and skip the "remember to test" reminders — it verifies more on its own than smaller models do.

---

**▼ Everything below this line is the prompt. Paste from here.**

---

> Paste this into a fresh session. Self-contained: assume no memory of earlier phases.
>
> **This phase is the project's contribution.** "Ordering enforced by refusing preconditions" is claimed here or nowhere.


## Goal

An MCP server over stdio that a teaching conversation can read but not write, refusing every call whose preconditions are unmet — with one topic taught end to end through it.

## Requirements in scope

- **FR-2** — probes authored at topic close for concepts actually taught, never in advance
- **DR-1** — grading accepts only a probe reference and a verbatim response
- **DR-2** — each of the four documented prototype failures has a tool precondition that refuses
- **DR-3** — teaching without recorded attempts is visible as missing evidence
- **DR-4** — read-back is one call, payload bounded at realistic graph size
- **CON-3** — the examiner never receives conversation history
- **CON-4** — rubrics are immutable once authored
- **SC-6** — zero rubrics for concepts never taught or never selected

## Read first

- `spec/design-spec.md` §4.1 Tool surface, §4.2 The digest, §6 Error and refusal semantics (all of it), §2 (the `server/` and `agents/examiner/` rows)
- `tests/test-contract.md`, the Phase 3 table

## Not in this phase

- **No dispatcher, no Telegram, no scheduled anything.** Phase 5
- **No candidate generators beyond the route-failure one built in phase 2.** Phase 4
- **No exports.** Phase 4
- **No teaching logic in the server.** The server exposes tools; the model on the other side does the pedagogy. If you find yourself writing a prompt that teaches, you are in the wrong module
- **No content library, no pre-authored curricula.** The learner supplies the material. Shipping curricula is a content business, not this one
- **Do not make a refusal an MCP protocol error.** It is a successful result carrying `refused: true` (D-7). Getting this wrong silently voids DR-6

## Also produce

`teaching/` — the prose instruction files that drive the external model, plus an install script that copies them into the Claude config. They are the other half of this interface; a tool rename that leaves them stale is a broken build.

## Definition of done

1. These tests pass, and were failing before the implementation:
   `test_dr1_grade_attempt_takes_only_attempt_id`, `test_dr1_no_code_path_from_caller_verdict_to_grade_event`,
   `test_dr2_refuses_open_topic_with_due_item_outstanding`, `test_dr2_refuses_attempt_without_onscreen_condition`,
   `test_dr2_refuses_regrade_of_graded_attempt`, `test_dr2_refuses_caller_supplied_review_date`,
   `test_dr3_unevidenced_topic_appears_in_digest`, `test_dr3_refuses_close_of_unevidenced_topic`,
   `test_dr4_digest_is_one_call`, `test_dr4_digest_bounded_at_scale`,
   `test_fr2_close_authors_probe_per_taught_concept`, `test_sc6_no_rubric_for_untaught_concept`,
   `test_con4_rubric_is_immutable`, `test_con3_examiner_has_no_conversation_import`,
   `test_d7_refusal_is_success_result_and_event`, `test_d9_merge_requires_prior_proposal`
2. Every reason code in spec §6.1 has a test that triggers it
3. No change to files outside `server/`, `teaching/`, `agents/examiner/`, `tests/contract/`

## Gate

```
pytest tests/contract/phase3/ -v && python -m server.selfcheck --enumerate-preconditions
```

Then confirm by hand — this is the phase where the manual check matters most:

1. **Teach one topic end to end** through the connector, in a real session. Author probes, record attempts, grade, close.
2. **Try to cheat.** Pass a verdict to `grade_attempt`. Argue with a grade. Close a topic you taught but never tested. Confirm each is refused, and that the refusal told you what to do instead.
3. **Check `get_state` after a session where you taught and recorded nothing.** The topic must appear under `unevidenced_topics`. If it doesn't, DR-3 is not implemented, whatever the tests say.

## Stop

When the definition of done is met, stop and report. Do not begin the next phase.
