---
id: PROP-anamnesis
title: Anamnesis
type: proposal
status: draft
version: 0.2.0
institution: ‹university / faculty›
programme: ‹e.g. BSCS›
term: ‹Term of Registration›
advisor: ‹advisor name›
project_type: software development · artificial intelligence · research based
created: 2026-07-27
updated: 2026-07-27
derived_from:
  charter: anamnesis-charter.md
  charter_version: 0.2.0
related:
  trace: ./anamnesis-proposal-trace.md
  literature_prompt: ./anamnesis-literature-research-prompt.md
---

# ‹PROGRAMME› FINAL YEAR PROJECT PROPOSAL

## ANAMNESIS — A LEARNER-MODELLING SERVICE FOR CONVERSATIONAL TUTORING

**Term of Registration:** ‹term›

### Particulars of the students

| Sr. # | Registration # | Name in Full (BLOCK LETTERS) | Contact # | CGPA |
|---|---|---|---|---|
| 1 | ‹reg› | HAMZA ‹SURNAME› | ‹contact› | ‹cgpa› |

*This is a single-student project. See §13 for the workstream breakdown.*

### Project Type

☑ Research based  ☐ Hardware based / Embedded  ☐ Game based
☑ Software Development  ☑ Artificial Intelligence (AI)  ☐ Mobile Application
☐ Web Application  ☐ Robotics  ☐ Database
☐ Other: —

**Faculty:** ‹faculty› · **Institution:** ‹institution›
**Project Advisor:** ‹advisor name›

‹INSTITUTIONAL BOILERPLATE — acceptance of project idea · supervisory meeting requirements · advisor's consent · signature tables. Paste verbatim from the department proforma.›

---

## 1. Abstract

Learners studying technical material independently must decide continually what to revise, and that decision rests on an estimate of what they already know. The estimate is unreliable in a measured way: repeated re-reading raises confidence without improving delayed retention, while retrieval practice, which does improve it, is used less. Existing software does not correct this, because each class of tool models the material rather than the learner. Spaced-repetition systems schedule atomic items precisely but represent no mechanism; note applications record what was written rather than what can be reproduced; document-grounded assistants model a corpus and retain no memory of how a learner fails. Recent conversational tutoring systems maintain persistent learner state and deliver practice between sessions, but assessment within them is produced by the same context that delivered the teaching, and language models are known to revise correct judgements when a user objects.

This project develops Anamnesis, a local service holding a learner's knowledge state behind a tool boundary, so that a teaching conversation can read that state but cannot write it. Its unit is the probe: a retrieval prompt bound to a concept, carrying a rubric fixed at authoring time. All state is recomputed deterministically from an append-only event log, so no caller can assert a competence it has not evidenced. Grading executes inside the service against the stored rubric, with a pinned model and no conversational history, and returns three separate signals: whether the answer was correct, whether it arrived by the intended mechanism, and how confident the learner sounded. A background process delivers due probes when no session is open.

The project delivers a working service and an empirical account of whether isolated assessment and mechanical enforcement are reliable enough that a learner can act on the record without re-deriving it first.

---

## 2. Introduction of the Project

Independent study of technical subjects is now common, and the tools supporting it have improved unevenly. Scheduling and note-keeping are solved; establishing whether the learner has understood anything is not. The learner remains the judge of their own progress, and cognitive psychology has established for decades that this judge is biased toward the strategies that feel effective rather than those that are.

Large language models changed one half of this. Conversational tutoring is now genuinely capable: it explains, adapts, questions and diagnoses. What it lacks is memory with integrity. A model asked at the start of a session what the learner knows must rely on notes the learner wrote, or on its own account of earlier sessions, and it will accept a correction to that account whenever the learner offers one.

This project is undertaken because the author has built and used a prototype of the intended system for several weeks — a conversational tutoring project writing to a note vault and a flashcard collection — and has logged how it fails. It teaches well and its bookkeeping is unreliable in repeatable ways. Those failures are the specification, and correcting them requires an architectural change rather than better instructions.

---

## 3. Problem Statement & Gap Analysis

A self-directed learner's decision about what to revise rests on an estimate of what they know, and that estimate is distorted. Repeated study raises confidence without improving delayed retention, whereas testing improves it [1]; of ten study techniques systematically reviewed, practice testing rated high utility and re-reading low [2]. A learner's sense of their own coverage is not a usable instrument.

Existing software supplies no better one, because each class of tool models the material rather than the learner. Spaced-repetition schedulers estimate recall probability accurately for atomic items [5], [6], [7] but represent no mechanism; note applications record what was written, not what can be produced unaided. Conversational tutoring systems now maintain persistent, auditable learner state [17] and deliver practice between sessions [18], closing part of the gap.

Three absences remain. First, the evidence behind a competence rating is not recorded, so an answer produced cold and one produced with the working on screen are stored identically. Second, only the fact of failure is captured, never its route, so an answer that is correct by the wrong mechanism is indistinguishable from understanding. Third, assessment is generated inside the conversation that taught, and models tuned on human feedback concede errors when challenged and revise correct answers toward the user's view [10] — so a judgement is least reliable precisely when disputed.

The result is a record of mastery that must be independently re-derived before it can be relied on — costlier than holding no record, because a false one stops the learner looking. This project therefore treats learning state as an auditable measurement problem rather than a note-keeping one.

**Scope bound:** The project addresses the modelling, scheduling and assessment of one learner's knowledge for a single operator. Teaching itself remains with the general-purpose conversational model and is not reimplemented; multi-user operation and authentication, authored curricula, and retrieval over source documents during teaching are outside its scope.

---

## 4. Proposed Solution / Product Concept

Anamnesis is a local service owning a learner's knowledge state: readable by a teaching conversation, not writable by it.

The atomic unit is the probe: a retrieval prompt bound to a concept, carrying a rubric written once and never edited. A concept holds no rating of its own; its state is a roll-up of its probes, so "explains it, cannot transfer it" stays visible rather than collapsing into one figure.

Responsibility divides across three layers. Teaching stays in editable prose instruction files driving a general-purpose model. The service holds an append-only event log from which every derived value is recomputed deterministically; it stores rubrics, grades, schedules review per probe, ranks candidates, and refuses tool calls whose preconditions are unmet, making ordering rules mechanical rather than advisory. A background process dispatches due probes to a messaging channel when no session is open, since the protocol is client-initiated and a server cannot originate contact [22].

Assessment is isolated by location, not instruction: the caller passes only a probe reference and a verbatim response; the service retrieves the rubric and calls its own pinned model, so the verdict forms outside the conversation holding the objection. Each attempt yields verdict, route quality and expressed confidence separately, and only the verdict advances memory state.

---

## 5. Objectives & Target Market

**Primary objective:** To build and evaluate a service holding an evidence-backed model of one learner's knowledge that a teaching conversation can read but not alter.

**Secondary objectives:**
- To establish whether an isolated examiner can separate correct answers from correct-sounding ones without ground truth.
- To derive all state from an immutable log, leaving no path by which competence is asserted rather than evidenced.
- To determine whether tool preconditions constrain a calling model, and quantify residual bypass.
- To deliver retrieval outside any session and measure its yield as retention evidence.

**Target market:** One self-directed learner studying technical material across domains — not classrooms, cohorts, or authored curricula. Generalisation beyond a single operator is not evaluated.

---

## 6. Customer & User Research

No formal interview study has been conducted. Requirements were derived from two sources, both stated as what they are.

**Instrumented use of a working prototype.** The author built and used a prototype — a conversational tutoring project writing to a note vault and a flashcard collection — and retained the transcripts. Analysis of eight sessions identified four reproducible failures. A due item was surfaced and deferred in five consecutive sessions, reaching twelve days overdue, because the ordering rule existed only as prose. A topic was recorded as securely known after a retrieval attempt made minutes after the answer was given, with the working still on screen. A wrong answer was committed as correct after the learner objected, having been assessed correctly moments earlier in the same conversation. Two reads of the same record on the same day disagreed about the same review date, because the model both wrote and interpreted its own state.

**Published evidence that these are general.** The third failure is a documented property of models tuned on human feedback [10]; the second matches the established dissociation between confidence and delayed retention [1]. Each failure is therefore treated as structural, not incidental.

**Planned validation.** Requirements are validated in use rather than by survey: from Month 3 every phase must be usable for real study before the next begins, and the system serves as the author's sole learning system for four consecutive weeks in Months 7–8, the resulting log providing the measurements in §8.

**Requirements derived:**
- Ordering rules must be enforced by refusal, not stated as instruction.
- Assessment must execute outside the conversation that delivered the teaching.
- Retention evidence must be distinguished from in-session performance and recorded with the attempt's conditions.
- No component other than the service may write learner state.
- Reading current state must cost one call and must not grow with the graph.

---

## 7. Tools and Technologies

**Language and runtime:** Python 3.12 — the connector, scheduling and flashcard libraries are Python-native.

**Service layer:** Model Context Protocol server over local standard I/O [22], plus a separate always-on dispatch process, since the protocol is client-initiated.

**Assessment:** Hosted model inference API, version pinned and recorded on every graded event, keeping strictness comparable across releases.

**Memory model:** FSRS [5], [6], with a fixed interval ladder as fallback if the §8 evaluation fails.

**Data storage:** Single-file embedded database — append-only events, derived tables rebuilt by replay.

**Messaging channel:** Telegram Bot API, for scriptability and no template approval; confirmed Month 6 against cost and latency.

**Project management:** Git; milestone gates as in §13.

---

## 8. Expected Outcomes / KPIs

**Technical outcomes:** a connector and dispatcher, a replayable learner-state store, an evaluation set and grading harness; integrity and refusal coverage verified by test (§9).

**Key performance indicators:**
- **Grading separation:** ≥90% of seeded pairs ranking the confidently-wrong answer below the hedged-correct one — design target, baselined Month 2; [9] reports over 80% judge–human agreement, establishing feasibility but not this threshold.
- **Route detection:** ≥80% of seeded right-answer-wrong-mechanism responses recorded as route failures — design target, baselined Month 2.
- **Schedule adherence:** no probe past its review date beyond one dispatch cycle without dispatch or recorded deferral — absolute, audited across the trial.
- **Ambient yield:** ≥20% of graded attempts arriving outside a session — above the 11–13% reported for notification-triggered engagement [19], [20]; measured in the trial.

---

## 9. Completeness Criteria

The project is complete when the following hold and can be judged by inspection or test:

The service accepts, stores and grades probes, computing every derived value from the event log alone; deleting derived state and replaying reproduces it exactly, and no code path raises a competence rating. Grading accepts only a probe reference and a verbatim response, rejecting any attempt to supply a rubric or verdict. Each of the four failures in §6 has a corresponding tool refusal demonstrated by test, and teaching conducted without recorded attempts appears at the next read-back as missing evidence. Read-back is one call returning a payload bounded at realistic graph size. The dispatcher runs with no client session open, survives sleep and wake, catches up missed windows within the daily limit, and reports its liveness in the read-back payload. A photographed handwritten answer grades through the same path as a typed one. Notes and printable sheets regenerate identically from identical events. The author has used the system as their sole learning system for four consecutive weeks with the prototype disabled.

Completeness is assessed against single-operator use. Importing the existing vault and flashcard collection, visualising the graph interactively, and supporting a second user are not completion conditions.

---

## 10. Challenges

**Grading open-ended answers without ground truth** is the hardest problem and could invalidate the design. It is confronted first, as a Month 2 feasibility gate against a seeded evaluation set; the architecture is revised if it fails.

**A refusal can be routed around** by a model that declines to call the tool, and policy-bound agents already follow written rules unreliably [16]. Managed in two layers: unrecorded teaching becomes detectable at read-back, and residual bypass is measured, not assumed.

**An always-on process on a laptop can fail silently**, restoring the problem the project exists to solve. Its liveness is reported in the read-back payload, so a stopped dispatcher surfaces next session.

---

## 11. Project Success Criteria

The project succeeds if the system is demonstrated end-to-end — a topic taught through the connector, probes authored and graded, review scheduled, a due probe delivered and answered outside any session, and the resulting state shown reproducible from its log — and if the author has replaced the prototype with it for four continuous weeks of real study.

Success also admits a negative result at the feasibility gate: if isolated assessment cannot separate understanding from fluent recall on open-ended material, that finding, measured and reported with the architectural revision it forces, is a legitimate outcome.

---

## 12. Related Work / Literature Survey

| ID | What it covers | Methods / concepts | Key findings | Limitation / gap this project targets |
|---|---|---|---|---|
| 3–8 | Learner modelling, scheduling and short-answer grading | Knowledge tracing; scheduling over large review logs; survey of 35 grading systems | Mastery estimates predict next-response correctness; retrievability from history improves review efficiency; grading consolidated around reference answers | Need a pre-authored skill decomposition, atomic items, or ground-truth reference answers — none available to a learner studying arbitrary material; correctness is modelled, the route is not |
| 9–11 | Model evaluators and their stability | Judges scored against human preference; rebuttal and persona probes | Over 80% agreement with human preference [9]; assistants concede errors when challenged and revise correct answers toward the user's view [10]; casual rebuttal persuades a judge more than formal critique [11] | Mitigate instability by prompt or persona; none removes the dialogue from the grader's input by construction |
| 12–14 | Reasoning route versus outcome | Process- and outcome-supervised reward models; faithfulness probes; staged rubric grading of handwritten calculus | Outcome supervision regularly yields correct answers reached by incorrect reasoning; stated reasoning is often post-hoc; staged grading beats single inference on step criteria | Route quality trains models or grades one exam; it is never a persisted per-learner signal, and the grader still sees the instructional context |
| 15 | Isolated verification in agent architectures | A verifier sub-agent between agent and environment, reading the full dialogue | Dialogue context improves policy verification over tool-call-only checks | The verifier is deliberately given the dialogue — the inverse of the isolation required here, and evidence that context-starved verification is not the norm |
| 16 | Whether tool constraints constrain a model | Typed tool APIs plus written policy; simulated users; repeated trials | Policy-bound agents follow rules unreliably and inconsistently across runs | Measures compliance as an outcome; leaves open whether refusing preconditions change behaviour in a tutoring loop |
| 17, 18 | Persistent learner state in conversational tutors | Centralised versioned state under a single-writer policy [17]; learner memory with scheduled out-of-session delivery [18] | Auditable state makes multi-turn tutoring consistent; proactive agents reach the learner without waiting for a conversation | Assessment runs inside the context that teaches; mastery is a scalar with no route signal; state is versioned, not recomputed from an immutable log, so a claim cannot be re-derived from its evidence |
| 19, 20 | How much practice arrives unprompted | Bandit optimisation over ~200 million reminders; wearable-video ethnography | Reminder-to-practice conversion near 13% within two hours, most lessons organic [19]; 11% of smartphone interactions notification-triggered [20] | Sets the realistic ceiling for out-of-session practice, against which this project's target is calibrated |
| 22 | The connector protocol implemented here | Open client–server standard exposing tools, resources and prompts | Standardises tool access; interaction is client-initiated | A server cannot originate contact, so scheduled delivery needs a separate process |

**Assessment of the gap.** The survey narrows this project's claim in two places and closes it in a third. Persistent auditable learner state is implemented in [17], and scheduled delivery with no session open in [18], so out-of-session retrieval is a known capability — claimed here as a requirement, not a contribution. Scoring the route separately from the answer is mature [12], [13] and already practised in educational grading [14], so what is claimed is the persisted three-signal representation, not the insight. No surveyed work combines all state recomputed deterministically from an append-only log, grading executed outside the teaching context by location — the inverse of [15] — and ordering enforced by refusing tool preconditions. The contribution is claimed at that intersection.

---

## 13. Project Plan / Schedule

| Months | Work breakdown & milestones |
|---|---|
| 1 | Requirements consolidation from the prototype transcripts; probe and rubric schema design; construction of the seeded evaluation set, including matched confidently-wrong / hedged-correct pairs and right-answer-wrong-mechanism responses. **Milestone: evaluation set built and frozen.** |
| 2 | Grading harness: blind assessment against stored rubrics with a pinned model, emitting verdict, route quality and expressed confidence separately. Agreement with a held-out human-labelled sample is reported as Cohen's κ per criterion, against the substantial band [21]. **Milestone (feasibility gate): grading separation and route detection measured against the evaluation set. If the gate is not met, the architecture is revised before any further phase runs.** |
| 3 | Append-only event log, deterministic reducer, derived state, concept and probe storage; per-probe scheduling. **Milestone: derived state reproduced exactly by replay.** First phase usable for real study. |
| 4 | Connector tool surface; gated preconditions covering each documented failure; single-call read-back digest. **Milestone: one topic taught end-to-end through the connector.** |
| 5 | Candidate generation and ranking; note export; instrumentation of refusals. **Milestone: bypass rate and read-back token cost measured at realistic graph size.** |
| 6 | Background dispatcher: scheduled delivery, messaging channel, reply ingestion and grading, catch-up after missed windows, liveness reporting. Channel confirmed against cost and latency criteria. **Milestone: schedule runs for two weeks with no client session open.** |
| 7 | Printable retrieval sheets; photographed handwritten answers graded through the same path; confidence calibration. **Milestone: handwritten attempt produces the same three outputs as a typed one.** Four-week sole-use trial begins, prototype disabled. |
| 8 | Trial completes; KPI evaluation against the event log; test completion for every mandatory capability; documentation, final report and demonstration preparation. **Milestone: four consecutive weeks as sole learning system, with results reported.** |

**Resources:**

| Subtask | Resources used |
|---|---|
| Evaluation set and grading harness | Hosted model inference API (metered); seeded answer set authored by the author |
| Event log, reducer, connector service | Python 3.12; embedded single-file database; local development machine |
| Scheduling | FSRS implementation, with fixed interval ladder as fallback |
| Background dispatch | Messaging bot API; always-on local process |
| Semantic reconciliation of concepts | Local embedding model |
| Exports | Note vault on local filesystem; printable sheet generation |
| Testing and measurement | Automated test suite; audit queries over the event log |

**Monitoring & advisor checkpoints:** Fortnightly supervisory meetings, with a written progress note against the current milestone's exit criterion; formal review at the Month 2 feasibility gate and at the Month 6 dispatch milestone. ‹Confirm cadence against the department minimum.›

**Per-student contribution:** Single-student project. The workstreams are the assessment and evaluation track (Months 1–2, 7–8), the state and service track (Months 3–5), and the delivery and integration track (Months 6–8); they are sequenced rather than parallel for this reason.

---

## 15. Sketch of Proposed Solution

```
+----------------------------------------------------------------+
|  TEACHING LAYER   (editable prose; owns pedagogy, no state)    |
|      Conversational model + instruction files  <-->  LEARNER   |
+-------+-------------------------------------+------------------+
        | tool calls (gated)                  | probe ref +
        v                                     v verbatim answer
+----------------------------------------------------------------+
|  ANAMNESIS SERVICE  --  sole writer of state                   |
|                                                                |
|   +------------+    +-------------+   +-------------------+    |
|   | Gated tool |--->|  Event log  |<--|  EXAMINER         |    |
|   |  surface   |    |(append-only)|   |  stored rubric +  |    |
|   +------------+    +------+------+   |  pinned model,    |    |
|                            |          |  no dialogue      |    |
|                            v          |  history          |    |
|                     +-------------+   +-------------------+    |
|                     |   Reducer   |   (deterministic,          |
|                     +------+------+    replayable)             |
|                            v                                   |
|              +------------------------+                        |
|              | Derived learner state  |                        |
|              | probe memory . error   |                        |
|              | trail . calibration    |                        |
|              +---+----------------+---+                        |
|                  v                v                            |
|         +---------------+  +---------------+                   |
|         | Due queue     |  | Candidate     |                   |
|         | (gated)       |  | queue(ranked) |                   |
|         +-------+-------+  +---------------+                   |
+-----------------+----------------------------------------------+
                  | shared store
                  v
+------------------------------+      +--------------------------+
|  DISPATCHER (always-on)      |      |  EXPORTS (write-only)    |
|  schedule . send . receive   |<---->|  note vault .            |
|  reply . liveness            |      |  printable sheets        |
+--------------+---------------+      +--------------------------+
               | one-line question / one-line reply
               v
        MESSAGING CHANNEL  <-->  LEARNER  (no session open)
```

Three properties are visible in the diagram and carry the design. All writes converge on the event log, and every displayed value is recomputed from it rather than stored independently. The examiner receives only a probe reference and a verbatim answer, so no path exists by which the teaching dialogue reaches the grading decision. The dispatcher shares the store but not the session, which is what allows retrieval to continue when nothing is open.

---

## 16. References / Bibliography

[1] H. L. Roediger III and J. D. Karpicke, "Test-enhanced learning: Taking memory tests improves long-term retention," *Psychological Science*, vol. 17, no. 3, pp. 249–255, 2006. doi: 10.1111/j.1467-9280.2006.01693.x

[2] J. Dunlosky, K. A. Rawson, E. J. Marsh, M. J. Nathan and D. T. Willingham, "Improving students' learning with effective learning techniques: Promising directions from cognitive and educational psychology," *Psychological Science in the Public Interest*, vol. 14, no. 1, pp. 4–58, 2013. doi: 10.1177/1529100612453266

[3] A. T. Corbett and J. R. Anderson, "Knowledge tracing: Modeling the acquisition of procedural knowledge," *User Modeling and User-Adapted Interaction*, vol. 4, no. 4, pp. 253–278, 1994. doi: 10.1007/BF01099821

[4] C. Piech, J. Bassen, J. Huang, S. Ganguli, M. Sahami, L. J. Guibas and J. Sohl-Dickstein, "Deep knowledge tracing," in *Advances in Neural Information Processing Systems 28 (NeurIPS)*, 2015, pp. 505–513.

[5] J. Ye, J. Su and Y. Cao, "A stochastic shortest path algorithm for optimizing spaced repetition scheduling," in *Proc. 28th ACM SIGKDD Conf. on Knowledge Discovery and Data Mining*, 2022, pp. 4381–4390. doi: 10.1145/3534678.3539081

[6] J. Su, J. Ye, L. Nie, Y. Cao and Y. Chen, "Optimizing spaced repetition schedule by capturing the dynamics of memory," *IEEE Transactions on Knowledge and Data Engineering*, 2023. doi: 10.1109/TKDE.2023.3251721

[7] B. Settles and B. Meeder, "A trainable spaced repetition model for language learning," in *Proc. 54th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*, 2016, pp. 1248–1258.

[8] S. Burrows, I. Gurevych and B. Stein, "The eras and trends of automatic short answer grading," *International Journal of Artificial Intelligence in Education*, vol. 25, no. 1, pp. 60–117, 2015. doi: 10.1007/s40593-014-0026-8

[9] L. Zheng, W.-L. Chiang, Y. Sheng, S. Zhuang, Z. Wu, Y. Zhuang, Z. Lin, Z. Li, D. Li, E. P. Xing, H. Zhang, J. E. Gonzalez and I. Stoica, "Judging LLM-as-a-judge with MT-Bench and Chatbot Arena," in *Advances in Neural Information Processing Systems 36 (NeurIPS), Datasets and Benchmarks Track*, 2023.

[10] M. Sharma, M. Tong, T. Korbak, D. Duvenaud, A. Askell, S. R. Bowman, E. Durmus, Z. Hatfield-Dodds, S. R. Johnston, S. Kravec, T. Maxwell, S. McCandlish, K. Ndousse, O. Rausch, N. Schiefer, D. Yan, M. Zhang and E. Perez, "Towards understanding sycophancy in language models," in *Proc. 12th International Conference on Learning Representations (ICLR)*, 2024. arXiv:2310.13548

[11] S. W. Kim and D. Khashabi, "Challenging the evaluator: LLM sycophancy under user rebuttal," in *Findings of the Association for Computational Linguistics: EMNLP 2025*, 2025. arXiv:2509.16533

[12] H. Lightman, V. Kosaraju, Y. Burda, H. Edwards, B. Baker, T. Lee, J. Leike, J. Schulman, I. Sutskever and K. Cobbe, "Let's verify step by step," in *Proc. 12th International Conference on Learning Representations (ICLR)*, 2024. arXiv:2305.20050

[13] M. Turpin, J. Michael, E. Perez and S. R. Bowman, "Language models don't always say what they think: Unfaithful explanations in chain-of-thought prompting," in *Advances in Neural Information Processing Systems 36 (NeurIPS)*, 2023. arXiv:2305.04388

[14] L. Y. Tan, B. Zhu, S. Hu, A. Mishra, D. J. Yeo and K. H. Cheong, "CalcTutor: Multi-agent LLM grading of handwritten mathematics with RAG-grounded feedback for adaptive learning support," *Mathematics*, vol. 14, no. 7, art. 1094, 2026. doi: 10.3390/math14071094

[15] S. Kang et al., "PolicyGuard: A dialogue-grounded sub-agent verifier for policy adherence in LLM agents," arXiv:2606.29225, 2026.

[16] S. Yao, N. Shinn, P. Razavi and K. Narasimhan, "τ-bench: A benchmark for tool-agent-user interaction in real-world domains," in *Proc. International Conference on Learning Representations (ICLR)*, 2025. arXiv:2406.12045

[17] J. David and S. Ghosh, "IntelliCode: A multi-agent LLM tutoring system with centralized learner modeling," in *Proc. 19th Conf. of the European Chapter of the Association for Computational Linguistics: System Demonstrations*, 2026. arXiv:2512.18669

[18] B. Zhao, J. Zhang, X. Ren, Z. Guo, T. Chu, Y. Ma and C. Huang, "DeepTutor: Towards agentic personalized tutoring," arXiv:2604.26962, 2026.

[19] K. P. Yancey and B. Settles, "A sleeping, recovering bandit algorithm for optimizing recurring notifications," in *Proc. 26th ACM SIGKDD Conf. on Knowledge Discovery and Data Mining*, 2020, pp. 3008–3016. doi: 10.1145/3394486.3403351

[20] M. Heitmayer and S. Lahlou, "Why are smartphones disruptive? An empirical study of smartphone use in real-life contexts," *Computers in Human Behavior*, vol. 116, art. 106637, 2021. doi: 10.1016/j.chb.2020.106637

[21] J. R. Landis and G. G. Koch, "The measurement of observer agreement for categorical data," *Biometrics*, vol. 33, no. 1, pp. 159–174, 1977.

[22] Anthropic, "Model Context Protocol," specification and documentation. [Online]. Available: https://modelcontextprotocol.io — and https://www.anthropic.com/news/model-context-protocol. Accessed: 27 July 2026.
