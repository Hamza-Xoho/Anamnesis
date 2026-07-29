#!/usr/bin/env bash
# sweep-boundaries.sh — PostToolUse on Write|Edit|MultiEdit
#
# Detective backstop for the same invariants. Reads the file FROM DISK, so it
# sees whole-file state including violations that pre-dated this edit — the case
# the PreToolUse hook structurally cannot catch through Edit, and the reason
# MultiEdit's undocumented tool_input shape does not matter here.
#
# Uses the top-level {"decision","reason"} form on exit 0. That form is current
# for PostToolUse, not deprecated. Exit codes and JSON are never mixed.
set -euo pipefail
command -v python3 >/dev/null || { echo "HOOK ERROR: python3 not found; cannot sweep Anamnesis invariants." >&2; exit 2; }
trap 'echo "HOOK ERROR: boundary sweep did not complete; blocking rather than passing." >&2; exit 2' ERR

payload=$(cat)
path=$(printf '%s' "$payload" | python3 -c '
import json, sys
d = json.load(sys.stdin)
sys.stdout.write(str((d.get("tool_input") or {}).get("file_path") or ""))
')

[ -z "$path" ] && exit 0
[ -f "$path" ] || exit 0
case "$path" in *.py) ;; *) exit 0 ;; esac
case "$path" in */tests/*|tests/*) exit 0 ;; esac

report() {
  P="$path" M="$1" python3 -c '
import json, os, sys
sys.stdout.write(json.dumps({
  "decision": "block",
  "reason": "Anamnesis invariant violated in {}:\n{}".format(os.environ["P"], os.environ["M"])
}))
'
  exit 0
}

case "$path" in */core/*|core/*)
  if grep -qE '^[[:space:]]*(from|import)[[:space:]]+.*\b(anthropic|openai|httpx|requests|aiohttp|urllib)\b' "$path"; then
    report "INV-1 — core/ contains a model or network import. core/ is the pure replayable layer (spec §2). Move the call to agents/examiner/ or server/ and consume its event here."
  fi
;; esac

case "$path" in */agents/examiner/*|agents/examiner/*)
  if grep -qE '^[[:space:]]*(from|import)[[:space:]]+.*\b(server|dispatcher|cli|channels)\b' "$path"; then
    report "INV-2 — the examiner imports a conversation-carrying module (CON-3). Only the five FR-4 inputs cross this boundary."
  fi
;; esac

case "$path" in */memory/*|memory/*)
  if grep -qE 'route_quality|route_failure|route_marker' "$path"; then
    report "INV-5 — memory/ references route quality (CON-12). Rate from verdict alone; a route failure emits a candidate in core/reducer.py."
  fi
;; esac

case "$path" in */core/store.py|core/store.py) ;; *)
  if grep -qE '(UPDATE[[:space:]]+events|DELETE[[:space:]]+FROM[[:space:]]+events)' "$path"; then
    report "INV-7 — the event log is append-only (spec §3.1). Append a superseding event; there is no edit path."
  fi
;; esac

case "$path" in */core/reducer.py|core/reducer.py) ;; *)
  if grep -qE '(INSERT[[:space:]]+INTO|UPDATE|DELETE[[:space:]]+FROM)[[:space:]]+.?(probe_state|concept_rollup|error_trail|calibration|candidate_rank|topic_evidence|dispatcher_liveness|reducer_position)\b' "$path"; then
    report "INV-3 — a module other than core/reducer.py writes derived state (CON-1). Append an event and let the reducer compute it."
  fi
;; esac

exit 0
