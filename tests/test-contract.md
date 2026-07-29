---
id: TESTS-anamnesis
title: Anamnesis — Test Contract
type: test-contract
version: 0.1.0
derived_from: anamnesis-charter.md v0.2.0 (acceptance clauses) + anamnesis-proposal.md v0.2.0 (DR- clauses)
created: 2026-07-27
---

# Anamnesis — Test Contract

Every acceptance clause as a named test. Tests are named after the requirement ID, so traceability needs no separate document and survives refactors.

**Three rules that make this worth having:**

1. **Write the tests for a phase before the implementation, and confirm they fail first.** A test written after the code tests the code. A test written from the acceptance clause tests the requirement.
2. **Rejected is not ignored.** Where a clause says an input must be refused, assert the refusal — never merely that the input had no effect. Silently ignoring is a different and worse behaviour that passes a sloppy test.
3. **Contract tests are frozen.** Files under `tests/contract/` cannot be modified or deleted once created. A failing contract test means the implementation is wrong. If the requirement genuinely changed, stop and regenerate the kit from an updated charter.

**Tiers.** *Invariant* — must hold for the life of the project; also hook-enforced, because a test can be skipped or quietly deleted. *Behavioural* — one per functional requirement. *Characterisation* — only definable once built; named and deferred deliberately, never omitted silently.

---

## Phase 0 — The gate

If these do not pass, the architecture changes and no further phase runs.

| Req | Test name | Asserts (EARS) | Tier | Phase |
|---|---|---|---|---|
| FR-3 | `test_fr3_rubric_carries_claims_and_route_markers` | WHEN a rubric is constructed THE SYSTEM SHALL require both a non-empty `claims` list and a non-empty `route_markers` list | behavioural | 0 |
| FR-3 | `test_fr3_rejects_rubric_with_no_route_markers` | WHEN a rubric with an empty `route_markers` list is submitted THE SYSTEM SHALL reject it with an error, not accept it silently | behavioural | 0 |
| FR-4 | `test_fr4_examiner_input_is_exactly_five_fields` | THE SYSTEM SHALL ALWAYS construct the examiner call from exactly concept, prompt, verbatim response, rubric, and `answer_was_onscreen` — and nothing else | invariant | 0 |
| FR-4 | `test_fr4_verdict_invariant_to_surrounding_conversation` | WHEN the same five inputs are graded twice with different surrounding text present in the process THE SYSTEM SHALL return the same verdict | invariant | 0 |
| FR-5 | `test_fr5_three_distinct_outputs` | WHEN an attempt is graded THE SYSTEM SHALL return verdict, route quality and expressed confidence as three distinct fields | behavioural | 0 |
| FR-5 | `test_fr5_expressed_confidence_has_no_path_to_verdict` | THE SYSTEM SHALL ALWAYS produce an identical verdict for two responses differing only in hedging register | invariant | 0 |
| SC-1 | `test_sc1_grading_separation_on_seeded_set` | WHEN the frozen evaluation set is graded THE SYSTEM SHALL rank the confidently-wrong answer below the hedged-correct one in ≥90% of matched pairs | behavioural | 0 |
| SC-4 | `test_sc4_route_detection_on_seeded_set` | WHEN the frozen right-answer-wrong-mechanism set is graded THE SYSTEM SHALL record ≥80% as route failures rather than clean passes | behavioural | 0 |
| NFR-7 | `test_nfr7_grade_records_model_identity` | WHEN a grade is produced THE SYSTEM SHALL record `model_id`, `model_version` and `prompt_hash` on the result | invariant | 0 |
| — | `test_gate_kappa_against_human_labels` | WHEN grading is compared to the held-out human-labelled sample THE SYSTEM SHALL report Cohen's κ per criterion | characterisation | 0 |

---

## Phase 1 — The log

| Req | Test name | Asserts (EARS) | Tier | Phase |
|---|---|---|---|---|
| FR-6 | `test_fr6_replay_reproduces_derived_state` | WHEN derived tables are dropped and the log replayed THE SYSTEM SHALL reproduce them exactly | invariant | 1 |
| NFR-3 | `test_nfr3_replay_is_byte_identical` | THE SYSTEM SHALL ALWAYS produce byte-identical derived state from identical event logs | invariant | 1 |
| NFR-4 | `test_nfr4_log_survives_crash_mid_write` | WHEN the process is killed mid-append THE SYSTEM SHALL leave the log readable and every completed event intact | invariant | 1 |
| CON-1 | `test_con1_no_write_path_to_derived_state` | THE SYSTEM SHALL ALWAYS expose no function outside `core/reducer` that writes a derived table | invariant | 1 |
| SC-2 | `test_sc2_status_is_pure_function_of_log` | THE SYSTEM SHALL ALWAYS compute status solely from the event log — property test over generated event sequences | invariant | 1 |
| — | `test_events_are_append_only` | WHEN an `UPDATE` or `DELETE` against `events` is attempted THE SYSTEM SHALL raise, not silently succeed | invariant | 1 |
| D-4 | `test_seq_is_monotonic_and_gapless` | THE SYSTEM SHALL ALWAYS assign `seq` monotonically with no gaps under concurrent append from two processes | invariant | 1 |
| D-20 | `test_replay_honours_old_schema_versions` | WHEN an event carrying an older `schema_version` is replayed THE SYSTEM SHALL interpret it as written | behavioural | 1 |

---

## Phase 2 — Memory and the two lanes

| Req | Test name | Asserts (EARS) | Tier | Phase |
|---|---|---|---|---|
| FR-7 | `test_fr7_probe_carries_retrievability_and_due_date` | WHEN a probe is graded THE SYSTEM SHALL advance its next-due date and update its retrievability estimate | behavioural | 2 |
| FR-8 | `test_fr8_concept_rolls_up_per_probe_class` | WHEN a concept is read THE SYSTEM SHALL return per-probe-class state, never a single scalar | behavioural | 2 |
| FR-8 | `test_fr8_concept_has_no_status_column` | THE SYSTEM SHALL ALWAYS store no status or confidence field on a concept row | invariant | 2 |
| FR-9 | `test_fr9_due_item_cannot_be_dismissed_by_omission` | WHEN a due item is not selected THE SYSTEM SHALL keep it due — only an explicit deferral with a reason removes it from the lane | invariant | 2 |
| FR-9 | `test_fr9_candidate_cannot_be_auto_dispatched` | THE SYSTEM SHALL ALWAYS refuse to dispatch an item from the candidate lane | invariant | 2 |
| FR-22 | `test_fr22_route_failure_emits_candidate` | WHEN a grade carries `route_quality = route_failure` THE SYSTEM SHALL emit a top-ranked candidate bound to the same concept and the missed route marker | behavioural | 2 |
| FR-22 | `test_fr22_route_failure_rates_verdict_only` | WHEN a grade carries `route_quality = route_failure` THE SYSTEM SHALL rate the original probe from the verdict alone | invariant | 2 |
| CON-12 | `test_con12_no_rating_path_from_route_quality` | THE SYSTEM SHALL ALWAYS contain no reference to `route_quality` anywhere in `memory/` | invariant | 2 |
| CON-9 | `test_con9_onscreen_attempt_cannot_establish_retention` | WHEN an attempt with `answer_was_onscreen = true` passes THE SYSTEM SHALL seed the memory model and SHALL NOT move the probe to `retained` | invariant | 2 |
| D-19 | `test_d19_verdict_to_rating_mapping` | WHEN a verdict is mapped THE SYSTEM SHALL produce Again/Hard/Good/Easy for miss/partial/hit/effortless_hit respectively | behavioural | 2 |

---

## Phase 3 — The tool surface

| Req | Test name | Asserts (EARS) | Tier | Phase |
|---|---|---|---|---|
| DR-1 | `test_dr1_grade_attempt_takes_only_attempt_id` | WHEN `grade_attempt` receives any key other than `attempt_id` THE SYSTEM SHALL refuse with `VERDICT_NOT_ACCEPTED_FROM_CALLER` | invariant | 3 |
| DR-1 | `test_dr1_no_code_path_from_caller_verdict_to_grade_event` | THE SYSTEM SHALL ALWAYS contain no path by which a caller-supplied verdict reaches a `graded` event | invariant | 3 |
| DR-2 | `test_dr2_refuses_open_topic_with_due_item_outstanding` | WHEN a probe is overdue beyond one dispatch cycle with no recorded deferral THE SYSTEM SHALL refuse `open_topic` with `DUE_ITEM_OUTSTANDING` | behavioural | 3 |
| DR-2 | `test_dr2_refuses_attempt_without_onscreen_condition` | WHEN `record_attempt` omits `answer_was_onscreen` THE SYSTEM SHALL refuse with `MISSING_ATTEMPT_CONDITION` | behavioural | 3 |
| DR-2 | `test_dr2_refuses_regrade_of_graded_attempt` | WHEN `grade_attempt` targets an already-graded attempt THE SYSTEM SHALL refuse with `ATTEMPT_ALREADY_GRADED` | behavioural | 3 |
| DR-2 | `test_dr2_refuses_caller_supplied_review_date` | WHEN any tool receives `review_due` or a memory-state field THE SYSTEM SHALL refuse with `SCHEDULE_IS_DERIVED` | behavioural | 3 |
| DR-3 | `test_dr3_unevidenced_topic_appears_in_digest` | WHEN a topic is opened and no attempt is recorded THE SYSTEM SHALL list it under `unevidenced_topics` in the next digest | behavioural | 3 |
| DR-3 | `test_dr3_refuses_close_of_unevidenced_topic` | WHEN `close_topic` targets a topic with zero attempts THE SYSTEM SHALL refuse with `TOPIC_UNEVIDENCED` | behavioural | 3 |
| DR-4 | `test_dr4_digest_is_one_call` | WHEN state is read back THE SYSTEM SHALL return the complete digest from a single `get_state` call | behavioural | 3 |
| DR-4 | `test_dr4_digest_bounded_at_scale` | WHEN the graph holds 500 concepts and 2000 probes THE SYSTEM SHALL return a digest under 8 KB serialised | invariant | 3 |
| FR-2 | `test_fr2_close_authors_probe_per_taught_concept` | WHEN a topic is closed THE SYSTEM SHALL require at least one probe per concept taught in it | behavioural | 3 |
| SC-6 | `test_sc6_no_rubric_for_untaught_concept` | THE SYSTEM SHALL ALWAYS hold zero rubrics for concepts never taught and never selected from the candidate queue | invariant | 3 |
| CON-4 | `test_con4_rubric_is_immutable` | WHEN a rubric edit is attempted THE SYSTEM SHALL refuse — supersession by a new probe is the only path | invariant | 3 |
| CON-3 | `test_con3_examiner_has_no_conversation_import` | THE SYSTEM SHALL ALWAYS contain no import of `server/`, `dispatcher/` or `cli/` inside `agents/examiner/` | invariant | 3 |
| D-7 | `test_d7_refusal_is_success_result_and_event` | WHEN a tool refuses THE SYSTEM SHALL return a successful result carrying `refused`, `reason_code`, `message`, `remedy` and `blocking`, and SHALL append a `refused` event | invariant | 3 |
| D-9 | `test_d9_merge_requires_prior_proposal` | WHEN `confirm_merge` is called with no matching `concept_merge_proposed` event THE SYSTEM SHALL refuse with `MERGE_NOT_PROPOSED` | behavioural | 3 |

---

## Phase 4 — Candidates, export, instrumentation

| Req | Test name | Asserts (EARS) | Tier | Phase |
|---|---|---|---|---|
| FR-10 | `test_fr10_candidate_names_generator_and_evidence` | WHEN a candidate is generated THE SYSTEM SHALL record its generator and the evidence that produced it | behavioural | 4 |
| FR-10 | `test_fr10_all_six_generators_produce_candidates` | WHEN the log contains the triggering condition THE SYSTEM SHALL produce candidates from each of unstudied prerequisites, route failures, untested angles, untested cross-links, calibration gaps and avoided items | behavioural | 4 |
| FR-11 | `test_fr11_ranking_is_reproducible_from_log` | WHEN ranking runs twice on identical logs THE SYSTEM SHALL produce identical ranks | invariant | 4 |
| FR-11 | `test_fr11_prereq_gap_outranks_others` | WHEN a solid concept rests on an unstudied prerequisite THE SYSTEM SHALL rank that candidate above others | behavioural | 4 |
| FR-15 | `test_fr15_export_is_deterministic` | WHEN an export is regenerated from identical events THE SYSTEM SHALL produce byte-identical output | invariant | 4 |
| CON-5 | `test_con5_vault_is_never_read` | THE SYSTEM SHALL ALWAYS contain no read of the export target outside tests | invariant | 4 |
| FR-18 | `test_fr18_source_parsed_for_structure_only` | WHEN a source is parsed THE SYSTEM SHALL store the topic tree with weights and dependencies and SHALL NOT store retrievable body content | invariant | 4 |
| DR-6 | `test_dr6_every_refusal_is_an_event` | THE SYSTEM SHALL ALWAYS append a `refused` event for every refusal returned | invariant | 4 |
| DR-6 | `test_dr6_bypass_rate_computable_from_log` | WHEN the bypass query runs THE SYSTEM SHALL compute the rate from the event log alone, with no separate instrumentation store | behavioural | 4 |
| NFR-2 | `test_nfr2_status_traces_to_attempts_in_one_query` | WHEN a concept is read THE SYSTEM SHALL return each rollup value alongside the attempt ids that produced it, in one query | invariant | 4 |

---

## Phase 5 — The dispatcher

| Req | Test name | Asserts (EARS) | Tier | Phase |
|---|---|---|---|---|
| FR-12 | `test_fr12_never_exceeds_daily_budget` | THE SYSTEM SHALL ALWAYS send no more ambient messages in a day than the configured budget | invariant | 5 |
| FR-12 | `test_fr12_silence_when_nothing_due` | WHEN no probe is due THE SYSTEM SHALL send nothing | invariant | 5 |
| FR-13 | `test_fr13_ambient_reply_recorded_as_cold` | WHEN a reply arrives from the ambient channel THE SYSTEM SHALL record it with `answer_was_onscreen = false` | invariant | 5 |
| FR-13 | `test_fr13_ambient_reply_grades_through_examiner` | WHEN a reply arrives THE SYSTEM SHALL grade it through the same examiner path as a session attempt | behavioural | 5 |
| DR-5 | `test_dr5_stopped_dispatcher_visible_in_digest` | WHEN the dispatcher stops THE SYSTEM SHALL report `status: stopped` with `last_heartbeat` in the next digest | invariant | 5 |
| SC-3 | `test_sc3_no_probe_past_due_beyond_one_cycle` | THE SYSTEM SHALL ALWAYS leave no probe past `review_due` beyond one dispatch cycle without either dispatch or a recorded deferral | invariant | 5 |
| D-13 | `test_d13_missed_window_recorded_not_backfilled` | WHEN dispatch windows are missed THE SYSTEM SHALL record `dispatch_window_missed` per window and SHALL send only today's items within budget | behavioural | 5 |
| D-12 | `test_d12_deferral_requires_reason_code` | WHEN `defer_due` receives no reason code from the fixed set THE SYSTEM SHALL refuse with `DEFERRAL_REASON_REQUIRED` | behavioural | 5 |
| CON-13 | `test_con13_setup_incomplete_without_handshake` | WHEN no learner-initiated handshake is recorded THE SYSTEM SHALL refuse to dispatch and SHALL report setup as incomplete | behavioural | 5 |
| NFR-5 | `test_nfr5_ambient_round_trip_latency` | WHEN a reply arrives THE SYSTEM SHALL return a graded response within the stated latency budget | characterisation | 5 |

---

## Phase 6 — Paper, photo, calibration

| Req | Test name | Asserts (EARS) | Tier | Phase |
|---|---|---|---|---|
| FR-16 | `test_fr16_sheet_generated_on_close` | WHEN a topic closes THE SYSTEM SHALL write a printable retrieval sheet to the configured folder, containing no answers | behavioural | 6 |
| FR-17 | `test_fr17_photo_produces_same_three_outputs` | WHEN a photographed answer is ingested THE SYSTEM SHALL produce verdict, route quality and expressed confidence exactly as a typed attempt does | behavioural | 6 |
| D-14 | `test_d14_transcription_stored_verbatim` | WHEN a photo is ingested THE SYSTEM SHALL store the transcription verbatim on the attempt event before grading | invariant | 6 |
| D-14 | `test_d14_examiner_receives_text_not_image` | THE SYSTEM SHALL ALWAYS pass text to the examiner, never an image | invariant | 6 |
| FR-14 | `test_fr14_calibration_queryable_per_subject_and_window` | WHEN calibration is requested THE SYSTEM SHALL return predicted-versus-outcome per subject and per time window | behavioural | 6 |
| FR-19 | `test_fr19_hedging_does_not_depress_relative_score` | WHEN a learner's habitual hedging register is applied THE SYSTEM SHALL not depress expressed-confidence reads relative to that learner's own baseline | characterisation | 6 |

---

## Phase 7 — Trial and evaluation

Measured against the real log, not fixtures. These are the KPIs, and they cannot pass before the trial exists.

| Req | Test name | Asserts (EARS) | Tier | Phase |
|---|---|---|---|---|
| SC-5 | `test_sc5_ambient_yield` | WHEN the trial log is queried THE SYSTEM SHALL show the stated proportion of graded attempts arriving via the ambient channel | characterisation | 7 |
| SC-7 | `test_sc7_every_phase_usable_for_study` | Milestone review, not automated — a phase that does not improve actual learning is halted | characterisation | 7 |
| NFR-1 | `test_nfr1_no_egress_beyond_inference` | THE SYSTEM SHALL ALWAYS send nothing beyond probe text, learner response and rubric to any network endpoint | invariant | 7 |
| NFR-6 | `test_nfr6_per_attempt_cost_bounded` | WHEN the trial log is queried THE SYSTEM SHALL show per-attempt grading cost within the stated ceiling | characterisation | 7 |
| — | `test_all_must_requirements_have_passing_tests` | THE SYSTEM SHALL ALWAYS have a passing test for every `must` requirement | invariant | 7 |

---

## Coverage check

**Every live `must` requirement appears in exactly one phase.**

| Phase | `must` requirements |
|---|---|
| 0 | FR-3, FR-4, FR-5 |
| 1 | FR-6 |
| 2 | FR-7, FR-9, FR-22 |
| 3 | FR-2, DR-1, DR-2, DR-3, DR-4 |
| 4 | FR-10, FR-11, DR-6 |
| 5 | FR-12, FR-13, DR-5 |

`should` requirements: FR-8 (2), FR-15 · FR-18 (4), FR-14 · FR-16 · FR-17 · FR-19 (6). Cut: FR-1, FR-20, FR-21.

**Characterisation tests, deliberately deferred:** `test_gate_kappa_against_human_labels`, `test_nfr5_ambient_round_trip_latency`, `test_fr19_hedging_does_not_depress_relative_score`, `test_sc5_ambient_yield`, `test_sc7_every_phase_usable_for_study`, `test_nfr6_per_attempt_cost_bounded`. Each names what will be pinned once the value is known.
