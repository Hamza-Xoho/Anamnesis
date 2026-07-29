---
id: SPEC-anamnesis
title: Anamnesis — Design Specification
type: design-spec
version: 0.1.0
derived_from:
  charter: anamnesis-charter.md
  charter_version: 0.2.0
  proposal: anamnesis-proposal.md
  proposal_version: 0.2.0
  governing: proposal
created: 2026-07-27
---

# Anamnesis — Design Specification

> The charter says what and why. This says how. Where the two disagree, the charter wins and this document is wrong.
> **Test for every section: two competent implementers reading it should produce compatible systems.**

## 0. Which spec governs

**The proposal governs the architecture.** Charter v0.2.0 describes a desktop application with an in-repo tutor; proposal v0.2.0 describes an MCP service with teaching left to an external general-purpose model. The proposal is later, evidence-updated, and narrows the contribution claim after a literature survey that found two of the charter's three claimed novelties already occupied.

**Out of scope by this ruling, despite appearing in the charter:**

| Charter item | Status | Why |
|---|---|---|
| FR-1 (tutor teaches in-session, diagnoses material type) | Moved to the teaching layer | Proposal §3: "Teaching itself remains with the general-purpose conversational model and is not reimplemented" |
| FR-20 (brain view) | Cut | Proposal §9 names it a non-completion condition |
| FR-21 (Anki/vault import as seed) | Cut | Proposal §9; Q-6 committed to starting clean |
| Local web UI (charter §9 Interface) | Cut | Replaced by the MCP tool surface, the CLI status command, and the ambient channel |
| CON-2 (context-builder boundary) | Recast as INV-2 | Isolation is now by execution location and module boundary, not by a constructed context object |

**Derived requirements.** The proposal asserts six completeness conditions with no charter requirement behind them. They are numbered `DR-` and carry the same weight as an `FR-`. Their acceptance clauses were authored during buildkit generation and are attributed as such.

| ID | Requirement | Source |
|---|---|---|
| DR-1 | Grading accepts only a probe reference and a verbatim response | Proposal §9 |
| DR-2 | Each of the four §6 prototype failures has a tool precondition that refuses | Proposal §9, §6 |
| DR-3 | Teaching without recorded attempts is visible as missing evidence | Proposal §9 |
| DR-4 | Read-back is one call, payload bounded at realistic graph size | Proposal §9 |
| DR-5 | Dispatcher liveness is reported inside the read-back payload | Proposal §9, §10 |
| DR-6 | Refusals are instrumented so residual bypass is measurable | Proposal §8, §10 |

---

## 1. Decisions

| # | Decision | Made | Attribution | Settled | Rationale |
|---|---|---|---|---|---|
| D-1 | Which spec governs the build | Proposal | human-decided | 2026-07-27 | Later, evidence-updated; the trace states the design spec must not start against the old claim |
| D-2 | Phase ordering basis | Dependency-ordered, not calendar | human-decided | 2026-07-27 | No hard external deadline; the charter's M0 gate is preserved as phase zero |
| D-3 | Who writes to the event log | Dispatcher writes directly, through one shared append module (`core/store.append`) that is the only code permitted to write | human-decided | 2026-07-27 | "Sole writer" is about the teaching layer, not process count; RISK-13 requires the dispatcher to own its lifecycle |
| D-4 | Event ordering key | Monotonic integer `seq`, assigned inside `core/store.append` | derived-from-charter | 2026-07-27 | Single writer module, single user, no merge case (CON-11, non-goals) |
| D-5 | Derived state | Materialised tables, rebuilt by full replay on demand | human-decided | 2026-07-27 | NFR-3 is satisfied by provability, not by refusing to cache; NFR-5 and DR-4 both push against replay-on-read |
| D-6 | Tool surface granularity | Many thin tools plus one fat read-back | human-decided | 2026-07-27 | "Ordering enforced by refusing preconditions" only measures cleanly when a refusal names a tool |
| D-7 | Refusal mechanics | Successful result carrying `refused: true`, reason code, remedy and blocking item — **and** an appended `refused` event | human-decided | 2026-07-27 | Written policy is followed unreliably; a refusal naming its remedy converts policy into a next action. The event gives DR-6 for free |
| D-8 | Read-back digest | Fixed shape, N configurable (default 5), plus one detail tool | human-decided | 2026-07-27 | Makes DR-4's bound structural rather than a measurement that must keep being retaken |
| D-9 | Concept reconciliation | Propose only; merging requires an explicit tool call. Both proposal and decision are events | human-decided | 2026-07-27 | CON-1's spirit is that nothing about knowledge state is asserted without evidence; an automatic merge is an assertion |
| D-10 | FR-22 seam | Route failure emits a top-ranked **candidate** pinned to the failed route marker, not a probe | human-decided | 2026-07-27 | Probe authoring needs a model call and `core/` may make none. Resolves the charter's own §15 open item |
| D-11 | Anki integration (Q-5) | Atoms recorded as events; exported to a file the external `anki` skill consumes. No AnkiConnect | human-decided | 2026-07-27 | Keeps a runtime dependency out of a build whose central operational risk is a background process that must not die |
| D-12 | Snooze semantics | Reason-coded deferral from a fixed set; the deferral is evidence | human-decided | 2026-07-27 | Avoidance becomes queryable rather than invisible (RISK-9) |
| D-13 | Dispatch catch-up | Send only today's within budget; record missed windows as `dispatch_window_missed` events | human-decided | 2026-07-27 | CON-7 makes silence valid, so a backlog flood is the wrong repair; RISK-13 needs missed windows visible, not retroactively filled |
| D-14 | Photo ingestion | Transcribe with a vision model, then grade the transcription through the identical examiner call. Transcription stored verbatim on the attempt event | human-decided | 2026-07-27 | One examiner path, one pinned model; when a grade looks wrong you can see which half failed. Literature says transcription dominates residual error |
| D-15 | Teaching-layer instruction files | In repo under `teaching/`, installed to the Claude config by a script | human-decided | 2026-07-27 | They are the other half of the interface; a tool rename that doesn't update them is a broken build, and in-repo means a test catches it |
| D-16 | State visibility surface | CLI `anamnesis status` over the same digest; Obsidian as the reflective long-form view | human-decided | 2026-07-27 | Read-back-only would reproduce the app-must-be-open failure in a new form |
| D-17 | Storage engine | SQLite, single file, WAL mode | derived-from-charter | 2026-07-27 | Charter §9: single-file embedded database, append-only event table plus derived tables |
| D-18 | Multi-user concretisation | No identity column anywhere | derived-from-charter | 2026-07-27 | CON-11; adding one later is a migration, but adding one now is dead weight for the whole of v1 |
| D-19 | Rating mapping | miss → `Again`, partial → `Hard`, clean hit → `Good`, inferably-effortless hit → `Easy` | derived-from-charter | 2026-07-27 | ADR-11 verbatim |
| D-20 | Event schema versioning | Every event carries `schema_version`, per type | derived-from-charter | 2026-07-27 | NFR-3 over a multi-year log; replay must be able to interpret old events as written |

### Deferred to the implementer

| # | Decision | Bounding constraint |
|---|---|---|
| D-21 | SQLite access library and connection management | `core/store` is the only module holding a write connection. No ORM that can emit an `UPDATE` against `events` |
| D-22 | Inference client library and retry policy | Every call records `model_id`, `model_version`, `prompt_hash` on its event (NFR-7). No client import inside `core/` |
| D-23 | Embedding model and similarity threshold | Output may only produce a `concept_merge_proposed` event. It may never merge |
| D-24 | Test framework, lint and type-check tooling | Contract tests live under `tests/contract/` and are runnable by one command |
| D-25 | Printable sheet renderer | Output is deterministic from the event log; identical events produce a byte-identical sheet |
| D-26 | Evaluation-set file format | Lives in `tests/fixtures/`, git-tracked, never in the event log. Frozen once phase 0 passes; changing it invalidates the gate |
| D-27 | Telegram polling interval and jitter | Must stay inside CON-7's daily budget; send times jittered (RISK-12) |
| D-28 | Digest `N` default and configuration mechanism | Whatever N is, the payload must satisfy DR-4's ceiling at 500 concepts / 2000 probes |
| D-29 | Candidate ranking weights (FR-11) | Ranking must be reproducible from the log with inspectable inputs, and a solid concept resting on an unstudied prerequisite must outrank every other generator |

---

## 2. Module boundaries

Dependency direction is the rule agents most often violate while being locally reasonable. It is hook-enforced.

```
anamnesis/
  core/          store.py · events.py · reducer.py · schema.sql
  memory/        py-fsrs wrapper, per-probe scheduling
  agents/
    examiner/    blind grading
  candidates/    generators + ranking
  server/        MCP stdio server: tools, preconditions, refusals, digest
  dispatcher/    always-on: Telegram, schedule, catch-up, liveness
  export/        obsidian renderer, paper sheets
  cli/           status command
  teaching/      prose instruction files installed into the Claude config
  tests/
    contract/    frozen
    fixtures/    the seeded evaluation set
```

| Module | Responsibility | May depend on | Must never |
|---|---|---|---|
| `core/` | Event log, replay, derived state | stdlib, sqlite3 | Import any model or HTTP client. Import any other project module |
| `core/store.py` | The **only** code that appends events | `core/events` | Emit `UPDATE events` or `DELETE FROM events` |
| `core/reducer.py` | The **only** code that writes derived tables | `core/store` (read), `memory/` | Call a model. Accept a status value from a caller |
| `memory/` | FSRS-6 wrapper, verdict-only rating | `py_fsrs`, `core/` types | Reference `route_quality` in any form. Write to the store |
| `agents/examiner/` | Blind grading against a stored rubric | `core/` types, inference client | Import `server/`, `dispatcher/`, `cli/`. Receive conversation history |
| `candidates/` | Generators and ranking | `core/` | Call a model. Append events directly — must route through `core/store` |
| `server/` | Tool surface, preconditions, refusals, digest | `core/`, `memory/`, `agents/examiner/`, `candidates/` | Write derived tables. Expose any tool that accepts a verdict, rubric, or review date |
| `dispatcher/` | Scheduled delivery, reply grading, liveness | `core/`, `memory/`, `agents/examiner/` | Import `server/` |
| `export/` | Obsidian render, paper sheets | `core/` (read only) | Read from the vault. Be imported by anything except `cli/` |
| `cli/` | Status command | `core/`, `memory/`, `export/` | Write anything |

---

## 3. Data shapes

### 3.1 Event envelope — table `events`

Append-only. No `UPDATE`, no `DELETE`, ever.

| Field | Type | Required | Immutable | Notes |
|---|---|---|---|---|
| `seq` | INTEGER PK AUTOINCREMENT | yes | yes | Monotonic. Assigned inside `core/store.append` and nowhere else |
| `event_id` | TEXT | yes | yes | UUIDv4. Idempotency key — a second append with the same id is a no-op |
| `ts` | TEXT | yes | yes | ISO 8601 UTC, e.g. `2026-07-27T14:03:11Z` |
| `type` | TEXT | yes | yes | Discriminator, see 3.2 |
| `schema_version` | INTEGER | yes | yes | Per type. Replay must interpret old events as written |
| `actor` | TEXT | yes | yes | `teaching` · `examiner` · `dispatcher` · `cli` · `system` |
| `payload` | TEXT (JSON) | yes | yes | Type-specific, see 3.2 |

Worked example:

```json
{ "seq": 4822, "event_id": "9f2c…", "ts": "2026-07-27T14:03:11Z",
  "type": "graded", "schema_version": 1, "actor": "examiner",
  "payload": { "attempt_id": "att_7c1", "probe_id": "prb_44a",
               "verdict": "partial", "route_quality": "route_failure",
               "expressed_confidence": 0.81, "model_id": "claude-sonnet-4-6",
               "model_version": "2026-05-14", "prompt_hash": "sha256:1a2b…",
               "rubric_hash": "sha256:ff10…" } }
```

### 3.2 Event types

| Type | Payload | Emitted by |
|---|---|---|
| `topic_opened` | `topic_id, title, source_ref?` | teaching |
| `concept_asserted` | `concept_id, title, subject, prereq_ids[], related_ids[]` | teaching |
| `concept_merge_proposed` | `a, b, similarity` | system |
| `concept_merged` | `from, into, decided_by` | teaching |
| `probe_authored` | `probe_id, concept_id, prompt, probe_class, rubric{claims[], route_markers[]}, rubric_hash` | teaching |
| `attempt_recorded` | `attempt_id, probe_id, response_text, response_image_ref?, transcription?, channel, answer_was_onscreen, predicted_confidence?` | teaching · dispatcher |
| `graded` | `attempt_id, probe_id, verdict, route_quality, expressed_confidence, model_id, model_version, prompt_hash, rubric_hash` | examiner |
| `candidate_generated` | `candidate_id, target_concept_id, generator, evidence, route_marker?` | system |
| `candidate_selected` / `candidate_dismissed` | `candidate_id, reason?` | teaching |
| `topic_closed` | `topic_id, concept_ids[]` | teaching |
| `due_dispatched` | `probe_id, channel, message_ref` | dispatcher |
| `dispatch_failed` | `probe_id, reason` | dispatcher |
| `dispatch_window_missed` | `window_start, window_end, due_count` | dispatcher |
| `deferred` | `probe_id, reason_code` | teaching · dispatcher |
| `refused` | `tool, reason_code, blocking, caller_args_hash` | server |
| `dispatcher_heartbeat` | `pid` | dispatcher |
| `atom_recorded` | `atom_id, front, back, concept_id?` | teaching |
| `source_parsed` | `source_id, tree` | teaching |
| `export_rendered` | `target, content_hash` | cli |

**Enums.** `verdict` ∈ `miss` · `partial` · `hit` · `effortless_hit`. `route_quality` ∈ `clean` · `route_failure` · `unassessable`. `probe_class` ∈ `micro` · `session` · `desk`. `channel` ∈ `session` · `ambient` · `paper`. `reason_code` for `deferred` ∈ `not_now` · `question_unclear` · `answered_elsewhere`.

### 3.3 Derived tables

Written **only** by `core/reducer.py`. Dropped and rebuilt by full replay on demand.

| Table | Key | Fields |
|---|---|---|
| `probe_state` | `probe_id` | `concept_id, stability, difficulty, review_due, last_verdict, reps, lapses, fsrs_params_version` |
| `concept_rollup` | `concept_id` | `per_class_state (JSON), n_probes, evidenced` |
| `error_trail` | `attempt_id` | `concept_id, route_marker_missed, ts` |
| `calibration` | `(subject, window)` | `predicted_mean, outcome_rate, n` |
| `candidate_rank` | `candidate_id` | `score, generator, evidence, rank, route_marker` |
| `topic_evidence` | `topic_id` | `n_attempts, evidenced, opened_at, closed_at` |
| `dispatcher_liveness` | singleton | `last_heartbeat, last_dispatch, status` |
| `reducer_position` | singleton | `last_seq_applied` |

**Concept carries no status column by construction** (CON-1, ADR-1). `concept_rollup.per_class_state` is a view over probe states, never an independent value.

### 3.4 Rubric

Frozen at authoring (CON-4, ADR-4). Immutable. A rubric may be superseded by a new probe, never edited.

```json
{ "claims": ["Hydrogen bonding arises from the O–H dipole",
             "Each water molecule can form up to four H-bonds"],
  "route_markers": ["Attributes cohesion to H-bonding, not to polarity alone"] }
```

`rubric_hash` = `sha256` of the canonical JSON (sorted keys, no whitespace). Recorded on `probe_authored` and again on every `graded` event, so a grade can be proven to have been made against the rubric as authored.

**A rubric with zero `route_markers` is rejected at authoring** (FR-3).

---

## 4. Interfaces

### 4.1 MCP tool surface

Transport: stdio. All tools return a JSON object. A refusal is a **successful** result (see §6), never a protocol error.

| Tool | Arguments | Returns | May not be passed |
|---|---|---|---|
| `get_state` | `n?` | Digest, §4.2 | — |
| `get_concept` | `concept_id` | Concept detail with probe states and linked attempts | — |
| `open_topic` | `title, source_ref?` | `topic_id` | — |
| `assert_concept` | `title, subject, prereq_ids?, related_ids?` | `concept_id` | Any confidence, status or rating field |
| `author_probe` | `concept_id, prompt, probe_class, claims[], route_markers[]` | `probe_id, rubric_hash` | `review_due`, any memory-state field |
| `record_attempt` | `probe_id, response_text, answer_was_onscreen, predicted_confidence?` | `attempt_id` | `verdict`, `route_quality`, `expressed_confidence` |
| `grade_attempt` | `attempt_id` — **and nothing else** | `verdict, route_quality, expressed_confidence, next_review_due` | `rubric`, `verdict`, `route_quality`, `expressed_confidence`, `model` |
| `close_topic` | `topic_id` | `concept_ids[], probes_authored` | — |
| `defer_due` | `probe_id, reason_code` | `deferred_until` | Arbitrary reason text — the code must be from the fixed set |
| `select_candidate` | `candidate_id` | `probe_authoring_brief` | — |
| `dismiss_candidate` | `candidate_id, reason` | `ok` | — |
| `record_atom` | `front, back, concept_id?` | `atom_id` | — |
| `propose_merge` | `a, b` | `similarity, proposal_id` | — |
| `confirm_merge` | `from, into` | `ok` | — |

**`grade_attempt` is the load-bearing signature.** It takes one argument. The service retrieves the rubric by `probe_id` from the attempt, calls its own pinned model with exactly the five inputs FR-4 names — concept, prompt, verbatim response, rubric, `answer_was_onscreen` — and returns the three outputs. There is no parameter by which a caller can influence the verdict. Passing any additional key is a refusal, not an ignore (DR-1).

### 4.2 The read-back digest

Fixed shape. Size is O(N), not O(graph). **Ceiling: 8 KB serialised at 500 concepts / 2000 probes** (DR-4).

```json
{ "log_position": 4822,
  "due": { "count": 3,
           "next": [ { "probe_id": "…", "concept": "…", "review_due": "…", "overdue_cycles": 0 } ] },
  "candidates": [ { "candidate_id": "…", "concept": "…", "generator": "route_failure",
                    "evidence": "…", "rank": 1 } ],
  "unevidenced_topics": [ { "topic_id": "…", "title": "…", "opened_at": "…" } ],
  "calibration": { "window_days": 30,
                   "subjects": [ { "subject": "…", "predicted_mean": 0.72, "outcome_rate": 0.55, "n": 41 } ] },
  "dispatcher": { "status": "running", "last_heartbeat": "…", "last_dispatch": "…" },
  "counts": { "concepts": 312, "probes": 1104, "attempts": 2890 } }
```

Each list is capped at `n` (default 5). `unevidenced_topics` satisfies DR-3; `dispatcher` satisfies DR-5.

### 4.3 CLI

```
anamnesis status              # the same digest, human-formatted
anamnesis status --json       # the digest verbatim
anamnesis replay --verify     # drop derived tables, replay, diff — exit 1 on mismatch
anamnesis export obsidian
anamnesis export sheet <topic_id>
anamnesis dispatcher run      # the always-on process
```

---

## 5. State transitions

### 5.1 Probe

| State | Enter when | Legal next | Illegal |
|---|---|---|---|
| `authored` | `probe_authored` | `seeded` | Going straight to `retained` |
| `seeded` | First in-session attempt graded, `answer_was_onscreen = true` | `retained`, `lapsed` | Establishing retention (CON-9, ADR-6) |
| `retained` | An attempt graded with `answer_was_onscreen = false` and verdict ≥ `hit` | `due`, `lapsed` | — |
| `due` | `now ≥ review_due` | `dispatched`, `deferred` | Being dismissed by not selecting it (CON-8, FR-9) |
| `dispatched` | `due_dispatched` | `retained`, `lapsed`, `deferred` | — |
| `deferred` | `deferred` with a reason code | `due` | Deferral without a reason code (D-12) |
| `lapsed` | Verdict `miss` | `retained` | — |
| `superseded` | A new probe supersedes it | terminal | Editing its rubric (CON-4) |

**An in-session pass may seed but never establish retention.** The `seeded → retained` edge requires `answer_was_onscreen = false`.

### 5.2 Topic

`opened → (concepts asserted, probes authored, attempts recorded) → closed`.

`close_topic` refuses if `topic_evidence.n_attempts = 0` (`TOPIC_UNEVIDENCED`) or if a due item is outstanding beyond one dispatch cycle without a recorded deferral (`DUE_ITEM_OUTSTANDING`).

### 5.3 Route failure — FR-22, D-10

A `graded` event with `route_quality = route_failure`:

1. produces a **verdict-only** rating on the original probe (`miss`/`partial`/`hit` → FSRS as per D-19). Route quality does not enter the mapping (CON-12).
2. emits `candidate_generated` with `generator = "route_failure"`, `route_marker` set to the marker that was missed, and `rank` forced to the top.

A route-failure candidate **cannot be dismissed without a recorded reason**. It materialises into a probe only when `select_candidate` is called and the teaching layer authors one.

---

## 6. Error and refusal semantics

This section is load-bearing. Refusal is the mechanism the project claims.

**A refusal is a successful tool result**, not a protocol error:

```json
{ "refused": true,
  "reason_code": "VERDICT_NOT_ACCEPTED_FROM_CALLER",
  "message": "grade_attempt accepts only attempt_id. It received: verdict, rubric.",
  "remedy": "Call grade_attempt(attempt_id) with no other arguments. The service retrieves the rubric and grades with its own pinned model.",
  "blocking": { "rejected_keys": ["verdict", "rubric"] } }
```

Every refusal appends a `refused` event carrying `tool`, `reason_code`, `blocking`, `caller_args_hash`. That is what makes DR-6 measurable without a separate instrumentation pass.

### 6.1 Reason codes — the four documented failures (DR-2)

| Failure (proposal §6) | Reason code | Refusing tool | Precondition |
|---|---|---|---|
| Due item deferred five sessions running | `DUE_ITEM_OUTSTANDING` | `open_topic`, `close_topic` | A probe past `review_due` by more than one dispatch cycle with no `deferred` event |
| Retention claimed from an on-screen attempt | `MISSING_ATTEMPT_CONDITION` | `record_attempt` | `answer_was_onscreen` absent |
| Wrong answer committed as correct after pushback | `VERDICT_NOT_ACCEPTED_FROM_CALLER` · `ATTEMPT_ALREADY_GRADED` | `grade_attempt` | Any grading field passed; or the attempt already has a `graded` event |
| Two reads disagreed about the same review date | `SCHEDULE_IS_DERIVED` | `author_probe`, any tool | `review_due` or any memory-state field passed |

Plus: `TOPIC_UNEVIDENCED` (`close_topic`, DR-3), `RUBRIC_HAS_NO_ROUTE_MARKERS` (`author_probe`, FR-3), `DEFERRAL_REASON_REQUIRED` (`defer_due`, D-12), `MERGE_NOT_PROPOSED` (`confirm_merge`, D-9).

### 6.2 Non-refusal errors

Inference endpoint unavailable → `attempt_recorded` still appends; grading queues for retry (INT-1). Attempts are never dropped. Telegram delivery failure → `dispatch_failed` event; no data loss (RISK-12).

---

## 7. Configuration and pinning

| Item | Fixed / configurable | Where | Recorded on output |
|---|---|---|---|
| Examiner model id + version | **Pinned**, changed only deliberately | `config.toml` | Yes — every `graded` event (NFR-7) |
| Examiner prompt | Pinned; hash recorded | `agents/examiner/prompts/` | `prompt_hash` on every `graded` event |
| `py-fsrs` | **Pinned to 6.3.1**, vendored | `pyproject.toml` | `fsrs_params_version` on `probe_state` |
| FSRS parameters | Default (pretrained) until Q-8 measurement | `config.toml` | `fsrs_params_version` |
| Daily ambient budget | Configurable | `config.toml` | — |
| Digest `n` | Configurable, default 5 | `config.toml` | — |
| Telegram bot token, API keys | **Secrets** | Local `.env`, never committed (O4) | Never logged |
| Obsidian vault path | Configurable | `config.toml` | — |

Changing the examiner model or prompt requires re-baselining against the phase 0 evaluation set (RISK-6).

---

## 8. Observability

- **`anamnesis status`** — the digest, human-formatted. The primary way a human sees system state without opening a teaching session (D-16).
- **`anamnesis replay --verify`** — drops derived tables, replays, diffs. Exit 1 on mismatch. This is NFR-3 made runnable, and it is a phase gate.
- **Every status traces to attempts in one query** (NFR-2): `get_concept` returns each rollup value alongside the attempt ids that produced it.
- **Dispatcher liveness** surfaces in the digest, so a stopped dispatcher is visible at the next read-back (DR-5) rather than discovered weeks later.
- **Refusals are events**, so bypass rate is a query over the log, not an instrumentation project (DR-6).
- **No telemetry, no analytics, no third-party logging** (NFR-1). Only probe text, learner response and rubric leave the machine.

---

## 9. Open items

| Item | Forced by |
|---|---|
| The evaluation set's actual content — matched confidently-wrong / hedged-correct pairs, and right-answer-wrong-mechanism responses | Phase 0. Cannot be generated; must be authored from real material |
| DR-4's payload ceiling — 8 KB is asserted, not measured | Phase 3 gate measures it; revise the spec if the real figure differs |
| FSRS parameter fitting vs. defaults (Q-8) | Not a build phase. 2–3 months of `(probe, verdict, delta_t)` after phase 2, then compare log-loss against defaults |
| Cohen's κ sample size for the phase 0 gate | Phase 0. Substantial band per Landis & Koch |
| Whether ambient yield ≥20% or ≥50% is the target (SC-5 vs proposal §8) | Phase 7. The proposal's ≥20% is evidence-grounded; the charter's ≥50% is not |
