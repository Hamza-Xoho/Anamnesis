#!/usr/bin/env bash
# block-boundary-violation.sh — PreToolUse on Write|Edit
#
# Preventive half of the module-boundary invariants. Sees the whole new file on
# Write (tool_input.content) and only the added fragment on Edit
# (tool_input.new_string). No hook event receives a diff, so the Edit case is
# structurally partial — sweep-boundaries.sh is the backstop that reads disk.
#
#   INV-1  core/ makes no model or network calls        charter §9, ADR-3
#   INV-2  the examiner sees no conversation            CON-3, ADR-2
#   INV-3  only core/reducer.py writes derived state    CON-1
#   INV-5  route quality never reaches the rating       CON-12, ADR-11
#   INV-7  the event log is append-only                 FR-6, NFR-4
#
# Parses with python3 rather than jq: python3 is already a hard dependency of
# this project, jq is not. Fails CLOSED — any unexpected failure blocks, because
# a hook that fails open stops enforcing without saying so.
set -euo pipefail
command -v python3 >/dev/null || { echo "HOOK ERROR: python3 not found; cannot verify Anamnesis invariants." >&2; exit 2; }
trap 'echo "HOOK ERROR: boundary check did not complete; blocking rather than passing." >&2; exit 2' ERR

payload=$(cat)

field() {
  printf '%s' "$payload" | python3 -c '
import json, sys
d = json.load(sys.stdin)
ti = d.get("tool_input") or {}
for k in sys.argv[1:]:
    v = ti.get(k)
    if v:
        sys.stdout.write(str(v))
        break
' "$@"
}

path=$(field file_path)
body=$(field content new_string)

[ -z "$path" ] && exit 0
[ -z "$body" ] && exit 0

# Scope narrowly — Python source only, tests excluded. The spec, the phase
# prompts and the contract tests all quote forbidden strings on purpose. A hook
# that fires on prose gets ALL hooks switched off, and then nothing is enforced.
case "$path" in *.py) ;; *) exit 0 ;; esac
case "$path" in */tests/*|tests/*) exit 0 ;; esac

block() { printf '%s\n' "$1" >&2; exit 2; }

case "$path" in */core/*|core/*)
  if grep -qE '^[[:space:]]*(from|import)[[:space:]]+.*\b(anthropic|openai|httpx|requests|aiohttp|urllib)\b' <<<"$body"; then
    block "BLOCKED — INV-1: core/ must contain no model or network calls (spec §2; charter §9 Conventions).
core/ is the pure, replayable layer. A model call here makes replay non-deterministic
and breaks NFR-3, which is the whole trust model.
Do instead: put the call in agents/examiner/ or server/ and have core/ consume the
resulting event. If you need a model's judgement during reduction, you have found a
design error — stop and report it rather than working around this."
  fi
;; esac

case "$path" in */agents/examiner/*|agents/examiner/*)
  if grep -qE '^[[:space:]]*(from|import)[[:space:]]+.*\b(server|dispatcher|cli|channels)\b' <<<"$body"; then
    block "BLOCKED — INV-2: agents/examiner/ must not import server/, dispatcher/, cli/ or channels/ (spec §2; CON-3).
Isolation by execution location IS the project's contribution. An import here is a path
by which the teaching conversation could reach the grader.
Do instead: pass the five FR-4 inputs explicitly — concept, prompt, verbatim response,
rubric, answer_was_onscreen. Nothing else crosses this boundary."
  fi
;; esac

case "$path" in */memory/*|memory/*)
  if grep -qE 'route_quality|route_failure|route_marker' <<<"$body"; then
    block "BLOCKED — INV-5: memory/ must never reference route quality (spec §5.3; CON-12; ADR-11).
FSRS fits on a binary success/lapse target. No rating means 'right answer, wrong
reasoning' without corrupting the fit.
Do instead: rate from the verdict alone (spec D-19). A route failure emits a top-ranked
candidate in core/reducer.py — it never touches this module."
  fi
;; esac

case "$path" in */core/store.py|core/store.py) ;; *)
  if grep -qE '(UPDATE[[:space:]]+events|DELETE[[:space:]]+FROM[[:space:]]+events)' <<<"$body"; then
    block "BLOCKED — INV-7: the event log is append-only (spec §3.1; FR-6; NFR-4).
The log is the only irreplaceable artifact — everything else regenerates by replay.
Do instead: append a new event that supersedes the old one. There is no edit path,
by construction."
  fi
;; esac

case "$path" in */core/reducer.py|core/reducer.py) ;; *)
  if grep -qE '(INSERT[[:space:]]+INTO|UPDATE|DELETE[[:space:]]+FROM)[[:space:]]+.?(probe_state|concept_rollup|error_trail|calibration|candidate_rank|topic_evidence|dispatcher_liveness|reducer_position)\b' <<<"$body"; then
    block "BLOCKED — INV-3: only core/reducer.py writes derived tables (spec §2; CON-1).
Status has no field to overwrite. That is the trust model — if any other module can
write derived state, the confidence map becomes assertable again, which is exactly the
prototype failure this project exists to remove.
Do instead: append an event through core/store.append and let the reducer compute it."
  fi
;; esac

exit 0
