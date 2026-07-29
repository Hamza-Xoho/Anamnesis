#!/usr/bin/env bash
# inject-invariants.sh — SessionStart
#
# Compaction summarises long sessions, and project rules are among the first
# things to go. CLAUDE.md's compact instructions are a practitioner heuristic;
# this is deterministic. No dependency that can go missing, and it never blocks
# a session from starting.
#
# Keep it to the invariants. A long injection is a per-session context tax —
# the same mistake as a bloated CLAUDE.md, one level down.
set -uo pipefail

cat <<'JSON'
{
  "hookSpecificOutput": {
    "additionalContext": "ANAMNESIS INVARIANTS — hook-enforced. If a hook blocks you, the code is wrong; do not work around it.\n- INV-1  core/ makes no model or network calls. It is the pure replayable layer.\n- INV-2  agents/examiner/ never imports server/, dispatcher/, cli/ or channels/. Only the five FR-4 inputs cross that boundary.\n- INV-3  Only core/reducer.py writes derived tables. Status has no field to overwrite.\n- INV-4  The Obsidian vault is an export target and is never read back as state.\n- INV-5  memory/ never references route quality. Rating derives from verdict alone.\n- INV-6  tests/contract/ is frozen. New files may be created; existing ones may not be modified or deleted.\n- INV-7  The event log is append-only. Supersede by appending, never by editing.\nA refusal is a successful result carrying refused/reason_code/remedy, never a protocol error.\nSpec: spec/design-spec.md. Contract: tests/test-contract.md. Current brief: prompts/."
  }
}
JSON
