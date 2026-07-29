# Phase 5 — The dispatcher

## Before you paste — setup only

**1. Launch a fresh session** from the repo root:

```bash
claude --model opus --effort xhigh
```

**2. Run these in the session, before pasting:**

| Command | Why |
|---|---|
| `/status` | Confirm the model and effort actually took. Effort persists across sessions, so it may not be what you left behind |
| `/permissions` | This phase writes a long-running process and talks to the network. Check what's auto-approved before it starts rather than after |
| `/plan` | Plan mode on — the catch-up and liveness semantics are worth agreeing before code |
| `/clear` | Only if you're reusing a terminal rather than opening a new one. A genuinely fresh session is better |

**Auditors:** `writer-audit` and `boundary-audit`.
**Why this model:** integration-heavy with real-world failure modes — timing, sleep/wake, delivery failure, catch-up arithmetic. When something misbehaves during the two-week soak, start that debugging session on `--model fable` instead: root-causing a background process that fails intermittently is precisely what it's best at.

---

**▼ Everything below this line is the prompt. Paste from here.**

---

> Paste this into a fresh session. Self-contained: assume no memory of earlier phases.
>
> **This is the phase whose absence broke the prototype.** A process that must run when nothing else is open, and must be visibly dead when it isn't.


## Goal

Due probes arrive on the learner's phone with no session open, replies come back graded as cold retrieval, and a stopped dispatcher is impossible to miss.

## Requirements in scope

- **FR-12** — dispatch due micro-probes within a hard daily budget, emitting nothing when nothing is due
- **FR-13** — accept a reply from the ambient channel and grade it as a cold, unaided attempt
- **DR-5** — dispatcher liveness reported inside the read-back payload
- **CON-7** — hard daily budget; silence is a valid output
- **CON-13** — a one-time learner-initiated handshake before the system may message unprompted
- **SC-3** — no probe sits past `review_due` beyond one dispatch cycle without dispatch or recorded deferral
- **NFR-5** — grade-and-reply round trip fast enough to feel conversational

## Read first

- `spec/design-spec.md` §1 rows D-3, D-12, D-13, §4.2 (the `dispatcher` block), §5.1 (the `due`/`dispatched`/`deferred` transitions), §6.2 Non-refusal errors
- `tests/test-contract.md`, the Phase 5 table

## Not in this phase

- **No backlog flooding.** After missed windows, send only today's within budget and record each missed window as an event (D-13). Draining a queue at the learner is how RISK-4 kills the loop
- **No importing `server/`.** The dispatcher shares the store, not the session. It writes through `core/store.append` like everything else
- **No mobile app.** The ambient channel *is* the mobile surface. A second client duplicates it for no gain
- **No second messaging channel.** Signal is the documented, un-built fallback. Building both now doubles the surface for no gain
- **No photo handling.** Phase 6
- **Do not assume delivery succeeded.** Detect failure explicitly and emit `dispatch_failed` — Telegram suspension is a real tail risk (RISK-12) and it fails quietly

## Definition of done

1. These tests pass, and were failing before the implementation:
   `test_fr12_never_exceeds_daily_budget`, `test_fr12_silence_when_nothing_due`,
   `test_fr13_ambient_reply_recorded_as_cold`, `test_fr13_ambient_reply_grades_through_examiner`,
   `test_dr5_stopped_dispatcher_visible_in_digest`, `test_sc3_no_probe_past_due_beyond_one_cycle`,
   `test_d13_missed_window_recorded_not_backfilled`, `test_d12_deferral_requires_reason_code`,
   `test_con13_setup_incomplete_without_handshake`
2. `test_nfr5_ambient_round_trip_latency` runs and reports a figure, which is then pinned in the spec
3. `anamnesis dispatcher run` survives sleep/wake on the target machine
4. No change to files outside `dispatcher/`, `tests/contract/`

## Gate

```
pytest tests/contract/phase5/ -v && anamnesis dispatcher run --dry-run --explain
```

Then confirm by hand, over two weeks — this gate is the only one that takes calendar time:

1. **Run it with no client session open for two weeks.** Confirm probes arrive, replies grade, and the budget is never exceeded.
2. **Kill the dispatcher and leave it dead for a day.** Open a session. The digest must say `stopped` with a stale heartbeat. If it says `running`, DR-5 is decorative.
3. **Close your laptop overnight.** Confirm the missed window is recorded as an event and that the next morning does not deliver yesterday's backlog on top of today's.

## Stop

When the definition of done is met, stop and report. Do not begin the next phase.
