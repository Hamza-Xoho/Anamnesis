---
id: TRACE-anamnesis
type: proposal-trace
proposal: anamnesis-proposal.md
proposal_version: 0.2.0
charter: anamnesis-charter.md
charter_version: 0.2.0
literature_findings: promoted 2026-07-27
created: 2026-07-27
---

# Anamnesis — Proposal Trace

Every substantive claim in the proposal mapped to its source. This is the viva-preparation document: the answer to *"where did that come from?"*. It is also what makes the proposal re-derivable when the charter version moves past 0.2.0.

---

## 0. Literature promotion (proposal v0.1.0 → v0.2.0)

Literature findings returned and promoted on 2026-07-27. The gap assessment was read **before** any table row was written, because it changes claims rather than citations.

### What the findings did to each claim

| Claim | Verdict | What changed in the proposal |
|---|---|---|
| Assessment isolated from the teaching context by execution location | **Holds, narrowed.** The countermeasure pattern exists in agent safety, but no system starves the grader of dialogue, rubric and suggested verdict | §12 now cites the nearest precedent [15] explicitly and states that its verifier is deliberately given the dialogue — the inverse design. Claim stated as the specific boundary, not "isolating the grader" |
| Route quality as a signal distinct from correctness | **Largely occupied.** This is the process-versus-outcome distinction, already practised in educational grading | §12 cites [12], [13] as the origin and [14] as the education precedent, then claims only the **persisted three-signal representation** |
| Retrieval delivered when no session exists | **Occupied as a capability** by [18], which ships scheduled out-of-session delivery | Retired as a contribution. §1, §3 and §12 now state it as a requirement the design must meet, not a novelty |

**The surviving contribution is the conjunction**, stated in §12: deterministic recomputation from an append-only log + grading isolated by execution location + ordering enforced by refusing preconditions. No surveyed work combines all three.

### Thresholds re-grounded

| Target | Was | Now | Basis |
|---|---|---|---|
| Ambient yield | ≥50%, design target, no external grounding | **≥20%**, stated as above baseline | Contradicted by [19] (≈13% reminder-to-practice within two hours, most lessons organic, ~200M reminders) and [20] (11% of smartphone interactions notification-triggered). ≥50% would have exceeded every known figure with no stated mechanism |
| Grading separation | ≥90%, design target | Unchanged, provenance tightened | [9] over 80% judge–human agreement establishes feasibility, not the threshold |
| Grader agreement protocol | none | Cohen's κ per criterion against a held-out human-labelled sample, substantial band | [21]; added to the Month 2 milestone in §13 |
| Tool-precondition compliance | framed as an open question | cited baseline | [16]; added to §10 so the objective measures against a known figure rather than rediscovering it |

### Sources deliberately **not** used

- A language-learning trial reporting an 82%/67%/49% notification-versus-self-scheduled adherence split was found in a non-indexed venue and could not be verified. **Excluded.** It would have supported the original ≥50% target, which is precisely why it must not be cited.
- Three near-precedents (TASA, AgentTutor, and a workshop paper on unfaithful tool refusals) were verified as existing but do nothing on the three claims; omitted for space rather than substance.
- A 2026 study of vision-model grading of handwritten mathematics reports most residual error as transcription failure rather than rubric misapplication. Relevant to the Month 7 photo-ingestion work; not cited here because it does not bear on the gap. **Carry it into the design spec.**

---

## 1. The uncertainty ledger

Every `Q-`, `AS-`, `RISK-` and `proposed` item in charter v0.2.0, and which of the three moves it took. **Nothing was deleted.**

### Committed — decided on your behalf; sanity-check these

| Charter item | Commitment made | Where it appears |
|---|---|---|
| Q-4 — which ambient channel | Telegram Bot API, with the selection criterion (cost, delivery latency) stated and confirmation scheduled for Month 6 | §7 Tools; §13 Month 6 |
| Q-5 — integrate with or absorb the rote store | **Integrate, not absorb.** The existing flashcard collection remains the rote store; absorbing it is out of scope | §7 Tools (Python-native libraries); §9 (import not a completion condition) |
| Q-6 — migrate existing vault and cards as seed | **Start clean.** Import is explicitly not a completion condition | §9 Completeness |
| AS-2 — hosted inference API | Stated declaratively as the assessment layer | §7 Tools |
| AS-3 — tests for all mandatory capabilities | Stated as a completion condition and a Month 8 deliverable | §9; §13 Month 8 |
| AS-7 — no hard external deadline | **Reversed.** The registered term now imposes one; the roadmap was fitted to eight months | §13 |
| Technical Direction (whole table, marked `proposed`) | Committed as the stated stack, with rationale only on contentious choices | §7 |
| Charter M4/M5 scope | **Cut.** Interactive visualisation, collection import and the standalone application are excluded and named as non-completion conditions | §9 |

### Absorbed — uncertainty converted into work the project does

| Charter item | Became | Where |
|---|---|---|
| **Q-1** — can the examiner separate verdict, route and confidence without ground truth? *(blocking, gates everything)* | Secondary objective 1 + the Month 2 **feasibility gate** with an explicit exit criterion and a stated architecture revision on failure | §5; §8 (two KPIs); §10; §13 Month 2 |
| **Q-8** — do tool preconditions actually constrain a calling model? | Secondary objective 3, framed as an empirical determination with residual bypass **quantified** rather than assumed | §5; §10; §13 Month 5 |
| Q-2 / RISK-3 — does FSRS generalise to open-ended probes? | Stated limitation in the survey (row 5, 6), a fallback interval ladder in Tools, and a Challenges entry stated as managed | §7; §10; §12 |
| Q-3 — real rubric authoring cost | Folded into the Month 1–2 evaluation-set and harness work; measured rather than asserted | §13 Months 1–2 |
| Q-9 — read-back context cost at realistic size | Completion condition ("bounded at realistic graph size") and a Month 5 measurement milestone | §9; §13 Month 5 |
| AS-6 — rubric quality without routine review | Absorbed into the same Month 1–2 measurement | §13 |
| AS-10 — enforcement changes model behaviour | Same as Q-8 — this is the assumption the objective tests | §5 |
| RISK-1 *(fatal)* — examiner cannot grade reliably | Challenges entry #1, stated with the gate that resolves it | §10 |
| RISK-10 — the model routes around a refusal | Challenges entry #2, with the two-layer management | §10 |
| RISK-13 — the dispatcher dies silently | Challenges entry #3, with liveness surfaced in the read-back payload | §10 |
| RISK-5 — building consumes the learning it serves | Plan constraint: every phase from Month 3 must be usable for real study | §6; §13 Month 3 |
| RISK-4 — ambient fatigue | Dissolved into the daily message limit in §9 | §9 |
| RISK-6 — grading strictness drifts across model versions | Dissolved into the pinned-and-recorded model version | §7 |
| RISK-8 — hedging registers penalised | Dissolved into calibration work | §13 Month 7 |

### Disclosed — stated as bounds, not hidden

| Charter item | Disclosure | Where |
|---|---|---|
| AS-1 / CON-11 — single user, no auth | Scope bound: multi-user operation and authentication outside scope | §3 scope bound; §5 |
| AS-4 — English only | *Not separately disclosed.* See open items below |
| AS-8 — target user's client supports a custom connector | Folded into the single-operator applicability bound | §5 |
| AS-9 — metered API key for dispatcher grading | Stated as a hosted metered API in Tools | §7 |
| Q-7 — is "others later" real? *(parked)* | "Generalisation beyond a single operator is not evaluated" | §5 |
| Non-goals: no tutor in the server, no corpus retrieval, no authored curriculum | Scope-bound sentence and completeness criteria | §3; §9 |
| SC-1, SC-4, SC-5, SC-10 *(all `proposed`)* | Every one reads as a **design target with a baselining phase named** — never as a settled result | §8 |

---

## 2. Section-by-section provenance

| Proposal section | Charter source | Citations | Notes |
|---|---|---|---|
| §1 Abstract | §1 TL;DR, §2, §4, O8 | — | Every claim restated from a supported section below |
| §2 Introduction | §2 *Why now*, §3 | — | Prototype account is the "why us" line; the only place personal motivation appears |
| §3 Problem & Gap | §2 Problem, §2 Gap, O7 Prior Art, §5 Non-goals | [1], [2], [5], [6], [7], [10], [11] | The three absences are the charter's Gap bullet, now each carrying evidence |
| §4 Proposed Solution | §4 Solution Concept; CON-1, 3, 5, 12, 13, 14 dissolved into prose | [12] | Mermaid diagram redrawn as §15; no constraint IDs survive |
| §5 Objectives | OBJ-1…8 compressed; Q-1 and Q-8 absorbed as objectives | — | Eight charter objectives → one primary + four secondaries (see chain below) |
| §6 User Research | §2 *Why now*, §3 use cases, prototype transcript analysis | [1], [2], [10] | Honest route 2 + route 3; **no invented interviews or statistics** |
| §7 Tools | §9 Technical Direction, ADR-11, 12, 14 | [5], [6], [12] | Rationale only on contentious choices |
| §8 KPIs | SC-1, SC-3, SC-4, SC-5 | [9] | Every threshold carries provenance |
| §9 Completeness | Definition of Done + O8 exit criteria + SC-2, 6, 8, 9, 10 | — | Second home for the scope bound |
| §10 Challenges | RISK-1, 10, 13 | — | Register inverted: risks stated as managed |
| §11 Success Criteria | Definition of Done, OBJ-1 | — | Explicitly admits the negative result at the gate |
| §12 Literature | O7 Prior Art (positioning only) + new research | [1]–[12] | **Not derivable from the charter** — see §4 below |
| §13 Plan | O8 Milestones M0–M4 | — | Dependency order → calendar order, fitted to eight months |
| §15 Sketch | §4 Mermaid diagram | — | Redrawn as a labelled block diagram |

---

## 3. The objective chain

Each objective must have a deliverable, a measurable outcome, and a slot in the plan. A panel checks this.

| Objective | Deliverable | Measured by | Plan slot |
|---|---|---|---|
| **Primary** — evidence-backed learner model, readable but not writable by the conversation | Connector service + replayable state store | State integrity (§9, property test); all §8 indicators | Months 3–5 |
| **S1** — isolated examiner separates correct from correct-sounding | Grading harness + seeded evaluation set | Grading separation ≥90%; route detection ≥80% (§8) | Months 1–2 (**gate**) |
| **S2** — all state derived from an immutable log | Event log + deterministic reducer | Replay reproduces state exactly; no code path raises a rating (§9) | Month 3 |
| **S3** — determine whether preconditions constrain the model; quantify bypass | Gated tool surface + refusal instrumentation | Refusal test per documented failure (§9); bypass rate (§13 M5) | Months 4–5 |
| **S4** — retrieval delivered outside a session | Dispatcher + messaging channel + reply grading | Ambient yield ≥50%; schedule adherence (§8) | Months 6–8 |

No orphans in either direction: every plan month serves at least one objective, and every objective appears in the plan.

---

## 4. Citation status

All twenty-two references were verified against the published record. **No citation was generated from memory, and none was accepted from the findings without checking the record.**

| ID | Source | Verification |
|---|---|---|
| [1]–[8] | Cognitive foundation, knowledge tracing, scheduling, short-answer grading | Journal, volume, pages and DOI confirmed for each; [4] and [7] confirmed across independent reference lists |
| [9] | LLM-as-a-judge | Venue and track confirmed; >80% figure is the paper's own reported result |
| [10] | Sycophancy | ICLR 2024 and arXiv identifier confirmed |
| [11] | Evaluator sycophancy under rebuttal | EMNLP 2025 Findings; arXiv identifier confirmed |
| [12] | Let's Verify Step by Step | ICLR 2024; author list and arXiv identifier confirmed |
| [13] | Unfaithful chain-of-thought | NeurIPS 2023; author list and arXiv identifier confirmed |
| [14] | CalcTutor | **Author list resolved during promotion** — the findings flagged it as unresolved. Journal, volume, article number and DOI confirmed |
| [15] | PolicyGuard | **First author resolved during promotion.** Cited as "S. Kang et al." because the full list was not recoverable — abbreviated, not invented. Note there is a second, unrelated paper of the same name; this is arXiv:2606.29225 |
| [16] | τ-bench | ICLR 2025; author list and arXiv identifier confirmed |
| [17] | IntelliCode | ACL Anthology entry and arXiv identifier confirmed |
| [18] | DeepTutor | **Full author list resolved during promotion**; arXiv identifier and open-source release confirmed |
| [19] | Duolingo notification bandit | KDD 2020; pages and DOI confirmed |
| [20] | Smartphone interaction ethnography | Journal, article number and DOI confirmed |
| [21] | Landis & Koch | **Added during promotion** to give the κ bands a source rather than asserting them |
| [22] | Model Context Protocol | Vendor documentation, labelled as such, with access date |

**Every table ID resolves to a bibliography entry**, and every bibliography entry is cited somewhere in the document ([3], [4] and [8] via the merged survey row). **Every row's last column names the gap this project targets.**

Seven of the twenty-two are 2025–2026 preprints ([11] is peer-reviewed Findings; [15] and [18] are not yet refereed). [18] is the load-bearing one, and its capabilities are verifiable in its public release even though the paper is not refereed — worth saying aloud if a panel member presses on preprint reliance.

## 5. Open items requiring your decision

1. **All administrative fields** — registration number, surname, contact, CGPA, institution, faculty, programme, term, advisor. Left as visible `‹…›` tokens.
2. **The institutional proforma.** The default template was used; section names, word limits and conditional sections vary by department. The cover-page boilerplate must be pasted verbatim from your own.
3. **Term length.** The plan assumes eight months. If yours differs, Months 5 and 7 are the compressible ones.
4. **The ambient-yield target is now ≥20%, not ≥50%.** This is the single largest substantive change and it is yours to confirm. The evidence says ≥50% would exceed every measured baseline; if you want to keep a higher figure, it needs a stated mechanism (a committed single learner with no competing in-app surface) and should be labelled aspirational.
5. **Charter divergence is now substantial.** Beyond the earlier commitments (Q-4, Q-5, Q-6, the reversed deadline assumption and the M4/M5 cut), the charter still frames out-of-session delivery and learner modelling as contributions. Both are occupied. **Charter v0.3.0 should restate the contribution as the conjunction** before any design-spec work begins, or the build will be aimed at the wrong claim.
6. **Word limits.** Nine sections exceed by 2–46 words, 106 in total. The largest is §12 at 546/500; the cut I would make is the merged background row (learner modelling, scheduling and short-answer grading), which recovers roughly 55 words and would also retire [3], [4] and [8] from the bibliography. I left it in because it is what licenses the "models the material, not the learner" framing in §3.
7. **AS-4 (English-only content)** remains undisclosed. Defensible at this scope; raise it only if the calibration objective is questioned.
