# Phase 6 — Paper, photo, calibration

## Before you paste — setup only

**1. Launch a fresh session** from the repo root:

```bash
claude --model sonnet --effort high
```

**2. Run these in the session, before pasting:**

| Command | Why |
|---|---|
| `/status` | Confirm the model and effort actually took. Effort persists across sessions, so it may not be what you left behind |
| `/config` | Same classifier toggle as phase 0 — the transcription step sends handwritten medical answers to a vision model |
| `/clear` | Only if you're reusing a terminal rather than opening a new one. A genuinely fresh session is better |

**Plan mode:** no.
**Auditors:** `boundary-audit`, if the renderer reaches outside `export/`.
**Why this model:** three loosely coupled pieces, each moderately specified. Switch to `--model opus` for the calibration work if the relative-baseline maths goes wrong — FR-19 is subtler than it looks, because the baseline is per-learner and moves under you.

---

**▼ Everything below this line is the prompt. Paste from here.**

---

> Paste this into a fresh session. Self-contained: assume no memory of earlier phases.


## Goal

Retrieval leaves the screen: printable sheets at topic close, handwritten answers graded through the identical examiner path, and a calibration read that does not punish you for hedging.

## Requirements in scope

- **FR-16** — export a printable retrieval sheet at every topic close: blank diagrams, cold problems, no answers
- **FR-17** — ingest a photographed handwritten answer and grade it through the same examiner path
- **FR-14** — capture a predicted confidence before revealing the answer; compute calibration against outcome
- **FR-19** — calibrate expressed-confidence reads against the learner's own baseline, never an absolute register

## Read first

- `spec/design-spec.md` §1 row D-14, §3.2 (the `attempt_recorded` row), §4.1 (`record_attempt`), §3.3 (the `calibration` table)
- `tests/test-contract.md`, the Phase 6 table

## Not in this phase

- **Do not send images to the examiner.** Transcribe with a vision model first, store the transcription verbatim on the attempt event, then grade the text through the identical call (D-14). This keeps one examiner path and one pinned model, and makes transcription failure separable from grading failure — which the literature says is where most residual error in handwritten grading lives
- **No answers on the sheet.** A retrieval sheet with an answer key is a study sheet, and study sheets are what the whole project exists to replace
- **No absolute confidence register.** FR-19 is explicitly relative to this learner's own baseline
- **Expressed confidence must still have no path into verdict.** Phase 0 established that; do not let calibration work reopen it

## Definition of done

1. These tests pass, and were failing before the implementation:
   `test_fr16_sheet_generated_on_close`, `test_fr17_photo_produces_same_three_outputs`,
   `test_d14_transcription_stored_verbatim`, `test_d14_examiner_receives_text_not_image`,
   `test_fr14_calibration_queryable_per_subject_and_window`
2. `test_fr19_hedging_does_not_depress_relative_score` runs against real attempt history and reports a figure
3. `anamnesis replay --verify` still passes
4. No change to files outside `export/`, `channels/photo/`, `core/reducer.py`, `tests/contract/`

## Gate

```
pytest tests/contract/phase6/ -v && anamnesis export sheet <topic_id>
```

Then confirm by hand: **print a sheet, answer it on paper, photograph it, and put it through the system.** Compare the stored transcription against what you actually wrote. Then compare the grade against what you would have given yourself. If the grade is wrong, the stored transcription tells you immediately whether the vision model or the examiner failed — that separation is the point of D-14, and this is the check that proves it works.

## Stop

When the definition of done is met, stop and report. Do not begin the next phase.
